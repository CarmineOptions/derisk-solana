from typing import Callable, Literal, Type, TypeVar
import logging
import time

import pandas
import sqlalchemy
import sqlalchemy.orm.session

from db import (
    MangoLoanStates,
    MarginfiLoanStates,
    KaminoLoanStates,
    SolendLoanStates,
    MangoParsedEvents,
    MarginfiParsedTransactionsV2,
    KaminoParsedTransactionsV2,
    SolendParsedTransactions,
    get_db_session,
    MangoLoanStatesEA, SolendLoanStatesEA, KaminoLoanStatesEA, MarginfiLoanStatesEA, SCHEMA_LENDERS
)
import src.loans.kamino
import src.loans.marginfi
import src.loans.mango
import src.loans.solend


LOGGER = logging.getLogger(__name__)


MARGINFI = "marginfi"
MANGO = "mango"
KAMINO = "kamino"
SOLEND = "solend"

Protocol = Literal["marginfi", "mango", "kamino", "solend"]
AnyEvents = list[
    MangoParsedEvents
    | MarginfiParsedTransactionsV2
    | KaminoParsedTransactionsV2
    | SolendParsedTransactions
]

AnyProtocolModel = (
    Type[MangoLoanStates]
    | Type[MarginfiLoanStates]
    | Type[KaminoLoanStates]
    | Type[SolendLoanStates]
    | Type[MangoLoanStatesEA]
    | Type[MarginfiLoanStatesEA]
    | Type[KaminoLoanStatesEA]
    | Type[SolendLoanStatesEA]
)

TypeMarginfi = TypeVar("TypeMarginfi", bound=MarginfiParsedTransactionsV2)
TypeMango = TypeVar("TypeMango", bound=MangoParsedEvents)
TypeKamino = TypeVar("TypeKamino", bound=KaminoParsedTransactionsV2)
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


# TODO: these are redundant
def process_mango_events(events: list[MangoParsedEvents]) -> pandas.DataFrame:
    # TODO: process mango events
    print(events)

    return pandas.DataFrame()


def process_solend_events(events: list[SolendParsedTransactions]) -> pandas.DataFrame:
    # TODO: process solend events
    print(events)

    return pandas.DataFrame()


def protocol_to_protocol_class(
    protocol: Protocol,
) -> ProtocolFunc:
    if protocol == MARGINFI:
        return src.loans.marginfi.MarginFiState
    if protocol == KAMINO:
        return src.loans.kamino.KaminoState
    if protocol == MANGO:
        return src.loans.mango.MangoState
    if protocol == SOLEND:
        return src.loans.solend.SolendState
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def protocol_to_model(protocol: Protocol) -> AnyProtocolModel:
    if protocol == MARGINFI:
        return MarginfiLoanStates, MarginfiLoanStatesEA
    if protocol == MANGO:
        return MangoLoanStates, MangoLoanStatesEA
    if protocol == KAMINO:
        return KaminoLoanStates, KaminoLoanStatesEA
    if protocol == SOLEND:
        return SolendLoanStates, SolendLoanStatesEA
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def widen_loan_states(loan_states: pandas.DataFrame) -> pandas.DataFrame:
    if loan_states.empty:
        return pandas.DataFrame(
            columns=['protocol', 'slot', 'user', 'collateral_keys', 'collateral_values', 'debt_keys', 'debt_values'],
        )
    loan_states = loan_states.copy()
    for column in ['collateral', 'debt']:
        loan_states[f'{column}_keys'] = loan_states[column].apply(lambda x: tuple(sorted(x.keys())))
        loan_states[f'{column}_values'] = loan_states[column].apply(lambda x: tuple(sorted(x.values())))
    loan_states.drop(columns = ['collateral', 'debt'], inplace = True)
    return loan_states


def store_loan_states(df: pandas.DataFrame, protocol: Protocol, session: sqlalchemy.orm.session.Session):
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

    model, _ = protocol_to_model(protocol)

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


