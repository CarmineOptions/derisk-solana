import traceback
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


AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")

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
            initial_loan_states=initial_loan_states,
        )
        self.client = Client(AUTHENTICATED_RPC_URL)
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
        self.last_slot = int(time.time())
                