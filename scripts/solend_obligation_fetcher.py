"""
Script for Solend loan states collection.
"""
# Standard library imports
import logging
import os
import struct
import time
from typing import Any, Dict, List, Tuple

# Related third-party imports
import base58
import borsh_construct as borsh
import pandas as pd
import requests
from anchorpy.borsh_extension import BorshPubkey
from solana.exceptions import SolanaRpcException
from solana.rpc.api import Client
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey
from solders.rpc.responses import GetProgramAccountsResp

# Local application/library specific imports
import db
from src.loans.loan_state import store_loan_states
from src.loans.solend import SolendState

# logger
LOGGER = logging.getLogger(__name__)

# Constants
SOLEND_PROGRAM_ID = Pubkey.from_string("So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo")
LENDING_MARKET_MAIN = Pubkey.from_string("4UpD2fh7xH3VP9QQaXtsS1YY3bxzWhtfpks7FatyKvdY")
OBLIGATION_LEN = 1300
AUTHENTICATED_RPC_URL = os.getenv("RPC_URL")


LastUpdateLayout = borsh.CStruct(
    "slot" / borsh.U64,
    "stale" / borsh.U8
)

# struct layouts
ObligationLayout = borsh.CStruct(
    "version" / borsh.U8,
    "last_update" / LastUpdateLayout,
    "lendingMarket" / BorshPubkey,
    "owner" / BorshPubkey,
    "depositedValue" / borsh.U128,
    "borrowedValue" / borsh.U128,
    "allowedBorrowValue" / borsh.U128,
    "unhealthyBorrowValue" / borsh.U128,
    "padding" / borsh.U8[64],
    "depositsLen" / borsh.U8,
    "borrowsLen" / borsh.U8,
    "dataFlat" / borsh.U8[1096],
)

OBLIGATION_COLLATERAL_LAYOUT = "32s Q 16s 32x"  # 32 bytes PublicKey, uint64, uint128, 32 bytes padding
OBLIGATION_LIQUIDITY_LAYOUT = "32s 16s 16s 16s 32x"  # 32 bytes PublicKey, three uint128, 32 bytes padding

# isolated pool addresses
ISOLATED_POOLS = {
    "TURBO_SOL_POOL": "7RCz8wb6WXxUhAigok9ttgrVgDFFFbibcirECzWSBauM",
    "INVICTUS_POOL": "5i8SzwX2LjpGUxLZRJ8EiYohpuKgW2FYDFhVjhGj66P1",
    "STEP_POOL": "DxdnNmdWHcW6RGTYiD5ms5f7LNZBaA7Kd1nMfASnzwdY",
    "BONFIDA_POOL": "91taAt3bocVZwcChVgZTTaQYt2WpBVE3M9PkWekFQx4J",
    "STAR_ATLAS_POOL": "99S4iReDsyxKDViKdXQKWDcB6C3waDmfPWWyb5HAbcZF",
    "DOG_POOL": "HASr6hiYVoRcVXk3GttC4PjBBPQ3sGYDzE7HSPJdcke6",
    "STABLE_POOL": "GktVYgkstojYd8nVXGXKJHi7SstvgZ6pkQqQhUPD7y7Q",
    "NFT_POOL": "29yTiqjGdoNiRLMVc7ZoqFpbW3gkmefwMG9SUiMMD4J9",
    "COIN98_POOL": "7tiNvRHSjYDfc6usrWnSNPyuN68xQfKs1ZG2oqtR5F46",
    "UXD_POOL": "HCuEqcXaGeioiJf5vNMTyQC7HMPqJm5aZPkSjA2qceDS",
    "STEPN_POOL": "BjsAGLZzAgBUsiaTTDQv7PWDUDL9dQfKvYwb4q6FoDuD",
    "SHADOW_POOL": "Foo9vqN6fj1NyymHmD1gwZkgVgEqzNSrwyeqyoLYGe7j"
}


def get_reserve_to_supply_map(reserves: List[str]) -> Dict[str, Any]:
    """ Get reserve data from solend.fi API. """
    ids = ",".join(reserves)
    url = f'https://api.solend.fi/v1/reserves/?ids={ids}'

    response = requests.get(url, timeout=15)
    return {
        i['reserve']['address']: {
            'liquiditySupply': i['reserve']['liquidity']['supplyPubkey'],
            'collateralSupply': i['reserve']['collateral']['supplyPubkey'],
            'liquidityMint': i['reserve']['liquidity']['mintPubkey'],
            'liquidityMintDecimals': i['reserve']['liquidity']['mintDecimals'],
            'collateralMint': i['reserve']['collateral']['mintPubkey'],
            'cumBorrowRateWADs': i['reserve']['liquidity']['cumulativeBorrowRateWads']
        }
        for i in response.json()['results']
    }


