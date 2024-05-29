import logging
import os

from flask import Flask
from flasgger import Swagger

import google.cloud.logging

from api.extensions import db, cache, compress
from api.utils import get_db_connection_string
from api.v1 import v1


# init app
application = Flask(__name__)

# set endpoints
application.register_blueprint(v1, url_prefix="/v1")
swagger = Swagger(application)

# init cache
cache.init_app(application)

# init db
application.config["SQLALCHEMY_DATABASE_URI"] = get_db_connection_string()
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(application)

# init compression
application.config["COMPRESS_MIMETYPES"] = ["text/html", "application/json"]
application.config["COMPRESS_LEVEL"] = 9
application.config["COMPRESS_MIN_SIZE"] = 500
compress.init_app(application)

# init GCP logging
# set "USE_GCP_LOGGING" to anything to allow GCP logging
if os.environ.get("USE_GCP_LOGGING") is not None:
    client = google.cloud.logging.Client()
    client.setup_logging()
    logging.info("logging into GCP logs")
else:
    logging.info("using default logging")

logging.info("API started")
