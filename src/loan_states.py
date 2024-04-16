
import pandas
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
    Fetches loan states from the DB and returns them as a DataFrame

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

    # TODO: limit states that are fetched
    query_result = session.query(LoanStates).all()
    df = pandas.DataFrame([{
        'slot': record.slot,
        'protocol': record.protocol,
        'user': record.user,
        'collateral': record.collateral,
        'debt': record.debt
    } for record in query_result])
    return df
