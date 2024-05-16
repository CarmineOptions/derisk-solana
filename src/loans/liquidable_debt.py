from typing import Callable, Literal, Type, TypeVar
import asyncio
import dataclasses
import decimal
import itertools
import logging
import os
import time
import traceback
import warnings

import numpy
import pandas
import solana.rpc.async_api
import solders.pubkey
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from src.loans.solend import compute_liquidable_debt_for_price_target
from src.visualizations.main_chart import get_token_range
from db import (
    MangoLoanStates,
    MarginfiLoanStates,
    KaminoLoanStates,
    SolendLoanStates,
    MarginfiHealthRatio,
    MangoLiquidableDebts,
    MarginfiLiquidableDebts,
    KaminoLiquidableDebts,
    SolendLiquidableDebts,
    get_db_session,
)
import src.kamino_vault_map
import src.loans.helpers
import src.loans.kamino
import src.loans.loan_state
import src.marginfi_map
import src.prices
import src.protocols
import src.protocols.dexes.amms.utils
import src.loans.mango
import src.mango_token_params_map



warnings.simplefilter(action="ignore", category=pandas.errors.PerformanceWarning)

# Ignore all warnings
warnings.filterwarnings('ignore')

# logger
LOGGER = logging.getLogger(__name__)

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


@dataclasses.dataclass
class TokenParameters:
    underlying: str
    decimals: int
    interest_rate_model: float
    factor: float


async def get_bank(
    client: solana.rpc.async_api.AsyncClient,
    token: str,
) -> src.protocols.anchor_clients.marginfi_client.accounts.Bank:
    try:
        return await src.protocols.anchor_clients.marginfi_client.accounts.Bank.fetch(
            client,
            solders.pubkey.Pubkey.from_string(token),
        )
    except solana.exceptions.SolanaRpcException:
        time.sleep(1)
        return await get_bank(client = client, token = token)


