from flask import Flask

from api.cache import cache
from api.db import CONN_STRING
from api.v1 import v1
from api.extensions import db


# init app
app = Flask(__name__)

# init cache
cache.init_app(app)

# set endpoints
app.register_blueprint(v1, url_prefix="/v1")

# configure db access
app.config["SQLALCHEMY_DATABASE_URI"] = CONN_STRING
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
