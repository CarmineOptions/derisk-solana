import pandas as pd
import plotly.express
import plotly.graph_objs

import db


def protocol_to_model(
    protocol: str,
) -> (
    db.MarginfiLiquidableDebts
    | db.MangoLiquidableDebts
    | db.KaminoLiquidableDebts
    | db.SolendLiquidableDebts
):
    if protocol == "marginfi":
        return db.MarginfiLiquidableDebts
    if protocol == "mango":
        return db.MangoLiquidableDebts
    if protocol == "kamino":
        return db.KaminoLiquidableDebts
    if protocol == "solend":
        return db.SolendLiquidableDebts
    raise ValueError(f"invalid protocol {protocol}")


def get_aggregated_liquidable_debt_data(protocol: str) -> pd.DataFrame:

    db_model = protocol_to_model(protocol)

    with db.get_db_session() as session:
        data = session.query(db_model).all()

        print(data, flush=True)

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
        x="collateral_token",
        y="amount",
        color="debt_token",  # Different bars for each debt_token
        barmode="group",  # Group bars for each collateral_token
        facet_col="collateral_token_price",  # Create a subplot for each price point
        title="Sum of Amounts by Collateral and Debt Tokens at Various Prices",
        labels={
            "amount": "Total Amount",
            "collateral_token": "Collateral Token",
            "debt_token": "Debt Token",
        },
    )

    return figure