async def process_marginfi_loan_states(
    loan_states: pandas.DataFrame,
    previous_health_ratios: pandas.DataFrame,
) -> None:
    PROTOCOL = 'marginfi'
    logging.info("Processing = {} loan states for protocol = {}.".format(len(loan_states), PROTOCOL))

    # Extract a set of collateral and debt tokens used.
    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}

    AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
    if AUTHENTICATED_RPC_URL is None:
        raise ValueError("no AUTHENTICATED_RPC_URL env var")

    client = solana.rpc.async_api.AsyncClient(AUTHENTICATED_RPC_URL)

    # Get token parameters.
    collateral_token_parameters = {
        token: None
        for collateral in loan_states['collateral']
        for token in collateral
    }
    for token in collateral_token_parameters:
        bank = await get_bank(client = client, token = token)
        collateral_token_parameters[token] = TokenParameters(
            underlying = str(bank.mint),
            decimals = int(bank.mint_decimals),
            interest_rate_model = float(bank.asset_share_value.value / 2**48),
            factor = float(bank.config.asset_weight_maint.value / 2**48),
        )
    debt_token_parameters = {
        token: None
        for debt in loan_states['debt']
        for token in debt
    }
    for token in debt_token_parameters:
        bank = await get_bank(client = client, token = token)
        debt_token_parameters[token] = TokenParameters(
            underlying = str(bank.mint),
            decimals = int(bank.mint_decimals),
            interest_rate_model = float(bank.liability_share_value.value / 2**48),
            factor = float(bank.config.liability_weight_maint.value / 2**48),
        )

    # Get underlying token prices.
    underlying_collateral_tokens = [x.underlying for x in collateral_token_parameters.values()]
    underlying_debt_tokens = [x.underlying for x in debt_token_parameters.values()]
    all_underlying_tokens = underlying_collateral_tokens + underlying_debt_tokens
    token_prices = src.prices.get_prices_for_tokens(all_underlying_tokens)

    underlying_to_bank_mapping = {underlying: set() for underlying in all_underlying_tokens}
    for bank, parameters in collateral_token_parameters.items():
        underlying_to_bank_mapping[parameters.underlying].add(bank)
    for bank, parameters in debt_token_parameters.items():
        underlying_to_bank_mapping[parameters.underlying].add(bank)

    # Put collateral and debt token holdings into the loan states df.
    for token in collateral_tokens:
        loan_states[f'collateral_{token}'] = loan_states['collateral'].apply(lambda x: x.get(token, 0.0))
    for token in debt_tokens:
        loan_states[f'debt_{token}'] = loan_states['debt'].apply(lambda x: x.get(token, 0.0))

    # Compute the USD value of collateral and debt token holdings.
    for token in collateral_tokens:
        loan_states[f'collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}']
            / (10**collateral_token_parameters[token].decimals)
            * collateral_token_parameters[token].interest_rate_model
            * token_prices[collateral_token_parameters[token].underlying]
        )
    collateral_columns = [x for x in loan_states.columns if 'collateral_usd_' in x]
    loan_states['collateral_usd'] = loan_states[collateral_columns].sum(axis = 1)
    for token in collateral_tokens:
        loan_states[f'risk_adjusted_collateral_usd_{token}'] = (
            loan_states[f'collateral_usd_{token}']
            * collateral_token_parameters[token].factor
        )
    risk_adjusted_collateral_columns = [x for x in loan_states.columns if 'risk_adjusted_collateral_usd_' in x]
    loan_states['risk_adjusted_collateral_usd'] = loan_states[risk_adjusted_collateral_columns].sum(axis = 1)
    for token in debt_tokens:
        loan_states[f'debt_usd_{token}'] = (
            loan_states[f'debt_{token}'].astype(float)
            / (10**debt_token_parameters[token].decimals)
            * debt_token_parameters[token].interest_rate_model
            * token_prices[debt_token_parameters[token].underlying]
        )
    debt_columns = [x for x in loan_states.columns if 'debt_usd_' in x]
    loan_states['debt_usd'] = loan_states[debt_columns].sum(axis = 1)
    for token in debt_tokens:    
        loan_states[f'risk_adjusted_debt_usd_{token}'] = (
            loan_states[f'debt_usd_{token}']
            * debt_token_parameters[token].factor
        )
    risk_adjusted_debt_columns = [x for x in loan_states.columns if 'risk_adjusted_debt_usd_' in x]
    loan_states['risk_adjusted_debt_usd'] = loan_states[risk_adjusted_debt_columns].sum(axis = 1)

    # Compute health ratios.
    loan_states['health_factor'] = (
        loan_states['risk_adjusted_collateral_usd'] - loan_states['risk_adjusted_debt_usd']
    ) / loan_states['risk_adjusted_collateral_usd']
    loan_states['std_health_factor'] = (
        loan_states['risk_adjusted_collateral_usd'] / loan_states['risk_adjusted_debt_usd']
    )

    # Prepare health ratio data.
    health_ratios = loan_states[['protocol', 'user']].copy()
    timestamp = time.time()
    health_ratios['slot'] = timestamp
    health_ratios['timestamp'] = timestamp
    health_ratios['last_update'] = timestamp
    health_ratios['collateral'] = loan_states['collateral_usd'].round(5)
    health_ratios['risk_adjusted_collateral'] = loan_states['risk_adjusted_collateral_usd'].round(5)
    health_ratios['debt'] = loan_states['debt_usd'].round(5)
    health_ratios['risk_adjusted_debt'] = loan_states['risk_adjusted_debt_usd'].round(5)
    health_ratios['health_factor'] = loan_states['health_factor'].round(5)
    health_ratios['std_health_factor'] = loan_states['std_health_factor'].round(5)

    # Save health ratios to the database.
    with get_db_session() as session:
        if previous_health_ratios.empty:
            changed_health_ratios = health_ratios
        else:
            health_ratios.set_index('user', inplace = True)
            previous_health_ratios.set_index('user', inplace = True)
            health_ratios['previous_std_health_factor'] = previous_health_ratios['std_health_factor'].astype(float)
            health_ratios['health_factor_relative_change'] = (
                health_ratios['std_health_factor']
                / health_ratios['previous_std_health_factor']
            ).fillna(numpy.inf)
            changed_health_ratios = health_ratios[
                (
                    (health_ratios['std_health_factor'] >= 1.2)
                    & (health_ratios['health_factor_relative_change'] >= 1.01)
                ) | (
                    (health_ratios['std_health_factor'] < 1.2)
                    & (health_ratios['health_factor_relative_change'] >= 1.0025)
                )
            ]
            changed_health_ratios.drop(
                columns=['previous_std_health_factor', 'health_factor_relative_change'],
                inplace = True,
            )
            changed_health_ratios.reset_index(drop = False, inplace = True)
        store_marginfi_health_ratios(changed_health_ratios, PROTOCOL, session)

    for collateral_token, debt_token in itertools.product(underlying_collateral_tokens, underlying_debt_tokens):
        if collateral_token == debt_token:
            continue

        collateral_banks = underlying_to_bank_mapping[collateral_token]
        debt_banks = underlying_to_bank_mapping[debt_token]
        collateral_usd_columns = [f'collateral_usd_{x}' for x in collateral_banks]
        debt_usd_columns = [f'debt_usd_{x}' for x in debt_banks]
        if not (loan_states[collateral_usd_columns].sum(axis = 1) * loan_states[debt_usd_columns].sum(axis = 1)).sum():
            continue

        logging.info(
            'Computing liquidable debt for protocol = {}, collateral token = {} and debt token = {}.'.format(
                PROTOCOL,
                collateral_token,
                debt_token,
            )
        )

        collateral_token_price = token_prices[collateral_token]

        # Compute liqidable debt.
        liquidable_debts = pandas.DataFrame(
            {
                "collateral_token_price": src.visualizations.main_chart.get_token_range(collateral_token_price),
            }
        )

        collateral_token_columns = [
            f'collateral_{x}'
            for x in underlying_to_bank_mapping[collateral_token]
        ]
        debt_token_columns = [
            f'debt_{x}'
            for x in underlying_to_bank_mapping[debt_token]
        ]
        relevant_loan_states = loan_states[
            loan_states[collateral_token_columns].sum(axis = 1).astype(bool)
            & loan_states[debt_token_columns].sum(axis = 1).astype(bool)
        ]

        liquidable_debt = liquidable_debts['collateral_token_price'].apply(
            lambda x: src.loans.marginfi.compute_liquidable_debt_at_price(
                loan_states = relevant_loan_states.copy(),
                token_prices = token_prices,
                underlying_to_bank_mapping=underlying_to_bank_mapping,
                underlying_collateral = collateral_token,
                target_underlying_collateral_price = x,
                underlying_debt = debt_token,
            )
        )
        liquidable_debts['amount'] = liquidable_debt.diff().abs()
        liquidable_debts['protocol'] = PROTOCOL
        liquidable_debts['slot'] = loan_states['slot'].max()
        liquidable_debts['collateral_token'] = collateral_token
        liquidable_debts['debt_token'] = debt_token
        liquidable_debts.dropna(inplace = True)
        with get_db_session() as session:
            store_liquidable_debts(liquidable_debts, PROTOCOL, session)


