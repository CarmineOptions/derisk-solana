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



def get_token(pair: str, split_character: str, base: bool) -> str:
	token = pair.split(split_character)[0] if base else pair.split(split_character)[1]
	# TODO: Create a proper mapping.
	return 'ETH' if 'ETH' in token else token


class Pool:

	def __init__(
		self,
		base_token: str,
		quote_token: str,
		base_token_amount: int,
		quote_token_amount: int,
	):
		self.base_token: str = base_token
		self.quote_token: str = quote_token
		self.base_token_amount: int = base_token_amount
		self.quote_token_amount: int = quote_token_amount

	def supply_at_price(self, initial_price: decimal.Decimal):
		# Assuming constant product function.
		constant = self.base_token_amount * self.quote_token_amount
		return (initial_price * constant) ** decimal.Decimal("0.5") * (
			decimal.Decimal("1") -
			decimal.Decimal("0.95") ** decimal.Decimal("0.5")
		)


# TODO: To be implemented.
def prepare_data(
	state: src.protocols.state.State,
	prices: dict[str, decimal.Decimal],
	amms: src.amms.Amms,
	collateral_token: str,
	debt_token: str,
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


def decimal_range(start: decimal.Decimal, stop: decimal.Decimal, step: decimal.Decimal) -> Iterator[decimal.Decimal]:
    while start < stop:
        yield start
        start += step


def get_range(start: decimal.Decimal, stop: decimal.Decimal, step: decimal.Decimal) -> list[decimal.Decimal]:
    return [x for x in decimal_range(start=start, stop=stop, step=step)]


def get_collateral_token_range(
    collateral_token: str,
    collateral_token_price: decimal.Decimal,
) -> list[decimal.Decimal]:
	assert collateral_token in {"ETH", "SOL", "JUP"}
	TOKEN_STEP = {
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
	protocols: list[str],
	token_pair: str,
	prices: dict[str, decimal.Decimal],
	collateral_token_price: decimal.Decimal,
) -> decimal.Decimal:
	return decimal.Decimal("0")


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
	figure.update_traces(hovertemplate=("<b>Price:</b> %{x}<br>" "<b>Volume:</b> %{y}"))
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
def get_dangerous_price_level_data(data: pandas.DataFrame) -> pandas.Series:
	return pandas.Series(
		index=[
			"collateral_token_price",
			"liquidable_debt_at_interval",
			"debt_token_supply",
			"debt_to_supply_ratio",
		],
	)


# TODO: To be implemented.
def get_risk(data: pandas.Series) -> str:
	return ''