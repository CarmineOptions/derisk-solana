import decimal

import pandas

import src.protocols.state



# TODO: To be implemented.
def get_loans_table_data(
	state: src.protocols.state.State,
	prices: dict[str, decimal.Decimal],
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()