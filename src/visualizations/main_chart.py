import decimal

import pandas

import src.amms
import src.protocols.state



# TODO: To be implemented.
def get_main_chart_data(
	state: src.protocols.state.State,
	prices: dict[str, decimal.Decimal],
	amms: src.amms.Amms,
	collateral_token: str,
	debt_token: str,
	save_data: bool,
) -> pandas.DataFrame:
	return pandas.DataFrame()