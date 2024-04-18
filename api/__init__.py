from flask import Flask
from api.cache import cache

from .v1 import v1

application = Flask(__name__)
cache.init_app(application)
application.register_blueprint(v1, url_prefix="/v1")
