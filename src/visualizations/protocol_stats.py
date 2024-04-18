from decimal import Decimal

import pandas as pd
import sqlalchemy

import src.protocols.state
import src.protocols.addresses
import db

# TODO: Add type hints

def get_unique_token_supply_mints() -> list[str] | None:
    with db.get_db_session() as sesh:
        addresses = (
            sesh.query(db.TokenLendingSupplies.underlying_mint_address).distinct().all()
        )

    if not addresses:
        return None

    return [i[0] for i in addresses]


def get_lending_tokens_with_tvl(prices, tokens) -> list[tuple[str, Decimal]]:

    with db.get_db_session() as session:
        latest_timestamps = (
            session.query(
                db.TokenLendingSupplies.market,
                db.TokenLendingSupplies.underlying_mint_address,
                sqlalchemy.func.max(db.TokenLendingSupplies.timestamp).label(
                    "max_timestamp"
                ),
            )
            .group_by(
                db.TokenLendingSupplies.market,
                db.TokenLendingSupplies.underlying_mint_address,
            )
            .subquery()
        )

        latest_entries_query = (
            session.query(
                latest_timestamps.c.underlying_mint_address,
                sqlalchemy.func.sum(db.TokenLendingSupplies.deposits_total).label(
                    "total_deposits"
                ),
            )
            .join(
                db.TokenLendingSupplies,
                sqlalchemy.and_(
                    latest_timestamps.c.market == db.TokenLendingSupplies.market,
                    latest_timestamps.c.underlying_mint_address
                    == db.TokenLendingSupplies.underlying_mint_address,
                    latest_timestamps.c.max_timestamp
                    == db.TokenLendingSupplies.timestamp,
                ),
            )
            .group_by(latest_timestamps.c.underlying_mint_address)
        )

        results = latest_entries_query.all()

    results_with_info = []

    for res in results:
        info = tokens.get(res[0])

        if not info:
            # TODO: log (res)
            continue

        res_with_info = {
            "address": res[0],
            "amount": res[1] / 10 ** info["decimals"],
        }

        results_with_info.append(res_with_info)

    for entry in results_with_info:
        price = prices.get(entry["address"])

        entry["price"] = Decimal(str(price)) if price else None

        if not price:
            print(f'cant find price for addr: {entry["address"]}')
            continue

    tvls = []

    for res in results_with_info:
        if not res["price"]:
            # TODO: LOG
            continue

        tvls.append((res["address"], res["price"] * res["amount"]))

    return sorted(tvls, key=lambda x: x[1], reverse=True)


def get_latest_lending_suplies_for_mints(mints: list[str]) -> pd.DataFrame:

    with db.get_db_session() as session:
        latest_timestamps = (
            session.query(
                db.TokenLendingSupplies.underlying_mint_address,
                sqlalchemy.func.max(db.TokenLendingSupplies.timestamp).label(
                    "max_timestamp"
                ),
            )
            .filter(db.TokenLendingSupplies.underlying_mint_address.in_(mints))
            .group_by(db.TokenLendingSupplies.underlying_mint_address)
            .subquery()
        )

        latest_entries_query = session.query(db.TokenLendingSupplies).join(
            latest_timestamps,
            sqlalchemy.and_(
                db.TokenLendingSupplies.underlying_mint_address
                == latest_timestamps.c.underlying_mint_address,
                db.TokenLendingSupplies.timestamp == latest_timestamps.c.max_timestamp,
            ),
        )

        df = pd.read_sql(latest_entries_query.statement, session.bind)

    return df


def prepare_latest_lending_supplies_df(df, prices, tokens) -> pd.DataFrame:
    addresses = {
        value: key for key, value in src.protocols.addresses.ALL_ADDRESSES.items()
    }

    df["symbol"] = [tokens[i]["symbol"] for i in df["underlying_mint_address"]]
    df["decimals"] = [tokens[i]["decimals"] for i in df["underlying_mint_address"]]
    df["lent_total"] = df["lent_total"] / 10 ** df["decimals"]
    df["deposits_total"] = df["deposits_total"] / 10 ** df["decimals"]
    df["available_to_borrow"] = df["available_to_borrow"] / 10 ** df["decimals"]
    df["protocol"] = [addresses[i] for i in df["protocol_id"]]
    df["price"] = [prices[i] for i in df["underlying_mint_address"]]

    df["Borrowed"] = df["lent_total"] * df["price"]
    df["Deposits"] = df["deposits_total"] * df["price"]
    df["Available"] = df["available_to_borrow"] * df["price"]

    return df


def get_lending_supplies_df(prices, tokens) -> pd.DataFrame:
    mints = get_lending_tokens_with_tvl(prices, tokens)[
        :12
    ]  # We want top 12 tokens by deposits
    df = get_latest_lending_suplies_for_mints([i[0] for i in mints])
    return prepare_latest_lending_supplies_df(df, prices, tokens)


# TODO: To be implemented.
# def get_general_stats(
# 	states: dict[str, src.protocols.state.State],
# 	individual_loan_stats: pandas.DataFrame,
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def get_supply_stats(
# 	states: dict[str, src.protocols.state.State],
# 	prices: dict[str, decimal.Decimal],
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def get_collateral_stats(
# 	states: dict[str, src.protocols.state.State],
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def get_debt_stats(
# 	states: dict[str, src.protocols.state.State],
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def get_utilization_stats(
# 	general_stats: pandas.DataFrame,
# 	supply_stats: pandas.DataFrame,
# 	debt_stats: pandas.DataFrame,
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def load_general_stats() -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def load_supply_stats() -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def load_collateral_stats() -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def load_debt_stats() -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def load_utilization_stats() -> pandas.DataFrame:
# 	return pandas.DataFrame()


# # TODO: To be implemented.
# def get_collateral_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
# 	return plotly.express.pie()


# # TODO: To be implemented.
# def get_debt_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
# 	return plotly.express.pie()


# # TODO: To be implemented.
# def get_supply_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
# 	return plotly.express.pie()
