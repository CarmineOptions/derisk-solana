"""
Script for Kamino loan states collection.
"""
# Standard library imports
import asyncio
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List

# Related third-party imports
import pandas as pd
from solana.exceptions import SolanaRpcException
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey
from solders.rpc.responses import RpcKeyedAccount

# Local application/library specific imports
import db
from src.loans.kamino import KaminoState
from src.loans.loan_state import store_loan_states
from src.parser import TransactionDecoder
from src.protocols.addresses import KAMINO_ADDRESS
from src.protocols.anchor_clients.kamino_client.accounts.obligation import Obligation
from src.protocols.anchor_clients.kamino_client.accounts.reserve import Reserve
from src.protocols.idl_paths import KAMINO_IDL_PATH

# logger
LOGGER = logging.getLogger(__name__)

# Constants
KAMINO_PROGRAM_ID = Pubkey.from_string("KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD")
AUTHENTICATED_RPC_URL = os.getenv("RPC_URL")
LENDING_MARKET_MAIN = '7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'
JLP_MARKET = 'DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek'
ALTCOIN_MARKET = 'ByYiZxp8QrdN9qbdtaAiePN8AAr3qvTPppNJDpf5DVJ5'


async def fetch_accounts(pool_pubkey: str, client: AsyncClient, filters: List[Any]) -> List[RpcKeyedAccount]:
    """ Fetch Solend obligations for pool. """
    try:
        response = await client.get_program_accounts(
            KAMINO_PROGRAM_ID,
            encoding='base64',
            filters=filters
        )

        return response.value

    except SolanaRpcException as e:
        LOGGER.error(f"SolanaRpcException: {e} while collecting obligations for `{pool_pubkey}`.")
        time.sleep(0.5)
        return await fetch_accounts(pool_pubkey, client, filters)


async def get_slot_number(client: AsyncClient) -> int:
    """ Fetch Solend obligations for pool. """
    try:
        response = await client.get_slot()
        return response.value

    except SolanaRpcException as e:
        LOGGER.error(f"SolanaRpcException: {e} while collecting slot number.")
        time.sleep(0.25)
        return await get_slot_number(client)


async def get_reserve_to_supply_map(decoder: TransactionDecoder, client: AsyncClient) -> Dict[str, Any]:
    """ Get reserve data for Kamino reserves. """
    reserves = []
    for market in [LENDING_MARKET_MAIN, JLP_MARKET, ALTCOIN_MARKET]:
        filters = [
            Reserve.layout.sizeof() + 8,
            MemcmpOpts(32, str(market)),
        ]

        market_accounts = await fetch_accounts(market, client, filters)

        market_reserves = [
            {
                'address': str(reserve.pubkey),
                'info': decoder.program.coder.accounts.decode(reserve.account.data)
            }
            for reserve in market_accounts
        ]

        for reserve in market_reserves:
            reserves.append(reserve)

    return {
        reserve['address']: {
            'liquiditySupply': str(reserve['info'].liquidity.supply_vault),
            'collateralSupply': str(reserve['info'].collateral.supply_vault),
            'liquidityMint': str(reserve['info'].liquidity.mint_pubkey),
            'liquidityMintDecimals': reserve['info'].liquidity.mint_decimals,
            'collateralMint': str(reserve['info'].collateral.mint_pubkey),
            'cumBorrowRateWADs': reserve['info'].liquidity.cumulative_borrow_rate_bsf.value[0]
        }
        for reserve in reserves
    }


def process_collateral(obligation: Any, reserve_to_supply_map: Dict[str, Any]):
    """
    Format collateral data:
     - replace reserve with corresponding supply
    """
    collateral_raw = obligation.deposits
    collateral = {}
    for position in collateral_raw:
        amount = position.deposited_amount
        if amount == 0:
            continue
        reserve = str(position.deposit_reserve)
        collateral_mint = reserve_to_supply_map[reserve]['collateralMint']
        collateral[str(collateral_mint)] = {'amount': amount, 'reserve': reserve}
    return collateral


def process_debt(obligation: Any, reserve_to_supply_map: Dict[str, Any]):
    """
    Format debt data:
    - replace reserve with corresponding supply
    - calculate borrowed amount by accounting for interest.
    """
    debt_raw = obligation.borrows
    debt = {}
    for position in debt_raw:
        borrowed_amount = position.borrowed_amount_sf
        if borrowed_amount == 0:
            continue
        reserve = str(position.borrow_reserve)
        liquidity_mint = reserve_to_supply_map[reserve]['liquidityMint']
        cumulative_borrow_rate = position.cumulative_borrow_rate_bsf.value[0]

        debt[str(liquidity_mint)] = {
            'rawAmount': borrowed_amount / cumulative_borrow_rate,
            'reserve': reserve
        }

    return debt


async def obtain_loan_states():
    """ Obtain Solend loan states. """
    LOGGER.info("Start loan states collection.")
    # get current slot number
    client = AsyncClient(AUTHENTICATED_RPC_URL)
    slot = await get_slot_number(client)
    # get and decode main pool obligations
    obligations = await fetch_accounts(
        str(LENDING_MARKET_MAIN), client, filters = [
            Obligation.layout.sizeof() + 8,
            MemcmpOpts(32, str(LENDING_MARKET_MAIN)),
        ]
    )

    LOGGER.info("Loan states for KAMINO MAIN pool successfully collected.")
    # get and decode obligations for isolated pools
    for market_address in [JLP_MARKET, ALTCOIN_MARKET]:
        filters = [
            Obligation.layout.sizeof() + 8,
            MemcmpOpts(32, market_address),
        ]
        response = await fetch_accounts(market_address, client=client, filters=filters)
        obligations.extend(response)
    LOGGER.info("Loan states for KAMINO ALTCOIN and JLP pools successfully collected.")
    # Create Kamino program decoder
    decoder = TransactionDecoder(path_to_idl=Path(KAMINO_IDL_PATH), program_id=Pubkey.from_string(KAMINO_ADDRESS))
    decoded_obligations = {}
    # decode obligations
    for obligation in obligations:
        decoded_obligations[str(obligation.pubkey)] = decoder.program.coder.accounts.decode(obligation.account.data)
    LOGGER.info("All obligations are successfully decoded.")
    # decode reserves and create reserve_to_supply_map
    reserve_to_supply_map = await get_reserve_to_supply_map(decoder, client)

    # Format decoded obligation data
    obligations_processed = []
    for user, obligation in decoded_obligations.items():
        processed_obligation = {
            'slot': slot,
            'protocol': 'kamino',
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
    state = KaminoState(initial_loan_states=new_loan_states)
    state.save_health_ratios()
    LOGGER.info(f"Health Factors updated in {time.time() - start_time:.2f} second.")


async def main():
    while True:
        timestamp = time.time()
        await obtain_loan_states()
        elapsed_time = time.time() - timestamp
        LOGGER.info(f"Loan state collection successfully done in {elapsed_time:.2f} seconds.")
        time.sleep(60*15 - elapsed_time)


# run loan states collection in an infinite loop
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
