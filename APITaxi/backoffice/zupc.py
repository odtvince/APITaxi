# -*- coding: utf-8 -*-
from ..extensions import db, index_zupc
from ..models import administrative as administrative_models
from ..forms.administrative import ZUPCreateForm, ZUPCUpdateForm
from ..utils import request_wants_json
from flask.ext.security import login_required, roles_accepted, current_user
from flask.ext.restplus import reqparse, marshal
from flask import (Blueprint, request, render_template, redirect, jsonify,
                   url_for)
from werkzeug.exceptions import BadRequest
import json


mod = Blueprint('zupc', __name__)

def zupc_list():
    page = int(request.args.get('page')) if 'page' in request.args else 1
    return render_template('lists/zupc.html',
        zupc_list=administrative_models.ZUPC.query.paginate(page))


def zupc_search():
    parser = reqparse.RequestParser()
    parser.add_argument('lon', type=float, required=True, location='args')
    parser.add_argument('lat', type=float, required=True, location='args')
    try:
        args = parser.parse_args()
    except BadRequest as e:
        return json.dumps(e.data), 400

    id_list = index_zupc.intersection(args['lon'], args['lat'])
    to_return = []
    if id_list:
        ZUPC = administrative_models.ZUPC
        zupc_list = ZUPC.query.filter(ZUPC.id.in_(id_list)).all()
#Level is one, because we don't want to have parent in the response
        to_return = marshal(zupc_list, ZUPC.marshall_obj(filter_id=True, level=1))
    return json.dumps({"data": to_return})




@mod.route('/zupc')
@mod.route('/zupc/')
def zupc():
    if request.method == "GET":
        if request_wants_json():
            return zupc_search()
        roles_accepted = set(['admin', 'mairie', 'prefecture', 'operateur'])
        if not current_user.is_anonymous() and\
                len(roles_accepted.intersection(current_user.roles)) > 0:
            return zupc_list()
    abort(405, message="method now allowed")


@mod.route('/zupc/form', methods=['GET', 'POST'])
@login_required
@roles_accepted('admin', 'mairie', 'prefecture')
def zupc_form():
    form = None
    if request.args.get("id"):
        zupc = administrative_models.ZUPC.query.get(request.args.get("id"))
        if not zupc:
            abort(404, message="Unable to find ZUPC")
        form = ZUPCUpdateForm(obj=zupc)
    else:
        form = ZUPCreateForm()
    if request.method == "POST":
        if request.args.get("id"):
            form.populate_obj(zupc)
            if form.validate():
                db.session.commit()
                return redirect(url_for('zupc.zupc'))
        else:
            if form.validate():
                zupc = administrative_models.ZUPC()
                form.populate_obj(zupc)
                db.session.add(zupc)
                db.session.commit()
                return redirect(url_for('zupc.zupc'))
    return render_template('forms/ads.html', form=form,
        form_method="POST", submit_value="Modifier")


@mod.route('/zupc/delete')
@login_required
@roles_accepted('admin', 'mairie', 'prefecture')
def zupc_delete():
    if not request.args.get("id"):
        abort(404, message="id is required")
    zupc = administrative_models.ZUPC.query.get(request.args.get("id"))
    if not zupc:
        abort(404, message="Unable to find the ZUPC")
    db.session.delete(zupc)
    db.session.commit()
    return redirect(url_for("zupc.zupc"))


@mod.route('/zupc/autocomplete')
def zupc_autocomplete():
    #@TODO: have some identification here?
    term = request.args.get('q')
    like = "%{}%".format(term)

    response = administrative_models.ZUPC.query.filter(
            administrative_models.ZUPC.nom.ilike(like)).all()
    return jsonify(suggestions=map(lambda zupc:{'name': zupc.nom, 'id': int(zupc.id)},
                                        response))

