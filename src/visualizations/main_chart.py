from typing import Iterator
import decimal
import json
import operator
import time

import pandas
import plotly.express
import plotly.graph_objs

import src.amms
import src.database
import src.protocols.state



LOOKBACK_DAYS: int = 5
MAXIMUM_PERCENTAGE_PRICE_CHANGE = 0.05

PAIRS_PAIRS_MAPPING: dict[str, tuple[str, ...]] = {
	"ETH-USDC": ("WETH/USDC", "ETHpo/USDC"),
	"SOL-USDC": ("SOL/USDC", ""),
	"SOL-USDT": ("SOL/USDT", ""),
	"JUP-USDC": ("JUP/USDC", ""),
	"JUP-USDT": ("JUP/USDT", ""),
}



def get_token(pair: str, split_character: str, base: bool) -> str:
	token = pair.split(split_character)[0] if base else pair.split(split_character)[1]
	# TODO: Create a proper mapping.
	return 'ETH' if 'ETH' in token else token


class Pool:

	def __init__(
		self,
		base_token: str,
		quote_token: str,
		base_token_amount: decimal.Decimal,
		quote_token_amount: decimal.Decimal,
	):
		self.base_token: str = base_token
		self.quote_token: str = quote_token
		self.base_token_amount: decimal.Decimal = base_token_amount
		self.quote_token_amount: decimal.Decimal = quote_token_amount

	def supply_at_price(self, initial_price: decimal.Decimal):
		# Assuming constant product function.
		constant = self.base_token_amount * self.quote_token_amount
		return (initial_price * constant) ** decimal.Decimal("0.5") * (
			decimal.Decimal("1") -
			decimal.Decimal("0.95") ** decimal.Decimal("0.5")
		)


# TODO: To be implemented.
def prepare_data(
	state: src.protocols.state.State,  # pylint: disable=W0613
	prices: dict[str, decimal.Decimal],  # pylint: disable=W0613
	amms: src.amms.Amms,  # pylint: disable=W0613
	collateral_token: str,  # pylint: disable=W0613
	debt_token: str,  # pylint: disable=W0613
	save_data: bool,  # pylint: disable=W0613
) -> pandas.DataFrame:
	return pandas.DataFrame()


def decimal_range(start: decimal.Decimal, stop: decimal.Decimal, step: decimal.Decimal) -> Iterator[decimal.Decimal]:
    while start < stop:
        yield start
        start += step


def get_range(start: decimal.Decimal, stop: decimal.Decimal, step: decimal.Decimal) -> list[decimal.Decimal]:
    return list(decimal_range(start=start, stop=stop, step=step))


def get_collateral_token_range(
    collateral_token: str,
    collateral_token_price: decimal.Decimal,
) -> list[decimal.Decimal]:
	assert collateral_token in {"ETH", "SOL", "JUP"}
	TOKEN_STEP = {  # pylint: disable=C0103
		"ETH": decimal.Decimal("50"),
		"SOL": decimal.Decimal("2.5"),
		"JUP": decimal.Decimal("0.01"),
	}
	return get_range(
		start = TOKEN_STEP[collateral_token],
		stop = collateral_token_price * decimal.Decimal("1.2"),
		step = TOKEN_STEP[collateral_token],
	)


# TODO: To be implemented.
def get_liquidable_debt(
	protocols: list[str],  # pylint: disable=W0613
	token_pair: str,  # pylint: disable=W0613
	prices: dict[str, decimal.Decimal],  # pylint: disable=W0613
	collateral_token_price: decimal.Decimal,  # pylint: disable=W0613
) -> decimal.Decimal:
	return decimal.Decimal("0")


