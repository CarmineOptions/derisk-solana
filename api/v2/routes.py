from flask import Blueprint, jsonify

v2 = Blueprint("v2", __name__)


@v2.route("/data")
def data():
    return jsonify({"status": "success", "data": [3, 2, 1], "version": 2})
