import decimal
from typing import Literal, Callable
import pandas
import src.loans.mango
import src.loans.kamino
import src.loans.marginfi
import src.loans.solend

from src.loans.loan_state import fetch_loan_states
import db


# # TODO: To be implemented.
# def prepare_data(
# 	state: src.protocols.state.State,
# 	prices: dict[str, decimal.Decimal],
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()


MARGINFI = "marginfi"
MANGO = "mango"
KAMINO = "kamino"
SOLEND = "solend"
Protocol = Literal["marginfi", "mango", "kamino", "solend"]


def get_loan_states_handler(protocol: Protocol) -> Callable:
	if protocol == MANGO:
		return src.loans.mango.get_mango_user_stats_df

	if protocol == KAMINO:
		return src.loans.kamino.get_kamino_user_stats_df

	if protocol == MARGINFI:
		return src.loans.marginfi.get_marginfi_user_stats_df
		
	if protocol == SOLEND:
		return src.loans.solend.get_solend_user_stats_df
		
		
def load_user_stats_data(protocols) -> pandas.DataFrame:

	data = []

	with db.get_db_session() as sesh:
		for protocol in protocols:
			state_handler = get_loan_states_handler(protocol)
			loan_states = fetch_loan_states(protocol, sesh)

			df = state_handler(loan_states)
			data.append(df)
		
	return pandas.concat(data)
