DEBUG = True
ENV = 'DEV'
SECRET_KEY = 'super-secret'
SQLALCHEMY_DATABASE_URI = 'postgresql://v:v@localhost/odtaxi'
REDIS_URL = "redis://:@localhost:6379/0"
REDIS_GEOINDEX = 'geoindex'
SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'pepper'
SECURITY_REGISTERABLE = True
UPLOADED_IMAGES_DEST = 'uploads'

UPLOADED_DOCUMENTS_DEST = 'uploads'
UPLOADED_DOCUMENTS_URL = '/documents/<path:filename>'

SLACK_API_KEY = None

DOGPILE_CACHE_URLS = ''
DOGPILE_CACHE_REGIONS = [
    ('taxis', None)
]

DOGPILE_CACHE_BACKEND = 'dogpile.cache.memory'
SQLALCHEMY_POOL_SIZE = 15

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['pickle']

from celery.schedules import crontab
#List of tuples of the form
# (frequency in minute, kwargs) where kwargs in passed to crontab
STORE_TAXIS_FREQUENCIES = [(1, {'minute': '*/1'}),
    (60,{'minute': 0, 'hour': '*/1'}), (24*60, {'minute': 0, 'hour': 0})]
CELERYBEAT_SCHEDULE = dict()
for frequency, cron_kwargs in STORE_TAXIS_FREQUENCIES:
    CELERYBEAT_SCHEDULE['store_active_taxis_every_{}'.format(frequency)] =  {
            'task': 'APITaxi.tasks.store_active_taxis',
            'schedule': crontab(**cron_kwargs),
            'args': [frequency]
    }

INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = ''
INFLUXDB_PASSWORD = ''
INFLUXDB_TAXIS_DB = 'taxis'
NOW = 'now'
