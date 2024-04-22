from flask import Blueprint, jsonify, request, abort
import sqlalchemy
from sqlalchemy.orm import load_only

from api.liquidity import get_cached_liquidity, get_pair_key
from api.utils import parse_int, to_dict
from api.db import db_session
from api.extensions import db

from db import (
    CallToActions,
    KaminoParsedTransactions,
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    TransactionStatusWithSignature,
)

v1 = Blueprint("v1", __name__)


MAX_BLOCK_AMOUNT = 50


protocols_parsed_transactions_model_map = {
    "marginfi": MarginfiParsedTransactions,
    "mango": MangoParsedTransactions,
    "kamino": KaminoParsedTransactions,
}


@v1.route("/readiness", methods=["GET"])
def readiness():
    return "API is ready!"


@v1.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        start_block_number = int(request.args.get("start_block_number"))
        end_block_number = int(request.args.get("end_block_number"))
    except TypeError:
        abort(
            400,
            description='"start_block_number" and "end_block_number" must be specified and valid integers.',
        )

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
        abort(400, description="cannot fetch more than 50 blocks at a time")

    transactions = (
        TransactionStatusWithSignature.query.options(load_only("id", "slot"))
        .filter(
            TransactionStatusWithSignature.slot >= start_block_number,
            TransactionStatusWithSignature.slot <= end_block_number,
        )
        .all()
    )

    # Serialize the query results
    results = [to_dict(transaction) for transaction in transactions]

    return jsonify(results)


@v1.route("/parsed-transactions", methods=["GET"])
def get_lender_parsed_transactions():
    default_limit = 10
    max_limit = 100

    try:
        limit = int(request.args.get("limit", default_limit))
        if limit > max_limit:
            abort(400, description=f"Bad limit. Maximum limit is {max_limit}")

        protocol = request.args.get("protocol", "marginfi")
        if protocol not in protocols_parsed_transactions_model_map:
            abort(
                400,
                description=f"Bad protocol. Allowed protocols are {list(protocols_parsed_transactions_model_map.keys())}",
            )

        model = protocols_parsed_transactions_model_map[protocol]

        # Example of a more idiomatic query assuming some common schema
        max_block = db.session.query(sqlalchemy.func.max(model.block)).scalar()
        transactions = model.query.filter(
            model.block.between(max_block - limit, max_block)
        ).all()

        return jsonify([to_dict(transaction) for transaction in transactions])

    except ValueError:
        abort(500, description="Server error: failed to process data")


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


@v1.route("/liquidable-debt", methods=["GET"])
def get_liquidable_debt():
    protocol = request.args.get("protocol")
    collateral_token = request.args.get("collateral_token")
    debt_token = request.args.get("protocol")

    if protocol is None or collateral_token is None or debt_token is None:
        abort(
            400,
            description='"protocol", "collateral_token" and "debt_token" query parameters must be specified',
        )

    try:
        protocol_table = f"lenders.{protocol}_liquidable_debts"
        query = f"""
        SELECT *
        FROM {protocol_table}
        WHERE collateral_token = {collateral_token} AND debt_token = {debt_token};
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


@v1.route("/cta", methods=["GET"])
def get_cta():
    call_to_actions = CallToActions.query.all()
    return [
        {
            "timestamp": cta.timestamp,
            "collateral_token": cta.collateral_token,
            "debt_token": cta.debt_token,
            "message": cta.message,
        }
        for cta in call_to_actions
    ]
