import traceback
import logging
import asyncio
import itertools
import time
import pandas as pd
import src.loans.state 
from decimal import Decimal
from solana.exceptions import SolanaRpcException
from solders.pubkey import Pubkey
from src.protocols.anchor_clients.mango_client.program_id import PROGRAM_ID as MANGO_ID
from solana.rpc.api import Client
import requests
import os
from solana.rpc.types import MemcmpOpts
from src.protocols.anchor_clients.mango_client.accounts.mango_account import MangoAccount
from src.prices import get_prices_for_tokens
import src.mango_token_params_map
import numpy as np

# =============================================================================================
# Helper Structs for parsing Serum orders

from construct import Bytes, Int64ul, Padding
from construct import Struct as cStruct
from construct import BitsInteger, BitsSwapped, BitStruct, Const, Flag

ACCOUNT_FLAGS_LAYOUT = BitsSwapped(  # Swap to little endian
    BitStruct(
        "initialized" / Flag,
        "market" / Flag,
        "open_orders" / Flag,
        "request_queue" / Flag,
        "event_queue" / Flag,
        "bids" / Flag,
        "asks" / Flag,
        Const(0, BitsInteger(57)),  # Padding
    )
)

OPEN_ORDERS_LAYOUT = cStruct(
    Padding(5),
    "account_flags" / ACCOUNT_FLAGS_LAYOUT,
    "market" / Bytes(32),
    "owner" / Bytes(32),
    "base_token_free" / Int64ul,
    "base_token_total" / Int64ul,
    "quote_token_free" / Int64ul,
    "quote_token_total" / Int64ul,
    "free_slot_bits" / Bytes(16),
    "is_bid_bits" / Bytes(16),
    "orders" / Bytes(16)[128],
    "client_ids" / Int64ul[128],
    "referrer_rebate_accrued" / Int64ul,
    Padding(7),
)
# =============================================================================================

def get_authenticated_rpc_url() -> str:
    authenticated_rpc_url = os.environ.get("AUTHENTICATED_RPC_URL")
    if authenticated_rpc_url is None:
        raise ValueError("No AUTHENTICATED_RPC_URL env var")
    return authenticated_rpc_url

def get_group_token_index_to_index_map():
    r = requests.get('https://api.mngo.cloud/data/v4/group-metadata')
    if r.status_code != 200:
        raise ValueError('Unable to fetch group -> token index -> mint info map')
    
    m = {}

    for group in r.json()['groups']:
        indexes = {}
        for token in group['tokens']:
            info = {
                'mint': token['mint'],
                'symbol': token['symbol'],
                'decimals': token['decimals'],
            }
            indexes[token['tokenIndex']] = info
        m[group['publicKey']] = indexes

    return m

class MangoLoanEntity(src.loans.state.LoanEntity):
    """ A class that describes the Mango loan entity. """

    def __init__(self) -> None:
        super().__init__()

