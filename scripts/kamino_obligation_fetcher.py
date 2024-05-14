"""
Script for Solend loan states collection.
"""
# Standard library imports
import logging
import os
import time
from typing import Any, Dict, List, Tuple

# Related third-party imports
import pandas as pd
import requests
from solana.exceptions import SolanaRpcException
from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey
from solders.rpc.responses import GetProgramAccountsResp

# Local application/library specific imports
import db
from src.loans.loan_state import store_loan_states
from src.protocols.anchor_clients.kamino_client.accounts.obligation import Obligation

# logger
LOGGER = logging.getLogger(__name__)

# Constants
KAMINO_PROGRAM_ID = Pubkey.from_string("KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD")
AUTHENTICATED_RPC_URL = os.getenv("RPC_URL")



# def get_reserve_to_supply_map(reserves: List[str]) -> Dict[str, Any]:
#     """ Get reserve data from solend.fi API. """
#     ids = ",".join(reserves)
#     url = f'https://api.solend.fi/v1/reserves/?ids={ids}'
#
#     response = requests.get(url, timeout=15)
#     return {
#         i['reserve']['address']: {
#             'liquiditySupply': i['reserve']['liquidity']['supplyPubkey'],
#             'collateralSupply': i['reserve']['collateral']['supplyPubkey'],
#             'liquidityMint': i['reserve']['liquidity']['mintPubkey'],
#             'liquidityMintDecimals': i['reserve']['liquidity']['mintDecimals'],
#             'collateralMint': i['reserve']['collateral']['mintPubkey'],
#             'cumBorrowRateWADs': i['reserve']['liquidity']['cumulativeBorrowRateWads']
#         }
#         for i in response.json()['results']
#     }


def fetch_obligations(pool_pubkey: str, client: Client) -> GetProgramAccountsResp:
    """ Fetch Solend obligations for pool. """
    try:

        filters = [
            Obligation.layout.sizeof() + 8,
            MemcmpOpts(32, pool_pubkey),
        ]
        response = client.get_program_accounts(
            KAMINO_PROGRAM_ID,
            encoding='base64',
            filters=filters
        )

        return response

    except SolanaRpcException as e:
        LOGGER.error(f"SolanaRpcException: {e} while collecting obligations for `{pool_pubkey}`.")
        time.sleep(0.5)
        return fetch_obligations(pool_pubkey, client)


def get_slot_number(client: Client) -> int:
    """ Fetch Solend obligations for pool. """
    try:
        response = client.get_slot()
        return response.value

    except SolanaRpcException as e:
        LOGGER.error(f"SolanaRpcException: {e} while collecting slot number.")
        time.sleep(0.25)
        return get_slot_number(client)


def obtain_loan_states():
    """ Obtain Solend loan states. """
    LOGGER.info("Start loan states collection.")
    # get current slot number
    client = Client(AUTHENTICATED_RPC_URL)
    slot = get_slot_number(client)
    # get and decode main pool obligations
    response = fetch_obligations(str(LENDING_MARKET_MAIN), client)
    decoded_obligations = {
        str(i.pubkey): decode_obligation(ObligationLayout.parse(i.account.data))
        for i in response.value
    }
    LOGGER.info("Loan states for Solend MAIN pool successfully collected and decoded.")
    # get and decode obligations for isolated pools
    for _, market_address in ISOLATED_POOLS.items():
        response = fetch_obligations(market_address, client)
        if not response.value:
            continue
        decoded_pool_obligations = {
            str(i.pubkey): decode_obligation(ObligationLayout.parse(i.account.data))
            for i in response.value
        }
        decoded_obligations.update(decoded_pool_obligations)
    LOGGER.info("Loan states for Solend ISOLATED pools successfully collected and decoded.")
    # get supply data for reserves
    reserves = list({
        i['publicKey']
        for _, obligation in decoded_obligations.items()
        for position in list(obligation)
        for i in position
    })
    reserve_to_supply_map = get_reserve_to_supply_map(reserves)

    # Format decoded obligation data
    obligations_processed = []
    for user, obligation in decoded_obligations.items():
        processed_obligation = {
            'slot': slot,
            'protocol': 'solend',
            'user': user,
            'collateral': process_collateral(obligation, reserve_to_supply_map),
            'debt': process_debt(obligation, reserve_to_supply_map)
        }
        obligations_processed.append(processed_obligation)
    new_loan_states = pd.DataFrame(obligations_processed)

    # store loan states to database
    with db.get_db_session() as session:
        store_loan_states(new_loan_states, 'kamino', session)
    LOGGER.info(f"{new_loan_states.shape[0]} loan states successfully collected and saved for `{slot}` block.")

    LOGGER.info("Start updating health factors...")
    start_time = time.time()
    # TODo store health factors to kamino_health_ratios table
    LOGGER.info(f"Health Factors updated in {time.time() - start_time:.2f} second.")



# run loan states collection in an infinite loop
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        timestamp = time.time()
        obtain_loan_states()
        elapsed_time = time.time() - timestamp
        LOGGER.info(f"Loan state collection successfully done in {elapsed_time:.2f} seconds.")
        time.sleep(60*15 - elapsed_time)
