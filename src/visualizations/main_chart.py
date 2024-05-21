from dataclasses import dataclass
import datetime
# import math
from typing import Iterator
# import decimal
import time

# import json
# import operator

# import time

from sqlalchemy.orm.session import Session
import streamlit as st
import sqlalchemy
import pandas as pd
import plotly.express
import plotly.graph_objs

import db

from src.prices import PricesType

# import src.protocols.dexes.amms
# import src.database
# import src.protocols.state


# LOOKBACK_DAYS: int = 5
# MAXIMUM_PERCENTAGE_PRICE_CHANGE = 0.05

# PAIRS_PAIRS_MAPPING: dict[str, tuple[str, ...]] = {
# 	"ETH-USDC": ("WETH/USDC", "ETHpo/USDC"),
# 	"SOL-USDC": ("SOL/USDC", ""),
# 	"SOL-USDT": ("SOL/USDT", ""),
# 	"JUP-USDC": ("JUP/USDC", ""),
# 	"JUP-USDT": ("JUP/USDT", ""),
# }

# def get_token(pair: str, split_character: str, base: bool) -> str:
# 	token = pair.split(split_character)[0] if base else pair.split(split_character)[1]
# 	# TODO: Create a proper mapping.
# 	return 'ETH' if 'ETH' in token else token


@dataclass
class Token:
    address: str
    symbol: str
    name: str
    decimals: int

    def __repr__(self):
        return self.symbol

    def __hash__(self):
        return hash(self.address)


@dataclass
class TokensSelected:
    collateral: Token
    loan: Token


def token_symbols_to_Token_list( # pylint: disable=C0103
    symbols: list[str], tokens_symbols_to_info_map: dict[str, dict[str, str | int]]
) -> list[Token]:

    tokens = []

    for symbol in symbols:
        info = tokens_symbols_to_info_map.get(symbol)
        if not info:
            print("Unable to find token info for:", symbol)
            continue

        tokens.append(
            Token(
                address=str(info["address"]),
                symbol=symbol,
                name=str(info["name"]),
                decimals=int(info["decimals"]),
            )
        )

    return tokens


def token_addresses_to_Token_list( # pylint: disable=C0103
    addresses: list[str], tokens_address_to_info_map: dict[str, dict[str, str | int]]
) -> list[Token]:

    tokens = []

    for address in addresses:
        info = tokens_address_to_info_map.get(address)
        if not info:
            print("Unable to find token info for:", address)
            continue

        tokens.append(
            Token(
                address=address,
                symbol=str(info['symbol']),
                name=str(info["name"]),
                decimals=int(info["decimals"]),
            )
        )

    return tokens

AnyLiquidableDebtModel = (
    db.MarginfiLiquidableDebts
    | db.MangoLiquidableDebts
    | db.KaminoLiquidableDebts
    | db.SolendLiquidableDebts
)

def protocol_to_model(
    protocol: str,
) -> AnyLiquidableDebtModel:
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


@st.cache_data(ttl=datetime.timedelta(minutes=60), show_spinner = 'Loading liquidable debt.')
def get_liquidable_debt_single_protocol(
    _session: Session,
    protocol: str, 
    collateral_token_address: str, 
    debt_token_address: str
) -> pd.DataFrame | None:

    model = protocol_to_model(protocol)

    try:
        # data over all protocols
        latest_slot_subquery = (
            _session.query(model.slot)
            .filter(model.collateral_token == collateral_token_address)
            .filter(model.debt_token == debt_token_address)
            .order_by(model.slot.desc())
            .limit(1)
        ).subquery()

        # data over all protocols
        data = (
            _session.query(model)
            .filter(model.collateral_token == collateral_token_address)
            .filter(model.debt_token == debt_token_address)
            .filter(model.slot == latest_slot_subquery.c.slot)
            .all()
        )
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
        return df

    except ValueError:
        logging.error(f"No data for {_db_model}")
        return None

    


@st.cache_data(ttl=datetime.timedelta(minutes=60))
def get_liquidable_debt(
    protocols: list[str],
    token_pair: TokensSelected,
) -> pd.DataFrame | None:

    with db.get_db_session() as session:
        data = []
        for protocol in protocols:
        
            debt = get_liquidable_debt_single_protocol(
                session, 
                protocol,
                token_pair.collateral.address,
                token_pair.loan.address,
            )

            if debt is None: 
                continue

            data.append(debt)

        if not data:
            logging.error(f'No liquidable debt found for protocols: {protocols}, pair: {token_pair}')
            return None

        df = pd.concat(data)

        aggregated_data = (
            df.groupby(["collateral_token", "debt_token", "collateral_token_price"])
            .agg({"amount": "sum"})
            .reset_index()
        )

    return aggregated_data