class MangoState(src.loans.state.State):
    """
    A class that describes the state of all Mango loan entities.

    TODO: Currently fetches present onchain data. Rework to process events.
    
    """
    def __init__(
        self,
        verbose_users: set[str] | None = None,
        initial_loan_states: pd.DataFrame = pd.DataFrame(),
    ) -> None:
        super().__init__(
            protocol='Mango',
            loan_entity_class=MangoLoanEntity,
            verbose_users=verbose_users,
        )
        self.client = Client(get_authenticated_rpc_url())
        self.group_token_index_map = get_group_token_index_to_index_map()

    def get_groups(self) -> list[Pubkey]:
        response = requests.get('https://api.mngo.cloud/data/v4/group-metadata')
        if response.status_code != 200:
            print('MANGO: Unable to fetch groups')
            time.sleep(20)
            return self.get_groups()

        info = [i for i in response.json()['groups'] if i['name'] == 'MAINNET.0']
        return [ Pubkey.from_string(i['publicKey']) for i in info]


    def get_all_accounts_for_group(self, mango_group: Pubkey) -> list[tuple[Pubkey, MangoAccount]]:
        filters = [
            MemcmpOpts(offset = 0, bytes = 'ho5hwwEoHot'),
            MemcmpOpts(offset = 8, bytes = str(mango_group))
        ]

        try: 
            res = self.client.get_program_accounts( 
                MANGO_ID, 
                encoding='base64',
                filters=filters
            )
        except SolanaRpcException as err:
            err_msg = "".join(traceback.format_exception(err))
            print(f'Received SolanaRpcException when fetching Mango accounts:\n {err_msg}')
            time.sleep(10)
            return self.get_all_accounts_for_group(mango_group)

        if not res.value:
            print(f'Unable to fetch accounts for group: {mango_group}')
            return []

        print(f'Fetched {len(res.value)} accounts for group {mango_group}')

        return [(i.pubkey, MangoAccount.decode(i.account.data)) for i in res.value]


    def get_unprocessed_events(self) -> None:
        mango_groups = self.get_groups()
        mango_accounts: list[tuple[Pubkey, MangoAccount]] = []

        for mango_group in mango_groups:
            mango_accounts += self.get_all_accounts_for_group(mango_group)

        self.accounts = mango_accounts

    def process_event(self):
        raise NotImplementedError('IMPLEMENT ME')
        pass

    def process_unprocessed_events(self):
        
        for account_pubkey, account in self.accounts:
            mango_group = str(account.group)
            mango_account = str(account_pubkey)

            # TODO: Add perps, serum3
            for token in account.tokens:
                if token.token_index == 65535:
                    # Disabled position
                    continue

                mint = self.group_token_index_map.get(mango_group)

                if not mint:
                    print(f'Unable to find token index map for group {mango_group}')
                    continue

                mint = mint.get(token.token_index)

                if not mint:
                    print(f'Unable to find mint info for group {mango_group}, token index {token.token_index}')
                    continue

                mint_address = mint['mint']
                position_index = Decimal(token.indexed_position.val) / 2**48
                index = Decimal(token.previous_index.val) / 2**48
                position = position_index * index

                if position > 0:
                    self.loan_entities[mango_account].collateral.set_value(token=mint_address, value=position)

                elif position < 0:
                    self.loan_entities[mango_account].debt.set_value(token=mint_address, value=abs(position))

                else:
                    continue

            for order in account.serum3:
                if order.market_index == 65535:
                    # Order Unset
                    continue

                # Get base and quote token info
                mint = self.group_token_index_map.get(mango_group)
                if not mint:
                    print(f'Unable to find token index map for group {mango_group}')
                    continue

                base_mint = mint.get(order.base_token_index)
                quote_mint = mint.get(order.quote_token_index)

                if not base_mint:   
                    print(f'Unable to find base token index map for index {order.base_token_index}')
                    continue

                if not quote_mint:   
                    print(f'Unable to find quote token index map for index {order.quote_token_index}')
                    continue
                
                try:
                    # Fetch Serum order account info
                    fetched_order = self.client.get_account_info(order.open_orders)
                except SolanaRpcException: 
                    logging.error(f'Unable to fetch serum order {order.open_orders} for account: {mango_account}')
                    continue

                # Parse Serum order
                parsed_order = OPEN_ORDERS_LAYOUT.parse(fetched_order.value.data)

                # Total contains the amount locked in order, the filled amount, 
                base_amount = parsed_order.base_token_total   
                quote_amount = parsed_order.quote_token_total 

                self.loan_entities[mango_account].collateral.increase_value(token=base_mint['mint'], value=base_amount)
                self.loan_entities[mango_account].collateral.increase_value(token=quote_mint['mint'], value=quote_amount)

        self.last_slot = int(time.time())
                


