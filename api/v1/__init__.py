from flask import Blueprint, jsonify, request, abort
import sqlalchemy
from sqlalchemy.orm import load_only

from api.utils import to_dict
from api.extensions import db

from db import (
    CallToActions,
    DexNormalizedLiquidity,
    KaminoParsedTransactions,
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    SolendParsedTransactions,
    MarginfiLiquidableDebts,
    MangoLiquidableDebts,
    KaminoLiquidableDebts,
    SolendLiquidableDebts,
    TransactionStatusWithSignature,
)

v1 = Blueprint("v1", __name__)


MAX_BLOCK_AMOUNT = 50


protocols_parsed_transactions_model_map = {
    "marginfi": MarginfiParsedTransactions,
    "mango": MangoParsedTransactions,
    "kamino": KaminoParsedTransactions,
    "solend": SolendParsedTransactions,
}

protocols_liquidable_debt_model_map = {
    "marginfi": MarginfiLiquidableDebts,
    "mango": MangoLiquidableDebts,
    "kamino": KaminoLiquidableDebts,
    "solend": SolendLiquidableDebts,
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

    try:
        result = (
            db.session.query(DexNormalizedLiquidity)
            .filter(
                DexNormalizedLiquidity.timestamp
                == db.session.query(
                    sqlalchemy.func.max(DexNormalizedLiquidity.timestamp)
                ),
                DexNormalizedLiquidity.token_x_address == token_x_address,
                DexNormalizedLiquidity.token_y_address == token_y_address,
            )
            .all()
        )

        if result is None:
            empty_response = [{"asks": [], "bids": []}]
            return jsonify(empty_response)

        data = [to_dict(row) for row in result]

        return jsonify(data)
    except ValueError:
        abort(
            500,
            description="failed getting data",
        )


@v1.route("/liquidable-debt", methods=["GET"])
def get_liquidable_debt():
    protocol = request.args.get("protocol")
    collateral_token = request.args.get("collateral_token")
    debt_token = request.args.get("debt_token")

    if not (protocol and collateral_token and debt_token):
        abort(
            400,
            description='"protocol", "collateral_token" and "debt_token" must be specified',
        )

    model = protocols_liquidable_debt_model_map.get(protocol)

    if model is None:
        abort(400, description=f"{protocol} is not a valid protocol")

    try:
        result = (
            db.session.query(model)
            .filter(
                model.collateral_token == collateral_token,
                model.debt_token == debt_token,
            )
            .all()
        )

        data = [to_dict(row) for row in result]

        return jsonify(data)

    except ValueError:
        abort(500, description="Failed getting data")


@v1.route("/cta", methods=["GET"])
def get_cta():
    call_to_actions = CallToActions.query.all()
    return jsonify([to_dict(cta) for cta in call_to_actions])