def process_mango_loan_states(loan_states: pandas.DataFrame) -> pandas.DataFrame:
    logging.info(f"processing {len(loan_states)} mango loan states.")
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
    token_parameters = src.mango_token_params_map.get_mango_token_params_map()
    tokens_info = src.protocols.dexes.amms.utils.get_tokens_address_to_info_map()


    for collateral_token in collateral_tokens:
        if not token_parameters.get(collateral_token):
            logging.info(f'No token parameters found for {collateral_token}')
            continue
        if not tokens_info.get(collateral_token):
            logging.info(f'No token info found for {collateral_token}')
            continue
        if not tokens_info[collateral_token].get('decimals'):
            logging.info(f'No decimals found for {collateral_token}')
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
            logging.info(f'No token parameters found for {debt_token}')
            continue
        if not tokens_info.get(debt_token):
            logging.info(f'No token info found for {debt_token}')
            continue
        if not tokens_info[debt_token].get('decimals'):
            logging.info(f'No decimals found for {debt_token}')
            continue
        
        decimals = tokens_info[debt_token]['decimals']
        liab_maint_w = token_parameters[debt_token]['maint_liab_weight']
        loan_states[f'debt_usd_{debt_token}'] = (
            loan_states[f'debt_{debt_token}'].astype(float)
            / (10**decimals)
            * float(liab_maint_w)
            * token_prices[debt_token]
        )

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
        with get_db_session() as session:
            store_liquidable_debts(data, "mango", session)


