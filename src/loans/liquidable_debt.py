import decimal
import itertools
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
    MangoLiquidableDebts,
    MarginfiLiquidableDebts,
    KaminoLiquidableDebts,
    SolendLiquidableDebts,
    get_db_session,
)
import src.kamino_vault_map
import src.loans.kamino
import src.loans.loan_state
import src.prices
import src.protocols
import src.visualizations.main_chart
import src.protocols.dexes.amms.utils
import src.loans.mango
import src.mango_token_params_map

from warnings import simplefilter
simplefilter(action="ignore", category=pandas.errors.PerformanceWarning)


MARGINFI = "marginfi"
MANGO = "mango"
KAMINO = "kamino"
SOLEND = "solend"

Protocol = Literal["marginfi", "mango", "kamino", "solend"]
AnyLoanState = list[
    MangoLoanStates,
    MarginfiLoanStates,
    KaminoLoanStates,
    SolendLoanStates,
]

AnyProtocolModel = (
    Type[MangoLiquidableDebts]
    | Type[MarginfiLiquidableDebts]
    | Type[KaminoLiquidableDebts]
    | Type[SolendLiquidableDebts]
)

TypeMarginfi = TypeVar("TypeMarginfi", bound=MarginfiLoanStates)
TypeMango = TypeVar("TypeMango", bound=MangoLoanStates)
TypeKamino = TypeVar("TypeKamino", bound=KaminoLoanStates)
TypeSolend = TypeVar("TypeSolend", bound=SolendLoanStates)

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


def process_marginfi_loan_states(
    loan_states: list[MarginfiLoanStates],
) -> pandas.DataFrame:
    # TODO: process marginfi loan_states
    print(f"processing {len(loan_states)} Marginfi loan states")

    return pandas.DataFrame()


def process_mango_loan_states(loan_states: pandas.DataFrame) -> pandas.DataFrame:
    print(f"processing {len(loan_states)} mango loan states")
    protocol = 'mango'
    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}

    for collateral_token in collateral_tokens:
        loan_states[f'collateral_{collateral_token}'] = (
            loan_states['collateral'].apply(lambda x: x[collateral_token] if collateral_token in x else decimal.Decimal('0'))
    )
    for debt_token in debt_tokens:
        loan_states[f'debt_{debt_token}'] = (
            loan_states['debt'].apply(lambda x: x[debt_token] if debt_token in x else decimal.Decimal('0'))
        )

    underlying_collateral_tokens: set = collateral_tokens
    underlying_debt_tokens: set = debt_tokens

    token_prices = src.prices.get_prices_for_tokens(list(underlying_collateral_tokens | underlying_debt_tokens))
    token_parameters = src.mango_token_params_map.token_parameters
    tokens_info = src.protocols.dexes.amms.utils.get_tokens_address_to_info_map()


    for collateral_token in collateral_tokens:

        if not token_parameters.get(collateral_token):
            print(f'No token parameters found for {collateral_token}')
            continue
        if not tokens_info.get(collateral_token):
            print(f'No token info found for {collateral_token}')
            continue
        if not tokens_info[collateral_token].get('decimals'):
            print(f'No decimals found for {collateral_token}')
            continue

        decimals = tokens_info[collateral_token]['decimals']
        asset_maint_w = token_parameters[collateral_token]['maint_asset_weight']
        loan_states[f'collateral_usd_{collateral_token}'] = (
            loan_states[f'collateral_{collateral_token}'].astype(float)
            / (10**decimals)
            * float(asset_maint_w)
            * token_prices[collateral_token]
        )

    for debt_token in debt_tokens:

        if not token_parameters.get(debt_token):
            print(f'No token parameters found for {debt_token}')
            continue
        if not tokens_info.get(debt_token):
            print(f'No token info found for {debt_token}')
            continue
        if not tokens_info[debt_token].get('decimals'):
            print(f'No decimals found for {debt_token}')
            continue
        
        decimals = tokens_info[debt_token]['decimals']
        liab_maint_w = token_parameters[debt_token]['maint_liab_weight']
        loan_states[f'debt_usd_{debt_token}'] = (
            loan_states[f'debt_{debt_token}'].astype(float)
            / (10**decimals)
            * float(liab_maint_w)
            * token_prices[debt_token]
        )
        
    all_data = []

    for collateral_token, debt_token in itertools.product(collateral_tokens, debt_tokens):
        if collateral_token == debt_token:
            continue

        logging.info(
            'Computing liquidable debt for protocol = {}, collateral token = {} and debt token = {}.'.format(
                protocol,
                collateral_token,
                debt_token,
            )
        )
        collateral_token_price = token_prices[collateral_token]
        
        data = pandas.DataFrame(
            {
                "collateral_token_price": src.visualizations.main_chart.get_token_range(collateral_token_price),
            }
        )
        liquidable_debt = data['collateral_token_price'].apply(
            lambda x: src.loans.mango.compute_liquidable_debt_at_price(
                loan_states = loan_states.copy(),
                token_prices = token_prices,
                collateral_token = collateral_token,
                target_collateral_token_price = x,
                debt_token = debt_token,
            )
        )
        data['amount'] = liquidable_debt.diff().abs()
        data['protocol'] = protocol
        data['slot'] = loan_states['slot'].max()
        data['collateral_token'] = collateral_token
        data['debt_token'] = debt_token
        data = data.dropna()
        
        all_data.append(data)
        
    return pandas.concat(all_data)

