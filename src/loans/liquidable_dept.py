import logging
import time
from typing import Callable, Literal, Type, TypeVar

import pandas
from sqlalchemy import func
from sqlalchemy.orm.session import Session
from db import (
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    KaminoParsedTransactions,
    SolendParsedTransactions,
    MangoLiquidableDepts,
    MarginfiLiquidableDepts,
    KaminoLiquidableDepts,
    SolendLiquidableDepts,
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

AnyProtocolModel = (
    Type[MangoLiquidableDepts]
    | Type[MarginfiLiquidableDepts]
    | Type[KaminoLiquidableDepts]
    | Type[SolendLiquidableDepts]
)

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
) -> AnyProtocolModel:
    if protocol == MARGINFI:
        return MarginfiLiquidableDepts
    if protocol == MANGO:
        return MangoLiquidableDepts
    if protocol == KAMINO:
        return KaminoLiquidableDepts
    if protocol == SOLEND:
        return SolendLiquidableDepts
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def store_liquidable_dept(df: pandas.DataFrame, protocol: Protocol, session: Session):
    """
    Stores data from a pandas DataFrame to the liquidable_depts table.

    Args:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - timestamp (int): Description of timestamp.
        - protocol (str): Description of protocol.
        - collateral_token (str): Description of collateral_token.
        - debt_token (str): Description of debt_token.
        - collateral_token_price (str): Description of collateral_token_price.
        - amount (str): Description of amount.

    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.
    """

    model = protocol_to_model(protocol)

    for _, row in df.iterrows():
        liquidable_dept = model(
            timestamp=row["timestamp"],
            protocol=row["protocol"],
            collateral_token=row["collateral_token"],
            debt_token=row["debt_token"],
            collateral_token_price=row["collateral_token_price"],
            amount=row["amount"],
        )
        session.add(liquidable_dept)
    session.commit()


def fetch_liquidable_depts(protocol: Protocol, session: Session) -> pandas.DataFrame:
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

    # Define a subquery for the maximum timestamp value
    max_timestamp_subquery = session.query(func.max(model.timestamp)).subquery()

    # Retrieve entries from the loan_states table where timestamp equals the maximum timestamp value
    query_result = session.query(model).filter(model.timestamp == max_timestamp_subquery).all()

    df = pandas.DataFrame(
        [
            {
                "timestamp": record.timestamp,
                "protocol": record.protocol,
                "collateral_token": record.collateral_token,
                "debt_token": record.debt_token,
                "collateral_token_price": record.collateral_token_price,
                "amount": record.amount,
            }
            for record in query_result
        ]
    )
    return df


def fetch_events(min_slot: int, protocol: Protocol, session: Session) -> AnyEvents:
    """
    Fetches events with the slot from the DB and returns them as a DataFrame

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


def process_events_to_liquidable_depts(
    protocol: Protocol,
    process_function: Callable[
        [AnyEvents],
        pandas.DataFrame,
    ],
    session: Session,
):
    current_liquidable_depts = fetch_liquidable_depts(protocol, session)
    min_slot = 0

    if len(current_liquidable_depts) > 0:
        min_slot = int(current_liquidable_depts.iloc[0]["slot"])

    events: AnyEvents = fetch_events(min_slot, protocol, session)

    new_liquidable_dept = process_function(events)

    store_liquidable_dept(new_liquidable_dept, protocol, session)


def process_events_continuously(protocol: Protocol):
    logging.info("Starting events to liquidable_depts processing.")
    session = get_db_session()

    process_func = protocol_to_process_func(protocol)

    while True:
        process_events_to_liquidable_depts(protocol, process_func, session)
        logging.info("Updated liquidable_depts.")
        time.sleep(120)
