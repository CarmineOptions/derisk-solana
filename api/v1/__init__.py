from flask import Blueprint, jsonify, request, abort
from flasgger import swag_from
import sqlalchemy

from api.utils import to_dict
from api.extensions import db

from db import (
    CallToActions,
    DexNormalizedLiquidity,
    KaminoHealthRatioEA,
    KaminoLoanStatesEA,
    KaminoParsedTransactionsV2,
    MangoHealthRatioEA,
    MangoLoanStatesEA,
    MangoParsedEvents,
    MarginfiHealthRatioEA,
    MarginfiLoanStatesEA,
    MarginfiParsedTransactionsV2,
    SolendHealthRatioEA,
    SolendLoanStatesEA,
    SolendParsedTransactions,
    MarginfiLiquidableDebts,
    MangoLiquidableDebts,
    KaminoLiquidableDebts,
    SolendLiquidableDebts,
    TransactionStatusWithSignature,
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
    "marginfi": MarginfiLoanStatesEA,
    "mango": MangoLoanStatesEA,
    "kamino": KaminoLoanStatesEA,
    "solend": SolendLoanStatesEA,
}

protocols_health_ratio_model_map = {
    "mango": MangoHealthRatioEA,
    "solend": SolendHealthRatioEA,
    "marginfi": MarginfiHealthRatioEA,
    "kamino": KaminoHealthRatioEA,
}


@v1.route("/readiness", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'API readiness status',
            'content': {
                'application/json': {
                    'example': "API is ready!"
                }
            }
        }
    }
})
def readiness():
    return "API is ready!"


@v1.route("/transactions", methods=["GET"])
@swag_from({
    'parameters': [
        {
            'name': 'start_time',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'Start time in epoch seconds'
        },
        {
            'name': 'end_time',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'End time in epoch seconds'
        }
    ],
    'responses': {
        200: {
            'description': 'List of transactions',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "source": "source1",
                            "slot": 12345,
                            "block_time": 1617181723,
                            "transaction_data": "data",
                            "collection_stream": "stream1"
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Invalid input',
            'content': {
                'application/json': {
                    'example': {
                        "description": "\"start_time\" and \"end_time\" must be specified and valid integers."
                    }
                }
            }
        }
    }
})
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

    results = TransactionStatusWithSignature.query.filter(
        TransactionStatusWithSignature.block_time >= start_time,
        TransactionStatusWithSignature.block_time <= end_time,
    ).all()

    # Convert results to list of dictionaries
    transactions = []
    for result in results:
        transaction = {
            "id": result.id,
            "source": result.source,
            "slot": result.slot,
            "block_time": result.block_time,
            "transaction_data": result.transaction_data,
            # Serialize the enum type
            "collection_stream": (
                result.collection_stream.value if result.collection_stream else None
            ),
        }
        transactions.append(transaction)

    return jsonify(transactions)


@v1.route("/parsed-transactions", methods=["GET"])
@swag_from({
    'parameters': [
        {
            'name': 'protocol',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Protocol name'
        },
        {
            'name': 'start_time',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'Start time in epoch seconds'
        },
        {
            'name': 'end_time',
            'in': 'query',
            'type': 'integer',
            'required': True,
            'description': 'End time in epoch seconds'
        }
    ],
    'responses': {
        200: {
            'description': 'List of parsed transactions',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "protocol": "marginfi",
                            "created_at": 1617181723,
                            "data": "transaction_data"
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Invalid input or protocol',
            'content': {
                'application/json': {
                    'example': {
                        "description": "Bad protocol. Allowed protocols are ['marginfi', 'mango', 'kamino', 'solend']"
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'parameters': [
        {
            'name': 'token_x',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Token X address'
        },
        {
            'name': 'token_y',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Token Y address'
        }
    ],
    'responses': {
        200: {
            'description': 'Liquidity data',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "timestamp": 1617181723,
                            "token_x_address": "address_x",
                            "token_y_address": "address_y",
                            "asks": [],
                            "bids": []
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Missing token addresses',
            'content': {
                'application/json': {
                    'example': {
                        "description": "Missing token_x"
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'parameters': [
        {
            'name': 'protocol',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Protocol name'
        },
        {
            'name': 'collateral_token',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Collateral token address'
        },
        {
            'name': 'debt_token',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Debt token address'
        }
    ],
    'responses': {
        200: {
            'description': 'List of liquidable debts',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "protocol": "marginfi",
                            "collateral_token": "token_x",
                            "debt_token": "token_y",
                            "amount": 1000
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Missing or invalid input',
            'content': {
                'application/json': {
                    'example': {
                        "description": '"protocol", "collateral_token" and "debt_token" must be specified'
                    }
                }
            }
        }
    }
})
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
@swag_from({
    'responses': {
        200: {
            'description': 'List of call to actions',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "action": "action1",
                            "description": "description1"
                        }
                    ]
                }
            }
        }
    }
})
def get_cta():
    call_to_actions = CallToActions.query.all()
    return jsonify([to_dict(cta) for cta in call_to_actions])


@v1.route("/loan-states", methods=["GET"])
@swag_from({
    'parameters': [
        {
            'name': 'protocol',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Protocol name'
        }
    ],
    'responses': {
        200: {
            'description': 'List of loan states',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "protocol": "marginfi",
                            "state": "state1",
                            "details": "details1"
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Missing or invalid protocol',
            'content': {
                'application/json': {
                    'example': {
                        "description": '"protocol" query parameter must be specified.'
                    }
                }
            }
        }
    }
})
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

    loan_states = model.query.all()

    # Serialize the query results
    data = [to_dict(loan_state) for loan_state in loan_states]

    return jsonify(data)


@v1.route("/health-ratios", methods=["GET"])
@swag_from({
    'parameters': [
        {
            'name': 'protocol',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Protocol name'
        }
    ],
    'responses': {
        200: {
            'description': 'List of health ratios',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "protocol": "mango",
                            "ratio": 1.5
                        }
                    ]
                }
            }
        },
        400: {
            'description': 'Missing or invalid protocol',
            'content': {
                'application/json': {
                    'example': '"protocol" query parameter must be specified.'
                }
            }
        }
    }
})
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

    health_ratios = model.query.all()

    # Serialize the query results
    data = [to_dict(loan_state) for loan_state in health_ratios]

    return jsonify(data)