def process_kamino_loan_states(loan_states: list[KaminoLoanStates]) -> pandas.DataFrame:
    PROTOCOL = 'kamino'
    logging.info("Processing = {} loan states for protocol = {}.".format(len(loan_states), PROTOCOL))

    # Get mappings between mint and LP tokens and mint and supply vaults.
    MINT_TO_LP_MAPPING = {x: [] for x in src.kamino_vault_map.lp_to_mint_map.values()}
    for x, y in src.kamino_vault_map.lp_to_mint_map.items():
        MINT_TO_LP_MAPPING[y].append(x)
    MINT_TO_SUPPLY_MAPPING = {x: [] for x in src.kamino_vault_map.supply_vault_to_mint_map.values()}
    for x, y in src.kamino_vault_map.supply_vault_to_mint_map.items():
        MINT_TO_SUPPLY_MAPPING[y].append(x)

    # Extract a set of collateral and debt tokens used.
    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}

    # Get underlying token prices.
    underlying_collateral_tokens = [
        src.kamino_vault_map.lp_to_mint_map[x]
        for x in collateral_tokens
        if x in src.kamino_vault_map.lp_to_mint_map
    ]
    underlying_debt_tokens = [
        src.kamino_vault_map.supply_vault_to_mint_map[x]
        for x in debt_tokens
        if x in src.kamino_vault_map.supply_vault_to_mint_map
    ]
    token_prices = src.prices.get_prices_for_tokens(underlying_collateral_tokens + underlying_debt_tokens)

    # Get token parameters.
    collateral_token_parameters = {
        token: src.kamino_vault_map.lp_to_info_map.get(token, None)
        for token
        in collateral_tokens
    }
    debt_token_parameters = {
        debt_token: src.kamino_vault_map.supply_to_info_map.get(debt_token, None)
        for debt_token
        in debt_tokens
    }

    # Put collateral and debt token holdings into the loan states df.
    for token in collateral_tokens:
        loan_states[f'collateral_{token}'] = loan_states['collateral'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )
    for token in debt_tokens:
        loan_states[f'debt_{token}'] = loan_states['debt'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )

    # Compute the USD value of collateral and debt token holdings.
    for token in collateral_tokens:
        if not collateral_token_parameters[token]:
            continue
        if not collateral_token_parameters[token]['underlying_decs']:
            continue
        decimals = collateral_token_parameters[token]['underlying_decs']
        ltv = collateral_token_parameters[token]['ltv']
        underlying_token = src.kamino_vault_map.lp_to_mint_map[token]
        loan_states[f'collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}'].astype(float)
            / (10**decimals)
            * (ltv/100)
            * token_prices[underlying_token]
        )
    for debt_token in debt_tokens:
        if not debt_token_parameters[debt_token]:
            continue
        if not debt_token_parameters[debt_token]['underlying_decs']:
            continue
        decimals = debt_token_parameters[debt_token]['underlying_decs']
        ltv = debt_token_parameters[debt_token]['ltv']
        underlying_token = src.kamino_vault_map.supply_vault_to_mint_map[debt_token]
        loan_states[f'debt_usd_{debt_token}'] = (
            loan_states[f'debt_{debt_token}'].astype(float)
            / (10**decimals)
            * (1/(ltv/100) if ltv else 1)
            * token_prices[underlying_token]
        )

    # These contain the underlying token addresses.
    COLLATERAL_TOKENS = {
        src.kamino_vault_map.lp_to_mint_map[x]
        for x in collateral_tokens
        if x in src.kamino_vault_map.lp_to_mint_map
    }
    DEBT_TOKENS = {
        src.kamino_vault_map.supply_vault_to_mint_map[x]
        for x in debt_tokens
        if x in src.kamino_vault_map.supply_vault_to_mint_map
    }

    all_data = pandas.DataFrame()
    for collateral_token, debt_token in itertools.product(COLLATERAL_TOKENS, DEBT_TOKENS):
        if collateral_token == debt_token:
            continue

        logging.info(
            'Computing liquidable debt for protocol = {}, collateral token = {} and debt token = {}.'.format(
                PROTOCOL,
                collateral_token,
                debt_token,
            )
        )

        collateral_token_price = token_prices[collateral_token]
        # The price is usually not found for unused tokens.
        if not collateral_token_price:
            return

        # Compute liqidable debt.
        data = pandas.DataFrame(
            {
                "collateral_token_price": src.visualizations.main_chart.get_token_range(collateral_token_price),
            }
        )
        liquidable_debt = data['collateral_token_price'].apply(
            lambda x: src.loans.kamino.compute_liquidable_debt_at_price(
                loan_states = loan_states.copy(),
                token_prices = token_prices,
                debt_token_parameters = debt_token_parameters,
                mint_to_lp_map=MINT_TO_LP_MAPPING,
                mint_to_supply_map=MINT_TO_SUPPLY_MAPPING,
                collateral_token = collateral_token,
                target_collateral_token_price = x,
                debt_token = debt_token,
            )
        )
        data['amount'] = liquidable_debt.diff().abs()
        data['protocol'] = PROTOCOL
        data['slot'] = loan_states['slot'].max()
        data['collateral_token'] = collateral_token
        data['debt_token'] = debt_token
        data.dropna(inplace = True)
        all_data = pandas.concat([all_data, data])
    return all_data


