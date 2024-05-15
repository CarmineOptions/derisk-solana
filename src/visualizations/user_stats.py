
import datetime
from typing import Literal, Callable, Type
import logging

import pandas as pd
import streamlit as st

from sqlalchemy import func, and_, Float
from sqlalchemy.sql import label
import sqlalchemy
from sqlalchemy.orm.session import Session

import db
from src.visualizations.shared import AnyHealthRatioModel, get_health_ratio_protocol_model


def fetch_protocol_user_stats(session: Session, model: AnyHealthRatioModel) -> dict[str, float]:
    
    # Subquery to get the latest timestamp for each user
    subquery = session.query(
        model.user,
        func.max(model.timestamp).label('latest_timestamp')
    ).group_by(model.user).subquery()

    active_users_case = sqlalchemy.case((model.collateral.cast(Float)>0, 1), else_=None)
    active_borrowers_case = sqlalchemy.case((model.debt.cast(Float)>0, 1), else_=None)

    # Main query to fetch the latest entries and calculate the statistics
    query = session.query(
        func.count(active_users_case),
        func.count(active_borrowers_case),
        func.sum(model.debt.cast(Float)),
        func.sum(model.risk_adjusted_collateral.cast(Float)),
    ).join(
        subquery,
        and_(
            model.user == subquery.c.user,
            model.timestamp == subquery.c.latest_timestamp
        )
    )
    
    # Execute the query and fetch the results
    result = query.one()

    return {
        'active_users': result[0], # Users where collateral > 0
        'active_borrowers': result[1], # Users where debt > 0
        'total_debt': result[2],
        'total_risk_adj_collateral': result[3]
    }


@st.cache_data(ttl=datetime.timedelta(minutes=60))
def get_users_stats(protocols: list[str]) -> pd.DataFrame:
    """
    For list of protocols it returns a dataframe containg all users stats.
    """
    data = []

    with db.get_db_session() as sesh:
        for protocol in protocols:
            # Get the correct model for given protocol
            model = get_health_ratio_protocol_model(protocol)

            if not model:
                logging.error(f'Unable to find HealthRatio model for protocol "{protocol}"')
                continue

            logging.info(f'Fetching user stats for "{protocol}"')

            stats = fetch_protocol_user_stats(sesh, model)

            stats['protocol'] = protocol.capitalize()

            data.append(stats)

    full_df = pd.DataFrame(data)   
    full_df = full_df.rename(columns = {
        'protocol': 'Protocol',
        'active_users': "Number of active users",
        'active_borrowers': "Number of active borrowers",
        'total_debt': "Total debt (freedom units)",
        'total_risk_adj_collateral': "Total risk adjusted collateral (bald eagles)"
    })

    return full_df.set_index('Protocol')