def liq_debt(x: pd.Series, collateral_collumn: str, debt_collumn: str) -> float:
    if x['health'] > 0:
        return 0
    coll_debt_diff = x[collateral_collumn] - x[debt_collumn]

    if coll_debt_diff < 0:
        # Means debt was higher than collateral, so the maximum that
        # can be liquidated is all of collateral
        return x[collateral_collumn]

    # In this case the collateral is higher than debt we need to liquidate
    # the amount that would bring the overall health above 0 

    # assets / borrows - 1 = health ie -> 100 / 150 - 1 = -0.33
    # we need to bring borrows to 100 -> multiply borrows by health
    # so we get abs(150 * -0.33) -> 50 and that's amount that need to be 
    # liquidated to bring borrows back to 100 (so health will be >=0)
    liquidation_needed_for_good_health = abs(x['debt_usd'] * x['health'])

    # if liquidation needed is higher then debt then return debt as that the 
    # max that can be liquidated in current loan, else just liquidation needed
    if liquidation_needed_for_good_health > x[debt_collumn]:
        return x[debt_collumn]
    
    return liquidation_needed_for_good_health


def compute_liquidable_debt_at_price(
    loan_states: pd.DataFrame,
    token_prices: dict[str, float],
    collateral_token: str,
    target_collateral_token_price: Decimal,
    debt_token: str,
) -> Decimal:

    # collateral_token_price = token_prices[collateral_token]
    # debt_token_price = token_prices[debt_token]
    price_ratio = target_collateral_token_price / token_prices[collateral_token]

    collateral_collumn = f'collateral_usd_{collateral_token}'
    debt_collumn = f'debt_usd_{debt_token}'

    if collateral_collumn in loan_states.columns:
        loan_states[collateral_collumn] = loan_states[collateral_collumn] * price_ratio

    # if debt_collumn in loan_states.columns:
    #     loan_states[debt_collumn] = loan_states[debt_collumn] * price_ratio

    loan_states['collateral_usd'] = loan_states[[x for x in loan_states.columns if 'collateral_usd_' in x]].sum(axis = 1)
    loan_states['debt_usd'] = loan_states[[x for x in loan_states.columns if 'debt_usd_' in x]].sum(axis = 1)

    loan_states['health'] = (loan_states['collateral_usd'] / loan_states['debt_usd']) - 1
    loan_states.loc[loan_states['health'] > 1, 'health'] = 1

    loan_states['to_be_liquidated'] = loan_states.apply(lambda x: liq_debt(x, collateral_collumn, debt_collumn), axis = 1)

    return loan_states['to_be_liquidated'].sum()


def get_mango_user_stats_df(loan_states: pd.DataFrame) -> pd.DataFrame:

    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}

    for collateral_token in collateral_tokens:
        loan_states[f'collateral_{collateral_token}'] = (
            loan_states['collateral'].apply(lambda x: x[collateral_token] if collateral_token in x else Decimal('0'))
        )
    for debt_token in debt_tokens:
        loan_states[f'debt_{debt_token}'] = (
            loan_states['debt'].apply(lambda x: x[debt_token] if debt_token in x else Decimal('0'))
        )


    underlying_collateral_tokens: set = collateral_tokens
    underlying_debt_tokens: set = debt_tokens
    token_prices = get_prices_for_tokens(list(underlying_collateral_tokens | underlying_debt_tokens))
    token_parameters = src.mango_token_params_map.get_mango_token_params_map()
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
            * token_prices[collateral_token]
        )

        loan_states[f'risk_adj_collateral_usd_{collateral_token}'] = (
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
            * token_prices[debt_token]
        )
        

        loan_states[f'risk_adj_debt_usd_{debt_token}'] = (
            loan_states[f'debt_{debt_token}'].astype(float)
            / (10**decimals)
            * float(liab_maint_w)
            * token_prices[debt_token]
        )

    loan_states['risk_adj_debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_debt_usd_')]].sum(axis=1)
    loan_states['debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('debt_usd_')]].sum(axis=1)

    loan_states['risk_adj_collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_collateral_usd_')]].sum(axis=1)
    loan_states['collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('collateral_usd_')]].sum(axis=1)

    loan_states['std_health'] = (loan_states['risk_adj_collateral_usd'] / loan_states['risk_adj_debt_usd'])

    wanted_cols = [
        'protocol', 
        'user', 
        'std_health',
        'collateral_usd', 
        'risk_adj_collateral_usd',
        'debt_usd', 
        'risk_adj_debt_usd',
        'collateral',
        'debt',
    ]

    return loan_states[wanted_cols]