def get_available_orderbook_liquidity_in_usd(
	orderbook_data: pandas.DataFrame,
	token_pair: str,
	prices: dict[str, decimal.Decimal],
) -> float:

	def _get_best_price(side: str, orderbook_side: list[list[float]]) -> float:
		assert side in {'bid', 'ask'}
		_operator = max if side == 'bid' else min
		return _operator(price for price, _ in orderbook_side)

	# Compute best price.
	for side in ['bid', 'ask']:
		orderbook_data[f'best_{side}'] = orderbook_data[f'{side}s'].apply(
			lambda x: _get_best_price(side=side, orderbook_side=x)  # pylint: disable=W0640
		)
	mid_price = (orderbook_data['best_bid'].max() + orderbook_data['best_ask'].min()) / 2

	def _get_target_liquidity_in_usd(
		orderbook_data: pandas.Series,
		debt_token: str,
		mid_price: float,
		prices: dict[str, decimal.Decimal],
	) -> float:
		base_token = get_token(pair=orderbook_data['pair'], split_character='/', base=True)
		quote_token = get_token(pair=orderbook_data['pair'], split_character='/', base=False)
		side = 'bid' if debt_token == quote_token else 'ask'

		available_liquidity_in_usd = 0
		_operator = operator.gt if side == 'bid' else operator.lt
		target_price = (
			mid_price * (1 - MAXIMUM_PERCENTAGE_PRICE_CHANGE)
			if side == 'bid'
			else mid_price * (1 + MAXIMUM_PERCENTAGE_PRICE_CHANGE)
		)
		for price, liquidity in orderbook_data[f'{side}s']:
			if _operator(price, target_price):
				available_liquidity_in_usd += liquidity
		return available_liquidity_in_usd * float(prices[base_token])

	# Compute the maximum amount of the debt token that can be exchanged for the collateral token without moving the
	# price by more than 5% from the mid.
	_, debt_token = token_pair.split('-')
	orderbook_data['available_liquidity_in_usd'] = orderbook_data.apply(
		lambda x: _get_target_liquidity_in_usd(
			orderbook_data=x,
			debt_token=debt_token,
			mid_price=mid_price,
			prices=prices,
		),
		axis=1,
	)
	return orderbook_data['available_liquidity_in_usd'].sum()


def get_available_orderbook_supply_in_usd(token_pair: str, prices: dict[str, decimal.Decimal]) -> decimal.Decimal:
	connection = src.database.establish_connection()
	token_pairs = PAIRS_PAIRS_MAPPING[token_pair]
	start_timestamp = time.time() - LOOKBACK_DAYS * 24 * 60 * 60
	orderbook_liquidities = pandas.read_sql(
		sql=f"""
			SELECT
				*
			FROM
				public.orderbook_liquidity
			WHERE
				pair IN {token_pairs}
            AND
                timestamp >= {start_timestamp}
			ORDER BY
				timestamp, dex, pair ASC;
		""",
		con = connection,
	)
	connection.close()
	available_liquidities = orderbook_liquidities.groupby('timestamp').apply(
		lambda x: get_available_orderbook_liquidity_in_usd(orderbook_data=x, token_pair=token_pair, prices=prices)
	)
	# TODO: Convert to decimals sooner.
	return decimal.Decimal(str(available_liquidities.quantile(0.05)))


def get_swap_amm_pools(token_pair: str) -> pandas.DataFrame:
	connection = src.database.establish_connection()
	collateral_token, debt_token = token_pair.split('-')
	reversed_token_pair = f'{debt_token}-{collateral_token}'
	token_pairs = (token_pair, reversed_token_pair)
	start_timestamp = time.time() - LOOKBACK_DAYS * 24 * 60 * 60
	swap_amm_pools = pandas.read_sql(
		sql=f"""
			SELECT
				*
			FROM
				public.amm_liquidity
			WHERE
				pair IN {token_pairs} 
            AND
                timestamp >= {start_timestamp}
			ORDER BY
				timestamp, dex, pair ASC;
		""",
		con = connection,
	)
	connection.close()
	swap_amm_pools = swap_amm_pools.groupby(['dex', 'pair']).last()
	return swap_amm_pools.reset_index()


def get_available_amm_liquidity_in_usd(
	token_pair: str,
	amm_data: pandas.DataFrame,
	prices: dict[str, decimal.Decimal],  # pylint: disable=W0613
	collateral_token_price: decimal.Decimal,
) -> decimal.Decimal:
	_, debt_token = token_pair.split('-')
	base_token = get_token(pair=amm_data['pair'], split_character='-', base=True)
	quote_token = get_token(pair=amm_data['pair'], split_character='-', base=False)
	if amm_data['dex'] == 'Meteora':
		additional_info = json.loads(amm_data['additional_info'])
		if float(additional_info['pool_tvl']) <= 0:
			return decimal.Decimal("0")
		base_token_amount = decimal.Decimal(additional_info['pool_token_amounts'][0])
		quote_token_amount = decimal.Decimal(additional_info['pool_token_amounts'][1])
		pool = Pool(
			base_token=base_token if debt_token == quote_token else quote_token,
			quote_token=quote_token if debt_token == quote_token else base_token,
			base_token_amount=base_token_amount if debt_token == quote_token else quote_token_amount,
			quote_token_amount=quote_token_amount if debt_token == quote_token else base_token_amount,
		)
		return pool.supply_at_price(initial_price=collateral_token_price)
	base_token_amount = amm_data['token_x']
	quote_token_amount = amm_data['token_y']
	pool = Pool(
		base_token=base_token if debt_token == quote_token else quote_token,
		quote_token=quote_token if debt_token == quote_token else base_token,
		base_token_amount=base_token_amount if debt_token == quote_token else quote_token_amount,
		quote_token_amount=quote_token_amount if debt_token == quote_token else base_token_amount,
	)
	return pool.supply_at_price(initial_price=collateral_token_price)


