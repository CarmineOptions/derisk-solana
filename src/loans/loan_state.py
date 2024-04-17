import logging
import time
from typing import Callable, Literal

import pandas
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db import (
    MangoLoanStates,
    MarginfiLoanStates,
    KaminoLoanStates,
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    KaminoParsedTransactions,
    get_db_session,
)

MARGIFI = "margifi"
MANGO = "mango"
KAMINO = "kamino"

Protocol = Literal["margifi", "mango", "kamino"]

AnyParsedTransactions = (
    MangoParsedTransactions | MarginfiParsedTransactions | KaminoParsedTransactions
)


def process_margifi_events(
    events: list[MarginfiParsedTransactions],
) -> pandas.DataFrame:
    # TODO: process margify events
    print(events)

    return pandas.DataFrame()


def process_mango_events(events: list[MangoParsedTransactions]) -> pandas.DataFrame:
    # TODO: process mango events
    print(events)

    return pandas.DataFrame()


def process_kamino_events(events: list[KaminoParsedTransactions]) -> pandas.DataFrame:
    # TODO: process kamino events
    print(events)

    return pandas.DataFrame()


def protocol_to_process_func(
    protocol: Protocol,
) -> Callable[[list[AnyParsedTransactions]], pandas.DataFrame]:
    if protocol == MARGIFI:
        return process_margifi_events
    elif protocol == MANGO:
        return process_mango_events
    elif protocol == KAMINO:
        return process_kamino_events
    else:
        raise ValueError(f'Invalid protocol "{protocol}"')


def protocol_to_model(
    protocol: Protocol,
) -> MangoLoanStates | MarginfiLoanStates | KaminoLoanStates:
    if protocol == MARGIFI:
        return MarginfiLoanStates
    elif protocol == MANGO:
        return MangoLoanStates
    elif protocol == KAMINO:
        return KaminoLoanStates
    else:
        raise ValueError(f'Invalid protocol "{protocol}"')


def store_loan_states(df: pandas.DataFrame, protocol: Protocol, session: Session):
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

    model = protocol_to_model(protocol)

    for _, row in df.iterrows():
        loan_state = model(
            slot=row["slot"],
            protocol=row["protocol"],
            user=row["user"],
            collateral=row["collateral"],
            debt=row["debt"],
        )
        session.add(loan_state)
    session.commit()


def fetch_loan_states(protocol: Protocol, session: Session) -> pandas.DataFrame:
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

    model = protocol_to_model(protocol)

    # Define a subquery for the maximum slot value
    max_slot_subquery = session.query(func.max(model.slot)).subquery()

    # Retrieve entries from the loan_states table where slot equals the maximum slot value
    query_result = session.query(model).filter(model.slot == max_slot_subquery).all()

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
    min_slot: int, protocol: Protocol, session: Session
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


def process_events_to_loan_states(
    protocol: Protocol,
    process_function: Callable[[list[AnyParsedTransactions]], pandas.DataFrame],
    session: Session,
):
    current_loan_states = fetch_loan_states(protocol, session)
    min_slot = 0

    if len(current_loan_states) > 0:
        min_slot = int(current_loan_states.iloc[0]["slot"])

    events: list[MarginfiParsedTransactions] = fetch_events(min_slot, protocol, session)

    new_loan_state = process_function(events)

    store_loan_states(new_loan_state, protocol, session)


def process_events_continuously(protocol: Protocol):
    logging.info("Starting events to loan_states processing.")
    session = get_db_session()

    process_func = protocol_to_process_func(protocol)

    while True:
        process_events_to_loan_states(protocol, process_func, session)
        logging.info("Updated loan_states.")
        time.sleep(120)
