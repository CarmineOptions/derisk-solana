import decimal

import pandas
import plotly.express
import plotly.graph_objs

import src.amms
import src.protocols.state



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


# TODO: To be implemented.
def load_data(protocols: list[str], token_pair: str) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_figure(data: pandas.DataFrame, token_pair: str) -> plotly.graph_objs.Figure:
	return plotly.express.bar()


# TODO: To be implemented.
def get_dangerous_price_level_data(data: pandas.DataFrame) -> pandas.Series:
	return pandas.Series(index=[])


# TODO: To be implemented.
def get_risk(data: pandas.Series) -> str:
	return ''