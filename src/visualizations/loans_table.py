import decimal

import pandas

import src.protocols.state



# TODO: To be implemented.
def prepare_data(
	state: src.protocols.state.State,
	prices: dict[str, decimal.Decimal],
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()


# TODO: To be implemented.
def load_data(protocols: list[str], token_pair: str) -> pandas.DataFrame:
	return pandas.DataFrame(columns=["Debt (USD)", "Health factor"])