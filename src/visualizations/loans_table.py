import decimal
from typing import Literal, Callable, Type
import logging
import datetime

import pandas as pd
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
import streamlit as st

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

AnyHealthRatioModel = (
    Type[db.MangoHealthRatio]
    | Type[db.SolendHealthRatio]
    # | Type[db.MarginfiHealthRatio]
    # | Type[db.KaminoHealthRatio]
)

def get_health_ratio_protocol_model(protocol: Protocol) -> AnyHealthRatioModel | None:

	if protocol == MANGO:
		return db.MangoHealthRatio

	if protocol == KAMINO:
		return None
		# return db.KaminoHealthRatio

	if protocol == MARGINFI:
		return None
		# return db.MarginfiHealthRatio
		
	if protocol == SOLEND:
		return db.SolendHealthRatio

	return None

def fetch_health_ratios(session: Session, model: AnyHealthRatioModel, n: int) -> pd.DataFrame:
	"""
	Fetches users health ratios for given Protocol.

	Parameters:
	- session: DB Session (this function doesn't close it)
	- model: Any health ratio model
	- n: how many users to fetch (n users with lowest std health factor)
	
	Note: Does not close the session.
	"""
	subquery = session.query(
		model.user,
		func.max(model.timestamp).label('latest_timestamp')
	).group_by(model.user).subquery()

	# Join the subquery with the main table to get the latest entries
	latest_entries_query = session.query(model).join(
		subquery,
		(model.user == subquery.c.user) & (model.timestamp == subquery.c.latest_timestamp)
	).filter(model.health_factor.isnot(None))

	latest_entries = latest_entries_query.order_by(model.std_health_factor.asc()).limit(n).all()

	data = [{
		'slot': entry.slot,
		'last_update': entry.last_update,
		'user': entry.user,
		'health_factor': entry.health_factor,
		'std_health_factor': entry.std_health_factor,
		'collateral': entry.collateral,
		'risk_adjusted_collateral': entry.risk_adjusted_collateral,
		'debt': entry.debt,
		'risk_adjusted_debt': entry.risk_adjusted_debt,
		'protocol': entry.protocol,
		'timestamp': entry.timestamp
	} for entry in latest_entries]

	return pd.DataFrame(data)

@st.cache_data(ttl=datetime.timedelta(minutes=10))
def load_user_health_ratios(protocols: list[str]) -> pd.DataFrame:
	"""
	For list of protocols it returns a dataframe containg all users health ratios.
	"""

	data = []

	with db.get_db_session() as sesh:
		for protocol in protocols:

			# Get the correct model for given protocol
			model = get_health_ratio_protocol_model(protocol)

			if not model:
				logging.error(f'Unable to find HealthRatio model for protocol "{protocol}"')
				continue

			logging.info(f'Fetching user health ratios for "{protocol}"')

			# Fetch health ratios data
			health_ratios_df = fetch_health_ratios(sesh, model, 50)
			# Drop redundant columns
			health_ratios_df = health_ratios_df.drop(['timestamp', 'slot', 'last_update'], axis =1)
			# Rename some collumns that are also present in loan states 
			# (in loan states these collumns contain the dict with debt/collateral holdings)
			health_ratios_df = health_ratios_df.rename(columns={'collateral': 'collateral_usd', 'debt': 'debt_usd'})

			# Fetch loan states 
			loan_states_df = fetch_loan_states(protocol, sesh)
			# Select only needed columns
			loan_states_df = loan_states_df[['user', 'collateral', 'debt']]

			# Merge health ratios and loan states so we have user holdings
			# also present in the table
			full_df = health_ratios_df.merge(loan_states_df, on = 'user')
			# Rename collumns to make it nicer
			full_df = full_df.rename(columns={
				'user': 'User',
				'protocol': 'Protocol',
				'health_factor': 'Health Factor',
				'std_health_factor': 'Standardized Health Factor',
				'collateral_usd': 'Collateral (USD)',
				'risk_adjusted_collateral': 'Risk. Adj. Collateral',
				'debt_usd': 'Debt (USD)',
				'risk_adjusted_debt': 'Risk. Adj. Debt',
				'collateral': 'Collaterals',
				'debt': 'Debts'
			})

			data.append(full_df)

	return pd.concat(data).set_index('User')

