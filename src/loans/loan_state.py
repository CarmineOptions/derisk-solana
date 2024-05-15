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
    MangoParsedTransactions,
    MarginfiParsedTransactions,
    KaminoParsedTransactions,
    SolendParsedTransactions,
    get_db_session,
)
import src.loans.kamino
import src.loans.marginfi
import src.loans.mango
import src.loans.solend




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
    Type[MangoLoanStates]
    | Type[MarginfiLoanStates]
    | Type[KaminoLoanStates]
    | Type[SolendLoanStates]
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



# TODO: these are redundant
def process_mango_events(events: list[MangoParsedTransactions]) -> pandas.DataFrame:
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


def protocol_to_model(
    protocol: Protocol,
) -> AnyProtocolModel:
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

    model = protocol_to_model(protocol)

    # Define a subquery for the maximum slot per user.
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
    )

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
    protocol_class: Callable[
        [AnyEvents],
        pandas.DataFrame,
    ],
    session: sqlalchemy.orm.session.Session,
):
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
            'user': [user for user in state.loan_entities],
            'collateral': [{token: float(amount) for token, amount in loan.collateral.items()} for loan in state.loan_entities.values()],
            'debt': [{token: float(amount) for token, amount in loan.debt.items()} for loan in state.loan_entities.values()],
        }
    )

    if state.last_slot > min_slot:
        new_loan_states_wide = widen_loan_states(new_loan_states)
        current_loan_states_wide = widen_loan_states(current_loan_states)
        COLUMNS = ['protocol', 'user', 'collateral_keys', 'collateral_values', 'debt_keys', 'debt_values']
        changed_loan_states_users = pandas.concat(
            [
                new_loan_states_wide[COLUMNS],
                current_loan_states_wide[COLUMNS],
            ],
        ).drop_duplicates(keep=False)['user'].unique()
        changed_loan_states = new_loan_states[new_loan_states['user'].isin(changed_loan_states_users)]
        store_loan_states(changed_loan_states, protocol, session)


def process_events_continuously(protocol: Protocol):
    logging.info("Starting events to loan states processing.")
    session = get_db_session()

    protocol_class = protocol_to_protocol_class(protocol)

    while True:
        start_time = time.time()
        process_events_to_loan_states(protocol, protocol_class, session)
        logging.info("Updated loan states.")
        processing_time = time.time() - start_time
        time.sleep(max(0, 900 - processing_time))
