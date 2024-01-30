from flask import Flask
from .v1 import v1


application = Flask(__name__)
application.register_blueprint(v1, url_prefix="/v1")
