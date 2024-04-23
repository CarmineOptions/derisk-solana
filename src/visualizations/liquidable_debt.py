import pandas as pd
import plotly.express
import plotly.graph_objs

import db
from . import main_chart


def protocol_to_model(
    protocol: str,
) -> (
    db.MarginfiLiquidableDebts
    | db.MangoLiquidableDebts
    | db.KaminoLiquidableDebts
    | db.SolendLiquidableDebts
):
    protocol = protocol.lower()
    if protocol == "marginfi":
        return db.MarginfiLiquidableDebts
    if protocol == "mango":
        return db.MangoLiquidableDebts
    if protocol == "kamino":
        return db.KaminoLiquidableDebts
    if protocol == "solend":
        return db.SolendLiquidableDebts
    raise ValueError(f"invalid protocol {protocol}")


def get_aggregated_liquidable_debt_data(
    protocols: list[str], selected_tokens: main_chart.TokensSelected
) -> pd.DataFrame:
    # db models of all selected protocols
    db_models = [protocol_to_model(protocol) for protocol in protocols]

    with db.get_db_session() as session:
        data = []
        for db_model in db_models:
            try:
                # data over all protocols
                data += (
                    session.query(db_model)
                    .filter(
                        db_model.collateral_token == selected_tokens.collateral.address
                    )
                    .filter(db_model.debt_token == selected_tokens.loan.address)
                    .all()
                )
            except ValueError:
                print(f"no data for {db_model}")

        df = pd.DataFrame(
            [
                {
                    "collateral_token": d.collateral_token,
                    "debt_token": d.debt_token,
                    "collateral_token_price": d.collateral_token_price,
                    "amount": d.amount,
                }
                for d in data
            ]
        )

        aggregated_data = (
            df.groupby(["collateral_token", "debt_token", "collateral_token_price"])
            .agg({"amount": "sum"})
            .reset_index()
        )

    return aggregated_data


def get_figure(
    data: pd.DataFrame,
) -> plotly.graph_objs.Figure:
    figure = plotly.express.bar(
        data,
        x="collateral_token_price",
        y="amount",
        color="debt_token",  # Different bars for each debt_token
        barmode="group",  # Group bars for each collateral_token
        # facet_col="collateral_token_price",  # Create a subplot for each price point
        title="Sum of Amounts by Collateral and Debt Tokens at Various Prices",
        labels={
            "amount": "Total Amount",
            "collateral_token": "Collateral Token",
        },
    )

    return figure
