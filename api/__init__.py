import logging

from flask import Flask
import google.cloud.logging

from api.extensions import db, cache, compress
from api.utils import get_db_connection_string
from api.v1 import v1


# init app
app = Flask(__name__)

# init cache
cache.init_app(app)

# init db
app.config["SQLALCHEMY_DATABASE_URI"] = get_db_connection_string()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# init compression
app.config["COMPRESS_MIMETYPES"] = ["text/html", "application/json"]
app.config["COMPRESS_LEVEL"] = 9
app.config["COMPRESS_MIN_SIZE"] = 500
compress.init_app(app)

# init GCP logging
client = google.cloud.logging.Client()
client.setup_logging()

# set endpoints
app.register_blueprint(v1, url_prefix="/v1")

logging.info("API started")
