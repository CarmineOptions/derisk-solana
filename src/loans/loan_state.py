import logging
import time
from typing import Callable, Literal, Type, TypeVar

import pandas
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db import (
    MangoLoanStates,
    MarginfiLoanStates,
    KaminoLoanStates,
    SolendLoanStates,
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    KaminoParsedTransactions,
    SolendParsedTransactions,
    get_db_session,
)

MARGINFI = "marginfi"
MANGO = "mango"
KAMINO = "kamino"
SOLEND = "solend"

Protocol = Literal["marginfi", "mango", "kamino", "solend"]
AnyEvents = list[
    MangoParsedTransactions
    | MarginfiParsedTransactions
    | KaminoParsedTransactions
    | SolendParsedTransactions
]

TypeMarginfi = TypeVar("TypeMarginfi", bound=MarginfiParsedTransactions)
TypeMango = TypeVar("TypeMango", bound=MangoParsedTransactions)
TypeKamino = TypeVar("TypeKamino", bound=KaminoParsedTransactions)
TypeSolend = TypeVar("TypeSolend", bound=SolendParsedTransactions)

ProcessFuncTypeMarginfi = Callable[[list[TypeMarginfi]], pandas.DataFrame]
ProcessFuncTypeMango = Callable[[list[TypeMango]], pandas.DataFrame]
ProcessFuncTypeKamino = Callable[[list[TypeKamino]], pandas.DataFrame]
ProcessFuncTypeSolend = Callable[[list[TypeSolend]], pandas.DataFrame]

ProtocolFunc = (
    ProcessFuncTypeMarginfi
    | ProcessFuncTypeMango
    | ProcessFuncTypeKamino
    | ProcessFuncTypeSolend
)


def process_marginfi_events(
    events: list[MarginfiParsedTransactions],
) -> pandas.DataFrame:
    # TODO: process marginfi events
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


def process_solend_events(events: list[SolendParsedTransactions]) -> pandas.DataFrame:
    # TODO: process solend events
    print(events)

    return pandas.DataFrame()


def protocol_to_process_func(
    protocol: Protocol,
) -> ProtocolFunc:
    if protocol == MARGINFI:
        return process_marginfi_events
    if protocol == MANGO:
        return process_mango_events
    if protocol == KAMINO:
        return process_kamino_events
    if protocol == SOLEND:
        return process_solend_events
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def protocol_to_model(
    protocol: Protocol,
) -> (
    Type[MangoLoanStates]
    | Type[MarginfiLoanStates]
    | Type[KaminoLoanStates]
    | Type[SolendLoanStates]
):
    if protocol == MARGINFI:
        return MarginfiLoanStates
    if protocol == MANGO:
        return MangoLoanStates
    if protocol == KAMINO:
        return KaminoLoanStates
    if protocol == SOLEND:
        return SolendLoanStates
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


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


def fetch_events(min_slot: int, protocol: Protocol, session: Session) -> AnyEvents:
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

    if protocol == "solend":
        return (
            session.query(SolendParsedTransactions)
            .filter(SolendParsedTransactions.block > min_slot)
            .all()
        )

    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def process_events_to_loan_states(
    protocol: Protocol,
    process_function: Callable[
        [AnyEvents],
        pandas.DataFrame,
    ],
    session: Session,
):
    current_loan_states = fetch_loan_states(protocol, session)
    min_slot = 0

    if len(current_loan_states) > 0:
        min_slot = int(current_loan_states.iloc[0]["slot"])

    events: AnyEvents = fetch_events(min_slot, protocol, session)

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