def process_kamino_loan_states(loan_states: list[KaminoLoanStates]) -> pandas.DataFrame:
    logging.info(f"processing {len(loan_states)} Solend loan states")
    # Create SolendState instance with current loan states.
    state = src.loans.kamino.KaminoState(initial_loan_states=loan_states)
    # get all present collateral/debt token pairs
    relevant_pairs = state.find_relevant_debt_collateral_pairs()
    # get all collateral and debt mints that at least once appears within current loan states.
    collateral_mints, debt_mints = state.get_all_unique_mints()
    # build dataframe of loan states with flattened positions (debt and collateral)
    # number of new columns equals to 'len(collateral_mints) + len(debt_mints) + 2`
    df_new = state.loan_entities_to_df(collateral_mints, debt_mints)

    # compute liquidable debt values for all debt/collateral token pairs present in current loan states
    for (debt_token, collateral_token), params in relevant_pairs.items():
        LOGGER.info(f"Start processing {debt_token} - {collateral_token}")
        try:
            ctokens = list(params['collateral_mints'])
            users = list(params['users'])
            loan_states = df_new.loc[users].copy()
            collateral_token_price = state.get_price_for(collateral_token)

            liquidable_debt_data = pandas.DataFrame(
                {
                    "collateral_token_price": get_token_range(collateral_token_price)
                }
            )

            liquidable_debt = liquidable_debt_data['collateral_token_price'].apply(
                lambda x: src.loans.kamino.compute_liquidable_debt_for_price_target(
                    loan_states=loan_states.copy(),
                    target_price=x,
                    debt_token=debt_token,
                    collateral_mints=ctokens,
                    original_price=collateral_token_price,
                    collateral_underlying_token=collateral_token
                )
            )
            liquidable_debt_data['amount'] = liquidable_debt.diff().abs()
            liquidable_debt_data['protocol'] = 'kamino'
            liquidable_debt_data['slot'] = loan_states['slot'].max()
            liquidable_debt_data['collateral_token'] = collateral_token
            liquidable_debt_data['debt_token'] = debt_token
            liquidable_debt_data.dropna(inplace=True)
            with get_db_session() as session:
                store_liquidable_debts(liquidable_debt_data, "kamino", session)
                LOGGER.info("Liquidable debt processing for pair successfully calculated and stored.")

        except Exception as e:
            # Log the error with traceback
            LOGGER.error("An error occurred: %s", traceback.format_exc())
            continue


def process_solend_loan_states(loan_states: pandas.DataFrame) -> None:
    logging.info(f"processing {len(loan_states)} Solend loan states")
    # Create SolendState instance with current loan states.
    state = src.loans.solend.SolendState(initial_loan_states=loan_states)
    # get all present collateral/debt token pairs
    relevant_pairs = state.find_relevant_debt_collateral_pairs()
    # get all collateral and debt mints that at least once appears within current loan states.
    collateral_mints, debt_mints = state.get_all_unique_mints()
    # build dataframe of loan states with flattened positions (debt and collateral)
    # number of new columns equals to 'len(collateral_mints) + len(debt_mints) + 2`
    df_new = state.loan_entities_to_df(collateral_mints, debt_mints)

    # compute liquidable debt values for all debt/collateral token pairs present in current loan states
    for (debt_token, collateral_token), params in relevant_pairs.items():
        LOGGER.info(f"Start processing {debt_token} - {collateral_token}")
        try:
            ctokens = list(params['collateral_mints'])
            users = list(params['users'])
            loan_states = df_new.loc[users].copy()
            collateral_token_price = state.get_price_for(collateral_token)

            liquidable_debt_data = pandas.DataFrame(
                {
                    "collateral_token_price": get_token_range(collateral_token_price)
                }
            )

            liquidable_debt = liquidable_debt_data['collateral_token_price'].apply(
                lambda x: compute_liquidable_debt_for_price_target(
                    loan_states=loan_states.copy(),
                    target_price=x,
                    debt_token=debt_token,
                    collateral_mints=ctokens,
                    original_price=collateral_token_price,
                    collateral_underlying_token=collateral_token
                )
            )
            liquidable_debt_data['amount'] = liquidable_debt.diff().abs()
            liquidable_debt_data['protocol'] = 'solend'
            liquidable_debt_data['slot'] = loan_states['slot'].max()
            liquidable_debt_data['collateral_token'] = collateral_token
            liquidable_debt_data['debt_token'] = debt_token
            liquidable_debt_data.dropna(inplace=True)
            with get_db_session() as session:
                store_liquidable_debts(liquidable_debt_data, "solend", session)
                LOGGER.info("Liquidable debt processing for pair successfully calculated and stored.")

        except Exception as e:
            # Log the error with traceback
            LOGGER.error("An error occurred: %s", traceback.format_exc())
            continue


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