def fetch_obligations(pool_pubkey: str, client: Client) -> GetProgramAccountsResp:
    """ Fetch Solend obligations for pool. """
    try:
        response = client.get_program_accounts(
            SOLEND_PROGRAM_ID,
            encoding='base64',
            filters=[
                OBLIGATION_LEN, MemcmpOpts(offset=10, bytes = str(pool_pubkey))
            ]
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


def process_collateral(
        obligation: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]],
        reserve_to_supply_map: Dict[str, Any]
):
    """
    Format collateral data:
     - replace reserve with corresponding supply
    """
    collateral_raw = obligation[1]
    collateral = {}
    for position in collateral_raw:
        reserve = position['publicKey']
        collateral_mint = reserve_to_supply_map[reserve]['collateralMint']
        collateral[collateral_mint] = {'amount': position['depositedAmount'], 'reserve': reserve}
    return collateral


def process_debt(
        obligation: Tuple[List[Dict[str, Any]], List[Dict[str, Any]]],
        reserve_to_supply_map: Dict[str, Any]
):
    """
    Format debt data:
    - replace reserve with corresponding supply
    - calculate borrowed amount by accounting for interest.
    """
    debt_raw = obligation[0]
    debt = {}
    for position in debt_raw:
        reserve = position['publicKey']
        liquidity_mint = reserve_to_supply_map[reserve]['liquidityMint']

        debt[liquidity_mint] = {
            'rawAmount': (position['borrowedAmountWads'] / position['cumulativeBorrowRateWads']),
            'reserve': reserve
        }

    return debt


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
        store_loan_states(new_loan_states, 'solend', session)
    LOGGER.info(f"{new_loan_states.shape[0]} loan states successfully collected and saved for `{slot}` block.")

    LOGGER.info("Start updating health factors...")
    start_time = time.time()
    state = SolendState(initial_loan_states=new_loan_states)
    state.save_health_ratios()
    LOGGER.info(f"Health Factors updated in {time.time() - start_time:.2f} second.")

def unpack_data(data: bytes, layout: str):
    """ Decode the binary data into structured data using predefined layouts. """
    layout_size = struct.calcsize(layout)
    num_items = len(data) // layout_size
    return [struct.unpack(layout, data[i * layout_size:(i + 1) * layout_size]) for i in range(num_items)]


def decode_obligation(parsed_obligation: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Decodes the binary data of an obligation account to extract detailed information
    about borrows and deposits.

    Args:
        parsed_obligation (Any): An object that contains the binary data of the obligation,
                                 specifically the lengths of borrows and deposits arrays,
                                 and the flat binary data.
    """
    # Extract lengths and raw binary data from the parsed obligation
    borrows_len = parsed_obligation.borrowsLen
    deposits_len = parsed_obligation.depositsLen
    data_flat = bytes(parsed_obligation.dataFlat)

    # Calculate the byte size of each layout according to the defined structures
    collateral_size = struct.calcsize(OBLIGATION_COLLATERAL_LAYOUT)
    liquidity_size = struct.calcsize(OBLIGATION_LIQUIDITY_LAYOUT)

    # Segment the flat data into collateral and liquidity portions
    collateral_data = data_flat[:deposits_len * collateral_size]
    liquidity_data = data_flat[
                     deposits_len * collateral_size:deposits_len * collateral_size + borrows_len * liquidity_size]

    # Decode the binary data into structured data using predefined layouts
    deposits = unpack_data(collateral_data, OBLIGATION_COLLATERAL_LAYOUT)
    borrows = unpack_data(liquidity_data, OBLIGATION_LIQUIDITY_LAYOUT)

    # Decode and collect borrows into a list of dictionaries
    decoded_borrows = []
    for borrow in borrows:
        public_key = base58.b58encode(borrow[0]).decode('utf-8')
        cumulative_borrow_rate_wads = int.from_bytes(borrow[1], byteorder='little')
        borrowed_amount_wads = int.from_bytes(borrow[2], byteorder='little')
        market_value = int.from_bytes(borrow[3], byteorder='little')

        decoded_borrows.append({
            "publicKey": public_key,
            "cumulativeBorrowRateWads": cumulative_borrow_rate_wads,
            "borrowedAmountWads": borrowed_amount_wads,
            "marketValue": market_value
        })

    # Decode and collect deposits into a list of dictionaries
    decoded_deposits = []
    for deposit in deposits:
        public_key = base58.b58encode(deposit[0]).decode('utf-8')
        deposited_amount = deposit[1]  # Already an integer
        market_value = int.from_bytes(deposit[2], byteorder='little')  # Convert 16-byte uint128

        decoded_deposits.append({
            "publicKey": public_key,
            "depositedAmount": deposited_amount,
            "marketValue": market_value
        })

    return decoded_borrows, decoded_deposits


# run loan states collection in an infinite loop
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        timestamp = time.time()
        obtain_loan_states()
        elapsed_time = time.time() - timestamp
        LOGGER.info(f"Loan state collection successfully done in {elapsed_time:.2f} seconds.")
        time.sleep(60*30 - elapsed_time)
