import os
from flask import Flask
from v1.routes import v1
from v2.routes import v2

PORT = os.environ["PORT"]

if __name__ == "__main__":
    app = Flask(__name__)
    app.register_blueprint(v1, url_prefix="/v1")
    app.register_blueprint(v2, url_prefix="/v2")
    app.run(debug=True, port=PORT, host="0.0.0.0")
