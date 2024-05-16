
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
    
    # Subquery to get the latest slot for each user
    subquery = session.query(
        model.user,
        func.max(model.slot).label('latest_slot')
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
            model.slot == subquery.c.latest_slot
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


@st.cache_data(ttl=datetime.timedelta(minutes=60), show_spinner = 'Loading user stats.')
def load_users_stats_single_protocol(_session: Session, protocol: str) -> dict[str, float|str] | None:
    # Get the correct model for given protocol
    model = get_health_ratio_protocol_model(protocol)

    if not model:
        return None

    logging.info(f'Fetching user stats for "{protocol}"')

    stats = fetch_protocol_user_stats(_session, model)

    stats['protocol'] = protocol.capitalize()
    return stats


def load_users_stats(protocols: list[str]) -> pd.DataFrame:
    """
    For list of protocols it returns a dataframe containg all users stats.
    """
    data = []
    with db.get_db_session() as session:
        for protocol in protocols:
            stats = load_users_stats_single_protocol(session, protocol)
            
            if stats is None:
                logging.error(f'Unable to get user stats data for protocol "{protocol}"')
                continue
                
            data.append(stats)

    full_df = pd.DataFrame(data)   
    full_df = full_df.rename(columns = {
        'protocol': 'Protocol',
        'active_users': "Number of active users",
        'active_borrowers': "Number of active borrowers",
        'total_debt': "Total debt (USD)",
        'total_risk_adj_collateral': "Total risk adjusted collateral (USD)"
    })
    
    return full_df.set_index('Protocol')
