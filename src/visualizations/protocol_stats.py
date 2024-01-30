import decimal

import pandas
import plotly.express
import plotly.graph_objs

import src.protocols.state



# TODO: To be implemented.
def get_general_stats(
	states: dict[str, src.protocols.state.State],
	individual_loan_stats: pandas.DataFrame,
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_supply_stats(
	states: dict[str, src.protocols.state.State],
	prices: dict[str, decimal.Decimal],
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_collateral_stats(
	states: dict[str, src.protocols.state.State],
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_debt_stats(
	states: dict[str, src.protocols.state.State],
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_utilization_stats(
	general_stats: pandas.DataFrame,
	supply_stats: pandas.DataFrame,
	debt_stats: pandas.DataFrame,
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_general_stats() -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_supply_stats() -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_collateral_stats() -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_debt_stats() -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_utilization_stats() -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_collateral_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
	return plotly.express.pie()


# TODO: To be implemented.
def get_debt_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
	return plotly.express.pie()


# TODO: To be implemented.
def get_supply_stats_figure(data: pandas.DataFrame, token: str) -> plotly.graph_objs.Figure:
	return plotly.express.pie()