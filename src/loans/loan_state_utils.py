
import pandas
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db import LoanStates


def store_loan_states(df: pandas.DataFrame, session: Session):
    """
    Stores data from a pandas DataFrame to the loan_states table.

    Args:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - protocol (str): Description of protocol.
        - user (str): Description of user.
        - collateral (json/dict): JSON or dictionary representing collateral.
        - debt (json/dict): JSON or dictionary representing debt.

    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.
    """

    for _, row in df.iterrows():
        loan_state = LoanStates(
            slot=row['slot'],
            protocol=row['protocol'],
            user=row['user'],
            collateral=row['collateral'],
            debt=row['debt']
        )
        session.add(loan_state)
    session.commit()


def fetch_loan_states(session: Session) -> pandas.DataFrame:
    """
    Fetches loan states with the max slot from the DB and returns them as a DataFrame

    Args:
    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.

    Returns:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - protocol (str): Description of protocol.
        - user (str): Description of user.
        - collateral (json/dict): JSON or dictionary representing collateral.
        - debt (json/dict): JSON or dictionary representing debt.
    """

    # Define a subquery for the maximum slot value
    max_slot_subquery = session.query(func.max(LoanStates.slot)).subquery()

    # Retrieve entries from the loan_states table where slot equals the maximum slot value
    query_result = session.query(LoanStates).filter(LoanStates.slot == max_slot_subquery).all()

    df = pandas.DataFrame([{
        'slot': record.slot,
        'protocol': record.protocol,
        'user': record.user,
        'collateral': record.collateral,
        'debt': record.debt
    } for record in query_result])
    return df



def fetch_events(min_slot: int, protocol: str, session: Session) -> pandas.DataFrame:
    """
    Fetches loan states with the max slot from the DB and returns them as a DataFrame

    Args:
    - min_slot (int): Slot from which events will be fetched (non-inclusive).
    - protocol (str): Protocol which events will be fetched.
    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.

    Returns:
    - df (pandas.DataFrame): Events in a DataFrame
    """
    pass
