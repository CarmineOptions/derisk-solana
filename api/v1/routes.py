from flask import Blueprint, jsonify

v1 = Blueprint("v1", __name__)


@v1.route("/data")
def data():
    return jsonify({"status": "success", "data": [1, 2, 3], "version": 1})