def get_supply_at_price(
	token_pair: str,
	prices: dict[str, decimal.Decimal],
	swap_amm_pools: pandas.DataFrame,
	collateral_token_price: decimal.Decimal,
	available_orderbook_supply: decimal.Decimal,
) -> decimal.Decimal:
	available_amm_supply = swap_amm_pools.apply(
		lambda x: get_available_amm_liquidity_in_usd(
			token_pair=token_pair,
			amm_data=x,
			prices=prices,
			collateral_token_price=collateral_token_price,
		),
		axis = 1,
	)
	return available_amm_supply.sum() + available_orderbook_supply


def get_main_chart_data(
	protocols: list[str],
	token_pair: str,
	prices: dict[str, decimal.Decimal],
) -> plotly.graph_objs.Figure:
	collateral_token, _ = token_pair.split('-')
	collateral_token_price = prices[collateral_token]
	data = pandas.DataFrame(
		{
			"collateral_token_price": get_collateral_token_range(
				collateral_token = collateral_token,
				collateral_token_price = collateral_token_price,
			),
		}
	)

	# TODO: Compute liqidable debt.
	data['liquidable_debt'] = data['collateral_token_price'].apply(
        lambda x: get_liquidable_debt(
			protocols=protocols,
			token_pair=token_pair,
			prices=prices,
			collateral_token_price=x,
		)
    )

	# Compute available debt token supply.
	available_orderbook_supply = get_available_orderbook_supply_in_usd(
		token_pair=token_pair,
		prices=prices,
	)
	swap_amm_pools = get_swap_amm_pools(token_pair=token_pair)
	data["debt_token_supply"] = data["collateral_token_price"].apply(
        lambda x: get_supply_at_price(
			token_pair=token_pair,
			prices=prices,
			swap_amm_pools=swap_amm_pools,
            collateral_token_price=x,
            available_orderbook_supply=available_orderbook_supply,
        )
    )
	return data


def get_figure(
	token_pair: str,
	data: pandas.DataFrame,
	prices: dict[str, decimal.Decimal],
) -> plotly.graph_objs.Figure:
	collateral_token, debt_token = token_pair.split('-')
	figure = plotly.express.bar(
		data_frame=data,
		x="collateral_token_price",
		# TODO: Add `liquidable_debt_at_interval`.
		y="debt_token_supply",
		title=f"Liquidable debt and the corresponding supply of {debt_token} at various price intervals of "
			f"{collateral_token}",
		barmode="overlay",
		opacity=0.65,
		# TODO: Align colors with the rest of the app.
		color_discrete_map={"liquidable_debt_at_interval": "#ECD662", "debt_token_supply": "#4CA7D0"},
	)
	figure.update_traces(hovertemplate="<b>Price:</b> %{x}<br>" "<b>Volume:</b> %{y}")
	figure.update_traces(selector={"name": "liquidable_debt_at_interval"}, name=f"Liquidable {debt_token} debt")
	figure.update_traces(selector={"name": "debt_token_supply"}, name=f"{debt_token} supply")
	figure.update_xaxes(title_text=f"{collateral_token} Price (USD)")
	figure.update_yaxes(title_text="Volume (USD)")
	collateral_token_price = prices[collateral_token]
	figure.add_vline(
		x=collateral_token_price,
		line_width=2,
		line_dash="dash",
		line_color="black",
	)
	figure.add_vrect(
		x0=decimal.Decimal("0.9") * collateral_token_price,
		x1=decimal.Decimal("1.1") * collateral_token_price,
		annotation_text="Current price +- 10%",
		annotation_font_size=11,
		annotation_position="top left",
		fillcolor="gray",
		opacity=0.25,
		line_width=2,
	)
	return figure


# TODO: To be implemented.
def get_dangerous_price_level_data(data: pandas.DataFrame) -> pandas.Series:  # pylint: disable=W0613
	return pandas.Series(
		index=[
			"collateral_token_price",
			"liquidable_debt_at_interval",
			"debt_token_supply",
			"debt_to_supply_ratio",
		],
	)


# TODO: To be implemented.
def get_risk(data: pandas.Series) -> str:  # pylint: disable=W0613
	return ''
