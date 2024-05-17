from flask import Blueprint, jsonify, request, abort
import sqlalchemy
from sqlalchemy.orm import load_only

from api.utils import to_dict
from api.extensions import db, db2

from db import (
    CallToActions,
    DexNormalizedLiquidity,
    KaminoHealthRatio,
    KaminoLoanStates,
    KaminoParsedTransactionsV2,
    MangoHealthRatio,
    MangoLoanStates,
    MangoParsedEvents,
    MarginfiHealthRatio,
    MarginfiLoanStates,
    MarginfiParsedTransactionsV2,
    SolendHealthRatio,
    SolendLoanStates,
    SolendParsedTransactions,
    MarginfiLiquidableDebts,
    MangoLiquidableDebts,
    KaminoLiquidableDebts,
    SolendLiquidableDebts,
    TransactionsForAPI,
    CollectionStreamTypes
)

v1 = Blueprint("v1", __name__)


MAX_SECONDS = 60
MAX_SECONDS_EVENTS = 300

protocols_parsed_transactions_model_map = {
    "marginfi": MarginfiParsedTransactionsV2,
    "mango": MangoParsedEvents,
    "kamino": KaminoParsedTransactionsV2,
    "solend": SolendParsedTransactions,
}

protocols_liquidable_debt_model_map = {
    "marginfi": MarginfiLiquidableDebts,
    "mango": MangoLiquidableDebts,
    "kamino": KaminoLiquidableDebts,
    "solend": SolendLiquidableDebts,
}

protocols_loan_states_model_map = {
    "marginfi": MarginfiLoanStates,
    "mango": MangoLoanStates,
    "kamino": KaminoLoanStates,
    "solend": SolendLoanStates,
}

protocols_health_ratio_model_map = {
    "mango": MangoHealthRatio,
    "solend": SolendHealthRatio,
    "marginfi": MarginfiHealthRatio,
    "kamino": KaminoHealthRatio,
}


@v1.route("/readiness", methods=["GET"])
def readiness():
    return "API is ready!"


@v1.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        start_time = int(request.args.get("start_time"))
        end_time = int(request.args.get("end_time"))
    except TypeError:
        abort(
            400,
            description='"start_time" and "end_time" must be specified and valid integers.',
        )

    if start_time is None or end_time is None:
        abort(
            400,
            description='"start_time" and "end_time" must be specified',
        )

    if start_time > end_time:
        abort(
            400,
            description='"end_time" must be greater than "start_time"',
        )

    if end_time - start_time > MAX_SECONDS:
        abort(400, description="cannot fetch interval longer then 60 seconds")

    transactions = db2.TransactionsForAPI.query(
        db2.TransactionsForAPI.signature,
        db2.TransactionsForAPI.slot,
        db2.TransactionsForAPI.transaction_data,
        db2.TransactionsForAPI.source,
        db2.TransactionsForAPI.block_time
    ).filter(
        db2.TransactionsForAPI.block_time >= start_time,
        db2.TransactionsForAPI.block_time <= end_time,
    ).all()

    # Serialize the query results
    results = [to_dict(transaction) for transaction in transactions]

    return jsonify(results)


@v1.route("/parsed-transactions", methods=["GET"])
def get_lender_parsed_transactions():
    default_limit = 10
    max_limit = 100

    try:
        protocol = request.args.get("protocol", "")
        if protocol not in protocols_parsed_transactions_model_map:
            abort(
                400,
                description=f"Bad protocol. Allowed protocols are {list(protocols_parsed_transactions_model_map.keys())}",
            )

        try:
            start_time = int(request.args.get("start_time"))
            end_time = int(request.args.get("end_time"))
        except TypeError:
            abort(
                400,
                description='"start_time" and "end_time" must be specified and valid integers.',
            )

        if start_time is None or end_time is None:
            abort(
                400,
                description='"start_time" and "end_time" must be specified',
            )

        if start_time > end_time:
            abort(
                400,
                description='"end_time" must be greater than "start_time"',
            )

        if end_time - start_time > MAX_SECONDS_EVENTS:
            abort(400, description="cannot fetch interval longer then 300 seconds")

        model = protocols_parsed_transactions_model_map[protocol.lower()]

        transactions = model.query.filter(
            model.created_at >= start_time,
            model.created_at <= end_time,
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

    model = protocols_liquidable_debt_model_map.get(protocol.lower())

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


@v1.route("/loan-states", methods=["GET"])
def get_loan_states():
    protocol = request.args.get("protocol")

    if protocol is None:
        abort(
            400,
            description='"protocol" query parameter must be specified.',
        )

    model = protocols_loan_states_model_map.get(protocol.lower())

    if model is None:
        abort(
            400,
            description=f'"{protocol}" is not a valid protocol.',
        )

    latest_slot_number = model.query.order_by(model.slot.desc()).first().slot
    loan_states = model.query.filter(model.slot == latest_slot_number).all()

    # Serialize the query results
    data = [to_dict(loan_state) for loan_state in loan_states]

    return jsonify(data)


@v1.route("/health-ratios", methods=["GET"])
def get_health_ratios():
    protocol = request.args.get("protocol")

    if protocol is None:
        abort(
            400,
            description='"protocol" query parameter must be specified.',
        )

    model = protocols_health_ratio_model_map.get(protocol.lower())

    if model is None:
        abort(
            400,
            description=f'"{protocol}" is not a valid protocol.',
        )

    latest_slot_number = model.query.order_by(model.slot.desc()).first().slot
    health_ratios = model.query.filter(model.slot == latest_slot_number).all()

    # Serialize the query results
    data = [to_dict(loan_state) for loan_state in health_ratios]

    return jsonify(data)
