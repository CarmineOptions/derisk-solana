from decimal import Decimal
import time
import asyncio
import os

from solana.exceptions import SolanaRpcException
from solana.rpc.async_api import AsyncClient
import requests
from src.protocols.anchor_clients.mango_client.accounts.bank import Bank
from src.loans.mango import get_authenticated_rpc_url

from solders.pubkey import Pubkey

def get_banks_addresses() -> list[Pubkey]:

    try:
        r = requests.get('https://api.mngo.cloud/data/v4/group-metadata', timeout = 30)
        r.raise_for_status()

        main_group = [i for i in r.json()['groups'] if i['name'] == 'MAINNET.0'][0]
        banks = [Pubkey.from_string(i['banks'][0]['publicKey']) for i in main_group['tokens']]

    except requests.exceptions.Timeout:
        time.sleep(60)
        return get_banks_addresses()

    return banks

def fetch_banks(client: AsyncClient, banks: list[Pubkey]) -> list[Bank]:
    try: 
        banks_fetched = asyncio.run(Bank.fetch_multiple(client, banks))
    except SolanaRpcException: 
        time.sleep(30)
        return fetch_banks(banks)

    return banks_fetched

def get_mango_token_params_map() -> dict[str, dict[str, Decimal]]:
    client = AsyncClient(get_authenticated_rpc_url())
  
    banks = get_banks_addresses()
    banks_fetched = fetch_banks(client, banks)

    token_params = {}
    for bank in banks_fetched:
        mint = str(bank.mint)

        token_params[mint] = {
            'maint_asset_weight': Decimal(bank.maint_asset_weight.val) / 2**48,
            'init_asset_weight': Decimal(bank.init_asset_weight.val) / 2**48,
            'maint_liab_weight': Decimal(bank.maint_liab_weight.val) / 2**48,
            'init_liab_weight': Decimal(bank.init_liab_weight.val) / 2**48,
        }
    return token_params
