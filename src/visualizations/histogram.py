import decimal

import plotly.express
import plotly.graph_objs

import src.protocols.state



# TODO: To be implemented.
def prepare_data(
	state: src.protocols.state.State,
	prices: dict[str, decimal.Decimal],
	save_data: bool,
) -> None:
	pass


# TODO: To be implemented.
def load_data(protocols: list[str], token_pair: str) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def get_figure(data: pandas.DataFrame) -> plotly.graph_objs.Figure:
	return plotly.express.histogram()