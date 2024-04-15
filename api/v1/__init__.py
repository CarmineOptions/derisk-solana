from flask import Blueprint, jsonify, request, abort
from sqlalchemy.sql import text

from api.utils import parse_int
from db import get_db_session

v1 = Blueprint("v1", __name__)


MAX_BLOCK_AMOUNT = 50


@v1.route("/readiness", methods=["GET"])
def readiness():
    return "api is ready"


@v1.route("/get-transactions", methods=["GET"])
def get_transactions():
    start_block_number = parse_int(request.args.get("start_block_number"))
    end_block_number = parse_int(request.args.get("end_block_number"))

    if start_block_number is None or end_block_number is None:
        abort(
            400,
            description='"start_block_number" and "end_block_number" must be specified',
        )

    if start_block_number > end_block_number:
        abort(
            400,
            description='"end_block_number" must be greater than "start_block_number"',
        )

    if end_block_number - start_block_number > MAX_BLOCK_AMOUNT:
        abort(
            400,
            description="cannot fetch more than 50 blocks at a time",
        )

    try:
        session = get_db_session()
        query = "SELECT * FROM tx_signatures WHERE slot >= :start AND slot <= :end"
        result = session.execute(
            text(query), {"start": start_block_number, "end": end_block_number}
        )
        session.close()
        keys = result.keys()
        data = list(
            map(
                lambda arr: {key: value for key, value in zip(keys, arr)},
                result,
            )
        )
        return jsonify(data)

    except Exception as e:
        print("Failed:", e)
        abort(
            500,
            description="failed getting data",
        )


@v1.route("/get-lender-parsed-transactions", methods=["GET"])
def get_lender_parsed_transactions():
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 100
    PROTOCOLS = ["marginfi", "mango", "kamino"]
    DEFAULT_PROTOCOL = "marginfi"

    limit = parse_int(request.args.get("limit"))
    protocol = request.args.get("protocol")

    if protocol is None:
        protocol = DEFAULT_PROTOCOL

    if protocol not in PROTOCOLS:
        abort(
            400,
            description=f'Bad protocol. Allowed protocols are {PROTOCOLS}',
        )

    if limit is None:
        limit = DEFAULT_LIMIT

    if limit > MAX_LIMIT:
        abort(
            400,
            description=f'Bad limit. Maximum limit is {MAX_LIMIT}',
        )

    try:
        session = get_db_session()
        protocol_table = f"lenders.{protocol}_parsed_transactions"
        query = f"""
        WITH MaxValue AS (
            SELECT MAX(block) AS max_block
            FROM {protocol_table}
        )
        SELECT *
        FROM {protocol_table}, MaxValue
        WHERE block BETWEEN max_block - {limit} AND max_block;
        """
        result = session.execute(text(query))
        session.close()
        keys = result.keys()
        data = list(
            map(
                lambda arr: {key: value for key, value in zip(keys, arr)},
                result,
            )
        )
        return data

    except Exception as e:
        print("Failed:", e)
        abort(
            500,
            description="failed getting data",
        )