def store_loan_states_for_easy_access(df: pandas.DataFrame, protocol: Protocol) -> str:
    """
    Stores data from a pandas DataFrame to the loan_states_easy_access table.

    """
    _, model = protocol_to_model(protocol)
    with get_db_session() as session:
        table_name = model.__tablename__
        assert table_name.endswith('easy_access'), f"Wrong table type is collected." \
                                                   f" *_easy_access expected, got {table_name}"
        session.execute(sqlalchemy.text(f"TRUNCATE TABLE {SCHEMA_LENDERS}.{table_name};"))
        LOGGER.info(f"{table_name} is truncated, but the change was not commited yet.")
        # Prepare data for bulk insert
        data_to_insert = [
            model(
                slot= row["slot"],
                protocol=row["protocol"],
                user=row["user"],
                collateral=row["collateral"],
                debt=row["debt"]
            )
            for _, row in df.iterrows()
        ]

        # Insert new data using bulk_insert_mappings for efficiency
        session.add_all(data_to_insert)
        session.commit()
        LOGGER.info(f"Loan states have been successfully updated in {table_name}")
    return table_name


def fetch_loan_states(protocol: Protocol, session: sqlalchemy.orm.session.Session) -> pandas.DataFrame:
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

    _, model = protocol_to_model(protocol)

    # For each user, query the loan state with tha maximum slot.
    query_result = session.query(model)

    return pandas.DataFrame(
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


def fetch_events(min_slot: int, protocol: Protocol, session: sqlalchemy.orm.session.Session) -> AnyEvents:
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
            session.query(MangoParsedEvents)
            .filter(MangoParsedEvents.block > min_slot)
            .all()
        )
    if protocol == "marginfi":
        return (
            session.query(MarginfiParsedTransactionsV2)
            .filter(MarginfiParsedTransactionsV2.block > min_slot)
            .all()
        )
    if protocol == "kamino":
        return (
            session.query(KaminoParsedTransactionsV2)
            .filter(KaminoParsedTransactionsV2.block > min_slot)
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
    protocol_class: Callable[
        [AnyEvents],
        pandas.DataFrame,
    ]
):
    with get_db_session() as session:
        current_loan_states = fetch_loan_states(protocol, session)
    min_slot = 0

    if len(current_loan_states) > 0:
        min_slot = int(current_loan_states.iloc[0]["slot"])

    state = protocol_class(
        verbose_users={},
        # TODO: switch back when the issues are solved
        # initial_loan_states=current_loan_states,
    )
    state.get_unprocessed_events()
    logging.info('The number of unprocessed events = {} for protocol = {}.'.format(len(state.unprocessed_events), protocol))
    state.process_unprocessed_events()
    logging.info('The number of loan entities = {} for protocol = {}.'.format(len(state.loan_entities), protocol))
    new_loan_states = pandas.DataFrame(
        {
            'protocol': [state.protocol for _ in state.loan_entities.keys()],
            'slot': [state.last_slot for _ in state.loan_entities.keys()],
            'user': list(state.loan_entities),
            'collateral': [
                {token: float(amount) for token, amount in loan.collateral.items()}
                for loan in state.loan_entities.values()
            ],
            'debt': [{token: float(amount) for token, amount in loan.debt.items()} for loan in state.loan_entities.values()],
        }
    )
    easy_access_table_name = store_loan_states_for_easy_access(new_loan_states, protocol)
    logging.info(f"New loan states are available in {easy_access_table_name}")

    if state.last_slot > min_slot:
        new_loan_states_wide = widen_loan_states(new_loan_states)
        current_loan_states_wide = widen_loan_states(current_loan_states)
        columns = ['protocol', 'user', 'collateral_keys', 'collateral_values', 'debt_keys', 'debt_values']
        changed_loan_states_users = pandas.concat(
            [
                new_loan_states_wide[columns],
                current_loan_states_wide[columns],
            ],
        ).drop_duplicates(keep=False)['user'].unique()
        changed_loan_states = new_loan_states[new_loan_states['user'].isin(changed_loan_states_users)]
        with get_db_session() as session:
            store_loan_states(changed_loan_states, protocol, session)


def process_events_continuously(protocol: Protocol):
    logging.info("Starting events to loan states processing.")

    protocol_class = protocol_to_protocol_class(protocol)

    while True:
        start_time = time.time()
        process_events_to_loan_states(protocol, protocol_class)
        logging.info("Updated loan states.")
        processing_time = time.time() - start_time
        time.sleep(max(0, 900 - processing_time))
