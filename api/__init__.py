from flask import Flask
from .v1 import v1


app = Flask(__name__)
app.register_blueprint(v1, url_prefix="/v1")