def process_solend_loan_states(loan_states: list[SolendLoanStates]) -> pandas.DataFrame:
    # TODO: process solend loan_states
    print(f"processing {len(loan_states)} Solend loan states", flush=True)

    return pandas.DataFrame()


def protocol_to_process_func(
    protocol: Protocol,
) -> ProtocolFunc:
    if protocol == MARGINFI:
        return process_marginfi_loan_states
    if protocol == MANGO:
        return process_mango_loan_states
    if protocol == KAMINO:
        return process_kamino_loan_states
    if protocol == SOLEND:
        return process_solend_loan_states
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def protocol_to_model(
    protocol: Protocol,
) -> AnyProtocolModel:
    if protocol == MARGINFI:
        return MarginfiLiquidableDebts
    if protocol == MANGO:
        return MangoLiquidableDebts
    if protocol == KAMINO:
        return KaminoLiquidableDebts
    if protocol == SOLEND:
        return SolendLiquidableDebts
    # Unreachable
    raise ValueError(f"invalid protocol {protocol}")


def store_liquidable_debts(df: pandas.DataFrame, protocol: Protocol, session: Session):
    """
    Stores data from a pandas DataFrame to the liquidable_debts table.

    Args:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - protocol (str): Description of protocol.
        - collateral_token (str): Description of collateral_token.
        - debt_token (str): Description of debt_token.
        - collateral_token_price (str): Description of collateral_token_price.
        - amount (str): Description of amount.

    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.
    """

    model = protocol_to_model(protocol)

    for _, row in df.iterrows():
        liquidable_debts = model(
            slot=row["slot"],
            protocol=row["protocol"],
            collateral_token=row["collateral_token"],
            debt_token=row["debt_token"],
            collateral_token_price=row["collateral_token_price"],
            amount=row["amount"],
        )
        session.add(liquidable_debts)
    session.commit()


def fetch_liquidable_debts(protocol: Protocol, session: Session) -> pandas.DataFrame:
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

    try:
        # Retrieve entries from the loan_states table where slot equals the maximum slot value
        query_result = (
            session.query(model).filter(model.slot == max_slot_subquery).all()
        )
    except:
        query_result = []

    df = pandas.DataFrame(
        [
            {
                "slot": record.slot,
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


def process_loan_states_to_liquidable_debts(
    protocol: Protocol,
    process_function: Callable[
        [AnyLoanState],
        pandas.DataFrame,
    ],
    session: Session,
):
    current_liquidable_debts = fetch_liquidable_debts(protocol, session)
    current_liquidable_debts_slot = 0
    if len(current_liquidable_debts) > 0:
        current_liquidable_debts_slot = int(current_liquidable_debts.iloc[0]["slot"])

    current_loan_states: AnyLoanState = src.loans.loan_state.fetch_loan_states(protocol, session)
    current_loan_states_slot = 0
    if len(current_liquidable_debts) > 0:
        current_loan_states_slot = int(current_loan_states.iloc[0]["slot"])

    if not current_liquidable_debts_slot or current_liquidable_debts_slot < current_loan_states_slot:
        new_liquidable_debts = process_function(current_loan_states)
        store_liquidable_debts(new_liquidable_debts, protocol, session)


def process_loan_states_continuously(protocol: Protocol):
    logging.info("Starting loan states to liquidable_debts processing.")
    session = get_db_session()

    process_func = protocol_to_process_func(protocol)

    while True:
        process_loan_states_to_liquidable_debts(protocol, process_func, session)
        logging.info("Updated liquidable_debts.")
        time.sleep(120)