def get_normalized_liquidity(tokens: TokensSelected) -> list[db.DexNormalizedLiquidity]:

    with db.get_db_session() as session:

        # Select rows where both tokens addresses are present in the collumns,
        # no matter in which
        first_and = sqlalchemy.and_(
            db.DexNormalizedLiquidity.token_x_address == tokens.collateral.address,
            db.DexNormalizedLiquidity.token_y_address == tokens.loan.address,
        )

        second_and = sqlalchemy.and_(
            db.DexNormalizedLiquidity.token_x_address == tokens.loan.address,
            db.DexNormalizedLiquidity.token_y_address == tokens.collateral.address,
        )

        subquery = (
            session.query(
                sqlalchemy.func.max(db.DexNormalizedLiquidity.timestamp).label(
                    "max_timestamp"
                ),
                db.DexNormalizedLiquidity.token_x_address,
                db.DexNormalizedLiquidity.token_y_address,
                db.DexNormalizedLiquidity.market_address,
            )
            .filter(sqlalchemy.or_(first_and, second_and))
            .group_by(
                db.DexNormalizedLiquidity.token_x_address,
                db.DexNormalizedLiquidity.token_y_address,
                db.DexNormalizedLiquidity.market_address,
            )
            .subquery()
        )

        result = (
            session.query(db.DexNormalizedLiquidity)
            .join(
                subquery,
                sqlalchemy.and_(
                    db.DexNormalizedLiquidity.token_x_address
                    == subquery.c.token_x_address,
                    db.DexNormalizedLiquidity.token_y_address
                    == subquery.c.token_y_address,
                    db.DexNormalizedLiquidity.timestamp == subquery.c.max_timestamp,
                    db.DexNormalizedLiquidity.market_address
                    == subquery.c.market_address,
                ),
            )
            .order_by(db.DexNormalizedLiquidity.timestamp.desc())
            .all()
        )

    return result


# TODO: To be implemented.
# def prepare_data(
# 	state: src.protocols.state.State,  # pylint: disable=W0613
# 	prices: dict[str, decimal.Decimal],  # pylint: disable=W0613
# 	amms: src.protocols.dexes.amms.Amms,  # pylint: disable=W0613
# 	collateral_token: str,  # pylint: disable=W0613
# 	debt_token: str,  # pylint: disable=W0613
# 	save_data: bool,  # pylint: disable=W0613
# ) -> pd.DataFrame:
# 	return pd.DataFrame()


def chart_range(start, stop, step) -> Iterator[float]:
    while start < stop:
        yield start
        start += step


def get_token_range_step(price: float) -> float: # pylint: disable=R0911
    if price > 10_000:
        return 2_500

    if price > 1_000:
        return 50

    if price > 100:
        return 2.5

    if price > 1:
        return 0.1

    if price > 0.1:
        return 0.01

    if price > 0.01:
        return 0.001

    if price > 0.001:
        return 0.0001

    if price > 0.0001:
        return 0.00001

    return 0.000001


def get_range(start, stop, step) -> list[float]:
    return list(chart_range(start, stop, step))


def get_token_range(price) -> list[float]:
    step = get_token_range_step(price)
    return get_range(step, price * 1.3, step)


# # TODO: To be implemented.
# def get_liquidable_debt(
# 	protocols: list[str],  # pylint: disable=W0613
# 	token_pair: str,  # pylint: disable=W0613
# 	prices: dict[str, decimal.Decimal],  # pylint: disable=W0613
# 	collateral_token_price: decimal.Decimal,  # pylint: disable=W0613
# ) -> decimal.Decimal:
# 	return decimal.Decimal("0")


def adjust_liquidity(liq: list[db.DexNormalizedLiquidity], token: Token):

    adj_result = []

    for res in liq:
        if token.address == res.token_x_address:
            adj_result.append(res)
            continue

        adj_bids = []
        adj_asks = []

        if not res.bids:
            # TODO: Report
            continue
        if not res.asks:
            # TODO: Report
            continue

        for bid_level in res.bids:
            new_price = 1 / bid_level[0]
            new_volume = bid_level[0] * bid_level[1]

            adj_bids.append((new_price, new_volume))

        for ask_level in list(res.asks):
            new_price = 1 / ask_level[0]
            new_volume = ask_level[0] * ask_level[1]

            adj_asks.append((new_price, new_volume))

        adj_res = db.DexNormalizedLiquidity(
            timestamp=res.timestamp,
            dex=res.dex,
            market_address=res.market_address,
            token_x_address=res.token_y_address,
            token_y_address=res.token_x_address,
            bids=adj_asks,
            asks=adj_bids,
        )
        adj_result.append(adj_res)
    return adj_result