def store_marginfi_health_ratios(df: pandas.DataFrame, protocol: Protocol, session: Session):
    """
    Stores data from a pandas DataFrame to the health ratios table.

    Args:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - last_update (int): Time of last update.
        - timestamp (int): Time of last update.
        - protocol (str): Description of protocol.
        - user (str): Description of user.
        - health_factor (str): Health factor as defined by the protocol.
        - std_health_factor (str): Standardized health factor.
        - collateral (str): Collateral in USD.
        - risk_adjusted_collateral (str): Risk-adjusted collateral in USD.
        - debt (str): Debt in USD.
        - risk_adjusted_debt (str): Risk-adjusted debt in USD.

    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.
    """

    for _, row in df.iterrows():
        health_ratios = MarginfiHealthRatio(
            slot=row["slot"],
            last_update=row["last_update"],
            timestamp=row["timestamp"],
            protocol=row["protocol"],
            user=row["user"],
            health_factor=row["health_factor"],
            std_health_factor=row["std_health_factor"],
            collateral=row["collateral"],
            risk_adjusted_collateral=row["risk_adjusted_collateral"],
            debt=row["debt"],
            risk_adjusted_debt=row["risk_adjusted_debt"],
        )
        session.add(health_ratios)
    session.commit()


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


def fetch_marginfi_health_ratios(protocol: Protocol, session: Session) -> pandas.DataFrame:
    """
    Fetches health ratios with the max slot from the DB and returns them as a DataFrame

    Args:
    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.

    Returns:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - last_update (int): Time of last update.
        - timestamp (int): Time of last update.
        - protocol (str): Description of protocol.
        - user (str): Description of user.
        - health_factor (str): Health factor as defined by the protocol.
        - std_health_factor (str): Standardized health factor.
        - collateral (str): Collateral in USD.
        - risk_adjusted_collateral (str): Risk-adjusted collateral in USD.
        - debt (str): Debt in USD.
        - risk_adjusted_debt (str): Risk-adjusted debt in USD.
    """
    # Define a subquery for the maximum slot value
    max_slot_subquery = session.query(func.max(MarginfiHealthRatio.slot)).subquery()

    try:
        # Retrieve entries from the loan_states table where slot equals the maximum slot value
        query_result = (
            session.query(MarginfiHealthRatio).filter(MarginfiHealthRatio.slot == max_slot_subquery).all()
        )
    except:
        query_result = []

    return pandas.DataFrame(
        [
            {
                "slot": record.slot,
                "last_update": record.last_update,
                "timestamp": record.timestamp,
                "protocol": record.protocol,
                "user": record.user,
                "health_factor": record.health_factor,
                "std_health_factor": record.std_health_factor,
                "collateral": record.collateral,
                "risk_adjusted_collateral": record.risk_adjusted_collateral,
                "debt": record.debt,
                "risk_adjusted_debt": record.risk_adjusted_debt,
            }
            for record in query_result  # TODO??? sqlalchemy.exc.PendingRollbackError
        ]
    )


def fetch_liquidable_debts(protocol: Protocol, session: Session) -> pandas.DataFrame:
    """
    Fetches loan states with the max slot from the DB and returns them as a DataFrame

    Args:
    - session (sqlalchemy.orm.session.Session): A SQLAlchemy session object.

    Returns:
    - df (pandas.DataFrame): A DataFrame with the following columns:
        - slot (int): Description of slot.
        - protocol (str): Description of protocol.
        - collateral_token (str): Description of collateral_token.
        - debt_token (str): Description of debt_token.
        - collateral_token_price (str): Description of collateral_token_price.
        - amount (str): Description of amount.
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

    return pandas.DataFrame(
        [
            {
                "slot": record.slot,
                "protocol": record.protocol,
                "collateral_token": record.collateral_token,
                "debt_token": record.debt_token,
                "collateral_token_price": record.collateral_token_price,
                "amount": record.amount,
            }
            for record in query_result  # TODO??? sqlalchemy.exc.PendingRollbackError
        ]
    )


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
        current_liquidable_debts_slot = int(current_liquidable_debts["slot"].max())

    current_loan_states = src.loans.loan_state.fetch_loan_states(protocol, session)
    current_loan_states_slot = 0
    if len(current_liquidable_debts) > 0:
        current_loan_states_slot = int(current_loan_states["slot"].max())

    if not current_liquidable_debts_slot or current_liquidable_debts_slot < current_loan_states_slot:
        if protocol == MARGINFI:
            current_health_ratios = fetch_marginfi_health_ratios(protocol, session)
            asyncio.run(process_function(current_loan_states, current_health_ratios))
        else:
            process_function(current_loan_states)


def process_loan_states_continuously(protocol: Protocol):
    logging.info("Starting loan states to liquidable debts processing.")
    session = get_db_session()

    process_func = protocol_to_process_func(protocol)

    while True:
        start_time = time.time()
        process_loan_states_to_liquidable_debts(protocol, process_func, session)
        logging.info("Updated liquidable debts.")
        processing_time = time.time() - start_time
        time.sleep(max(0, 900 - processing_time))
