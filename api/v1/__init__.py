from flask import Blueprint, jsonify, request, abort
import sqlalchemy

from api.liquidity import get_cached_liquidity, get_pair_key
from api.utils import parse_int
from api.db import db_session

v1 = Blueprint("v1", __name__)


MAX_BLOCK_AMOUNT = 50


@v1.route("/readiness", methods=["GET"])
def readiness():
    return "API is ready!"


@v1.route("/transactions", methods=["GET"])
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
        query = "SELECT * FROM tx_signatures WHERE slot >= :start AND slot <= :end"
        result = db_session.execute(
            sqlalchemy.text(query), {"start": start_block_number, "end": end_block_number}
        )
        keys = result.keys()
        data = list(
            map(
                lambda arr: dict(zip(keys, arr)),
                result,
            )
        )
        return jsonify(data)

    except ValueError as e:
        print("Failed:", e)
        abort(
            500,
            description="failed getting data",
        )

@v1.route("/parsed-transactions", methods=["GET"])
def get_lender_parsed_transactions():
    default_limit = 10
    max_limit = 100
    protocols = ["marginfi", "mango", "kamino"]
    default_protocol = "marginfi"

    limit = parse_int(request.args.get("limit"))
    protocol = request.args.get("protocol")

    if protocol is None:
        protocol = default_protocol

    if protocol not in protocols:
        abort(
            400,
            description=f"Bad protocol. Allowed protocols are {protocols}",
        )

    if limit is None:
        limit = default_limit

    if limit > max_limit:
        abort(
            400,
            description=f"Bad limit. Maximum limit is {max_limit}",
        )

    try:
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
        result = db_session.execute(sqlalchemy.text(query))
        keys = result.keys()
        data = list(
            map(
                lambda arr: dict(zip(keys, arr)),
                result,
            )
        )
        return data

    except ValueError as e:
        print("Failed:", e)
        abort(
            500,
            description="failed getting data",
        )


@v1.route("/liquidity", methods=["GET"])
def get_liquidity():
    token_x_address = request.args.get("token_x")
    token_y_address = request.args.get("token_y")

    if token_x_address is None:
        abort(
            400,
            description="Missing token_x",
        )

    if token_y_address is None:
        abort(
            400,
            description="Missing token_y",
        )

    key = get_pair_key(token_x_address, token_y_address)

    result = get_cached_liquidity().get(key)

    if result is None:
        abort(
            400,
            description=f"No data for the pair {token_x_address}, {token_y_address}",
        )

    return result
