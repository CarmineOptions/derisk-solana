import logging
import time
import pandas
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db import (
    LoanStates,
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    KaminoParsedTransactions,
    get_db_session,
)


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
            slot=row["slot"],
            protocol=row["protocol"],
            user=row["user"],
            collateral=row["collateral"],
            debt=row["debt"],
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
    query_result = (
        session.query(LoanStates).filter(LoanStates.slot == max_slot_subquery).all()
    )

    df = pandas.DataFrame(
        [
            {
                "slot": record.slot,
                "protocol": record.protocol,
                "user": record.user,
                "collateral": record.collateral,
                "debt": record.debt,
            }
            for record in query_result
        ]
    )
    return df


def fetch_events(
    min_slot: int, protocol: str, session: Session
) -> MarginfiParsedTransactions | MangoParsedTransactions | KaminoParsedTransactions:
    """
    Fetches loan states with the max slot from the DB and returns them as a DataFrame

    Args:
    - min_slot (int): Slot from which events will be fetched (non-inclusive).
    - protocol (str): Protocol which events will be fetched.
    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.

    Returns:
    - df (pandas.DataFrame): Events in a DataFrame
    """
    if protocol == "mango":
        return (
            session.query(MangoParsedTransactions)
            .filter(MangoParsedTransactions.block > min_slot)
            .all()
        )
    if protocol == "marginfi":
        return (
            session.query(MarginfiParsedTransactions)
            .filter(MarginfiParsedTransactions.block > min_slot)
            .all()
        )
    if protocol == "kamino":
        return (
            session.query(KaminoParsedTransactions)
            .filter(KaminoParsedTransactions.block > min_slot)
            .all()
        )
    raise ValueError(f"invalid protocol {protocol}")


def process_events_to_loan_states(session: Session):
    current_loan_states = fetch_loan_states(session)
    min_slot = 0

    if len(current_loan_states) > 0:
        min_slot = int(current_loan_states.iloc[0]["slot"])

    mango_events: list[MangoParsedTransactions] = fetch_events(
        min_slot, "mango", session
    )
    marginfi_events: list[MarginfiParsedTransactions] = fetch_events(
        min_slot, "marginfi", session
    )
    kamino_events: list[KaminoParsedTransactions] = fetch_events(
        min_slot, "kamino", session
    )

    new_loan_state = pandas.DataFrame()

    for event in mango_events:
        # TODO: process mango events
        pass

    for event in marginfi_events:
        # TODO: process marginfi events
        pass

    for event in kamino_events:
        # TODO: process kamino events
        pass

    store_loan_states(new_loan_state, session)

def process_events_continuously():
    logging.info("Starting events to loan_states processing.")
    session = get_db_session()
    while True:
        process_events_to_loan_states(session)
        logging.info("Updated loan_states.")
        time.sleep(120)
