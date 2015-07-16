# -*- coding: utf-8 -*-
from operator import itemgetter
from rtree import index
from sqlalchemy import distinct
from . import db
from functools import wraps
from werkzeug.wrappers import Response

class IndexZUPC(object):
    def __init__(self):
        self.index_zupc = None
        self.size = 0

    def __init_zupc(self):
        self.index_zupc = index.Index()
        self.size = 0
        from .models.taxis import ADS
        from .models.administrative import ZUPC
        insee_list = map(itemgetter(0),
                db.session.query(distinct(ADS.zupc_id)).all())
        if len(insee_list) == 0:
            return
        for zupc in ZUPC.query.filter(ZUPC.id.in_(insee_list)).all():
            if zupc.shape is None:
                continue
            self.index_zupc.insert(zupc.id,
                    (zupc.left, zupc.bottom, zupc.right, zupc.top))
            self.size += 1

    def intersection(self, lon, lat):
        if self.index_zupc is None:
            self.__init_zupc()
        return self.index_zupc.intersection((lon, lat, lon, lat))

    def reinit(self):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                resp = f(*args, **kwargs)
                t = type(resp)
                if t is tuple:
                    resp, status_code = resp
                    if status_code == 201 or status_code == 302:
                        self.__init_zupc()
                    return resp, status_code
                elif t is Response:
                    if resp.status_code == 302:
                        self.__init_zupc()
                return resp
            return wrapper
        return decorator