def get_debt_token_supply_at_price_point(
    entries: list[db.DexNormalizedLiquidity], price_point: float, debt_token_price
) -> float:
    """
    Returns supply of debt token for given price point.
    """
    # Price points are in terms of collateral/debt, but entries should now be adjusted
    # to debt/collateral so take inverse of price
    supply = 0

    for entry in entries:
        if not entry.bids:
            # TODO: Report
            continue
        if not entry.asks:
            # TODO: Report
            continue

        for level in list(entry.bids) + list(entry.asks):
            level_price = (1/level[0] * debt_token_price)
            if (level_price > price_point) and (level_price < price_point * 1.05):
                supply += level[1] * debt_token_price

    return supply


custom_hash_function = lambda x: hash(str(x))
@st.cache_data(
    ttl=datetime.timedelta(minutes=30), 
    show_spinner='Loading liquidity vs. debt comparison chart.',
    hash_funcs={
        list[str]: custom_hash_function, 
        TokensSelected: custom_hash_function,
        PricesType: custom_hash_function
    }
)
def get_main_chart_data(
    protocols: list[str],
    token_selection: TokensSelected,
    prices: dict[str, float | None],
) -> pd.DataFrame:

    collateral_token = token_selection.collateral
    collateral_token_price = prices.get(collateral_token.address)
    liquidity_entries = get_normalized_liquidity(token_selection)
    adjusted_entries = adjust_liquidity(liquidity_entries, token_selection.loan)

    collateral_token_price = prices.get(token_selection.collateral.address)
    debt_token_price = prices.get(token_selection.loan.address)

    data = pd.DataFrame(
        {
            "collateral_token_price": get_token_range(collateral_token_price),
        }
    )

    data["debt_token_supply"] = data["collateral_token_price"].apply(
        lambda x: get_debt_token_supply_at_price_point(adjusted_entries, x, debt_token_price)
    )

    # TODO: use protocols
    liquidable_dept = get_liquidable_debt(protocols=protocols, token_pair=token_selection)
    data = pd.merge(
        data,
        liquidable_dept[['collateral_token_price', 'amount']],
        left_on='collateral_token_price',
        right_on='collateral_token_price',
        how='left',
    )
    data['amount'] = data['amount'].fillna(0)

    return data


def get_figure(
    token_pair: TokensSelected,
    data: pd.DataFrame,
    prices: dict[str, float | None],
) -> plotly.graph_objs.Figure:

    df_long = data.melt(id_vars=["collateral_token_price"], 
                  value_vars=["debt_token_supply", "amount"],
                  var_name="Type", value_name="Value")

    color_discrete_map = {
        "debt_token_supply": "#636EFA",  # Blue color for debt_token_supply
        "amount": "#50C878"             # Red color for amount
    }

    figure = plotly.express.bar(
        data_frame=df_long,
        x="collateral_token_price",
        # TODO: Add `liquidable_debt_at_interval`.
        y="Value",
        title=f"Liquidable debt and the corresponding supply of {token_pair.loan.symbol} at various price intervals of "
        f"{token_pair.collateral.symbol}",
        color="Type",
        barmode="overlay",
        color_discrete_map=color_discrete_map,
        opacity=0.65,
        # TODO: Align colors with the rest of the app.
        # color_discrete_map={"liquidable_debt_at_interval": "#ECD662", "debt_token_supply": "#4CA7D0"},
    )

    figure.update_traces(hovertemplate="<b>Price:</b> %{x}<br><b>%{data.name}:</b> %{y}")
    figure.update_traces(
        selector={"name": "liquidable_debt_at_interval"},
        name=f"Liquidable {token_pair.collateral.symbol} debt",
    )
    figure.update_traces(
        selector={"name": "debt_token_supply"}, name=f"{token_pair.loan.symbol} available liquidity"
    )
    figure.update_traces(
        selector={"name": "amount"}, name=f"{token_pair.loan.symbol} liquidable amount"
    )
    figure.update_xaxes(title_text=f"{token_pair.collateral.symbol} Price (USD)")
    figure.update_yaxes(title_text="Volume (USD)")
    collateral_token_price = prices.get(token_pair.collateral.address)

    if not collateral_token_price:
        # TODO: Handle
        collateral_token_price = 1

    figure.add_vline(
        x=collateral_token_price,
        line_width=2,
        line_dash="dash",
        line_color="black",
    )
    figure.add_vrect(
        x0=0.9 * collateral_token_price,
        x1=1.1 * collateral_token_price,
        annotation_text="Current price +- 10%",
        annotation_font_size=11,
        annotation_position="top left",
        fillcolor="gray",
        opacity=0.25,
        line_width=2,
    )
    return figure

