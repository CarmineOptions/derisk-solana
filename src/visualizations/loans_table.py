import decimal
from typing import Literal, Callable, Type
import logging
import datetime

import pandas as pd
import sqlalchemy
from sqlalchemy.orm.session import Session
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func
import sqlalchemy
import streamlit as st

import src.loans.mango
import src.loans.kamino
import src.loans.marginfi
import src.loans.solend
from src.loans.loan_state import protocol_to_model

from src.visualizations.shared import AnyHealthRatioModel, get_health_ratio_protocol_model

from src.loans.loan_state import fetch_loan_states

import db


# # TODO: To be implemented.
# def prepare_data(
# 	state: src.protocols.state.State,
# 	prices: dict[str, decimal.Decimal],
# 	save_data: bool,
# ) -> pandas.DataFrame:
# 	return pandas.DataFrame()

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
		func.max(model.slot).label('latest_slot')
	).group_by(model.user).subquery()

	# Join the subquery with the main table to get the latest entries. Ignore loans with suspicious data.
	latest_entries_query = session.query(model) \
		.join(
			subquery,
			(model.user == subquery.c.user) & (model.slot == subquery.c.latest_slot)
		) \
		.filter(model.health_factor.isnot(None)) \
		.filter(model.risk_adjusted_collateral != '0') \
		.filter(model.risk_adjusted_collateral != '0.0') \
		.filter(sqlalchemy.or_(model.std_health_factor.cast(sqlalchemy.Float) > 0.001, model.protocol != 'MarginFi'))

	latest_entries = latest_entries_query.order_by(model.std_health_factor.cast(sqlalchemy.Float).asc()).all()

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


def fetch_loan_states_for_users(session: Session, protocol: str, users: list[str]) -> pd.DataFrame:
	model, _ = protocol_to_model(protocol)
	subquery = session.query(
		model.user,
		sqlalchemy.func.max(model.slot).label('max_slot')
	).group_by(model.user).subquery('t2')

	# For each user, query the loan state with tha maximum slot.
	query_result = session.query(model).join(
		subquery,
		sqlalchemy.and_(
			model.user == subquery.c.user,
			model.slot == subquery.c.max_slot
		)
	).filter(model.user.in_(users))

	df = pd.DataFrame(
		[
			{
				"slot": record.slot,
				"protocol": record.protocol,
				"user": record.user,
				"collateral": record.collateral,
				"debt": record.debt,
			}
			for record in query_result.all()
		]
	)
	return df


@st.cache_data(ttl=datetime.timedelta(minutes=60), show_spinner = 'Loading health ratios.')
def load_user_health_ratios_single_protocol(_session: Session, protocol: str) -> pd.DataFrame | None:
	model = get_health_ratio_protocol_model(protocol)

	if not model:
		return None

	logging.info(f'Fetching user health ratios for "{protocol}"')

	# Fetch health ratios data
	health_ratios_df = fetch_health_ratios(_session, model, 50)
	# Drop redundant columns
	health_ratios_df = health_ratios_df.drop(['timestamp', 'slot', 'last_update'], axis =1)
	# Rename some collumns that are also present in loan states 
	# (in loan states these collumns contain the dict with debt/collateral holdings)
	health_ratios_df = health_ratios_df.rename(columns={'collateral': 'collateral_usd', 'debt': 'debt_usd'})

	# Fetch loan states 
	loan_states_df = fetch_loan_states(protocol, _session)

	if len(loan_states_df) == 0:
		logging.warning(f'No loan states found for protocol "{protocol}"')
		return None

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
	
	return full_df


def load_user_health_ratios(protocols: list[str]) -> pd.DataFrame:
	"""
	For list of protocols it returns a dataframe containg all users health ratios.
	"""

	data = []
	with db.get_db_session() as session:
		for protocol in protocols:

			# Get the correct model for given protocol
			df = load_user_health_ratios_single_protocol(session, protocol)
			if df is None:
				logging.error(f'Unable to get user health ratios data for protocol "{protocol}"')
				continue

			data.append(df)

	return pd.concat(data).set_index('User')

