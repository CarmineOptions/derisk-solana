import os
import math
import time
import logging
import traceback
from decimal import Decimal
import logging


from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
import numpy as np
import pandas as pd

import db
from src.protocols.dexes.amms.utils import convert_amm_reserves_to_bids_asks
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map
from src.protocols.dexes.amms.utils import get_tokens_symbol_to_info_map
from src.protocols.dexes.amms.utils import get_mint_decimals

LOG = logging.getLogger(__name__)
NORMALIZE_INTERVAL_SECONDS: int = 20 * 60  # Five minutes

AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")


def get_last_entries_per_dex_per_pair() -> list[db.AmmLiquidity]:
    """
    For every distinct dex in AmmLiquidity table, it gets last entry of every distinct pair.

    Returns:
    - AmmLiquidity entries: List of AmmLiquidity entries
    """
    with db.get_db_session() as session:
        entries = (
            session.query(db.AmmLiquidity)
            .distinct(
                db.AmmLiquidity.dex,
                db.AmmLiquidity.token_x_address,
                db.AmmLiquidity.token_y_address,
            )
            .order_by(
                db.AmmLiquidity.dex,
                db.AmmLiquidity.token_x_address,
                db.AmmLiquidity.token_y_address,
                db.AmmLiquidity.timestamp.desc(),
            )
            .all()
        )

    if len(entries) == 0:
        LOG.warning("Fetched zero entries to normalize.")

    return entries


async def get_onchain_token_decimals(token_address: Pubkey) -> int:
    return await get_mint_decimals(token_address, AsyncClient(AUTHENTICATED_RPC_URL))


async def common_raw_amm_data_handler(
    amm_entry: db.AmmLiquidity, timestamp: int, tokens: dict[str, dict[str, str | int]]
) -> db.DexNormalizedLiquidity | None:
    """
    Converts raw amm data from AmmLiquidity to DexNormalizedLiquidity.

    Parameters:
    - amm_entry: AmmLiquidity table entry
    - timestamp: timestamp (to make all entries have the same one, better for grouping etc.)
    - tokens: mapping of token addresses to token info (in this case, 'decimals' is needed)

    Returns:
    - normalized liquidity: AmmLiquidity converted to DexNormalizedLiquidity
    """
    token_x = tokens.get(str(amm_entry.token_x_address))
    token_y = tokens.get(str(amm_entry.token_y_address))

    if not token_x:
        LOG.warning(
            f"Info for token X({amm_entry.token_x_address}) not present in API, getting onchain value."
        )
        token_x_decimals = await get_onchain_token_decimals(
            Pubkey.from_string(str(amm_entry.token_x_address))
        )
    else:
        token_x_decimals = int(tokens[str(amm_entry.token_x_address)]["decimals"])

    if not token_y:
        LOG.warning(
            f"Info for token Y({amm_entry.token_x_address}) not present in API, getting onchain value."
        )
        token_y_decimals = await get_onchain_token_decimals(
            Pubkey.from_string(str(amm_entry.token_y_address))
        )
    else:
        token_y_decimals = int(tokens[str(amm_entry.token_y_address)]["decimals"])

    # Convert token amounts to human readable values
    token_x_amount = Decimal(amm_entry.token_x_amount or 0) / 10**token_x_decimals
    token_y_amount = Decimal(amm_entry.token_y_amount or 0) / 10**token_y_decimals

    if token_x_amount * token_y_amount == 0:
        LOG.warning(
            f"One of the token amounts is zero: x({amm_entry.token_x_address}) is {token_x_amount}, "
            f"y({amm_entry.token_y_address}) is {token_y_amount}"
        )
        return None

    # Convert amm reserves to OB-like data
    amm_bids_asks = convert_amm_reserves_to_bids_asks(token_x_amount, token_y_amount)

    bids = [(float(i.price), float(i.amount)) for i in amm_bids_asks["bids"]]
    asks = [(float(i.price), float(i.amount)) for i in amm_bids_asks["asks"]]

    return db.DexNormalizedLiquidity(
        timestamp=timestamp,
        dex=amm_entry.dex,
        market_address=amm_entry.market_address,
        token_x_address=amm_entry.token_x_address,
        token_y_address=amm_entry.token_y_address,
        bids=bids,
        asks=asks,
    )


# Maps protocol identifier to function that will convert
# it's data to DexNormalizedLiquidity entry
RAW_DEX_DATA_HANDLERS = {
    "INVARIANT": common_raw_amm_data_handler,
    "LIFINITY": common_raw_amm_data_handler,
    "SABER": common_raw_amm_data_handler,
    "SENTRE": common_raw_amm_data_handler,
    "BonkSwap": common_raw_amm_data_handler,
    "DOOAR": common_raw_amm_data_handler,
    "FluxBeam": common_raw_amm_data_handler,
    'Meteora': common_raw_amm_data_handler,
}


def upload_normalized_liquidity(data: list[db.DexNormalizedLiquidity]):
    """
    Uploads list of DexNormalizedLiquidity to the database.

    Parameters:
    - data: list of DexNormalizedLiquidity entries
    """

    if len(data) == 0:
        LOG.warning("No normalized entries to upload")
        return

    with db.get_db_session() as sesh:
        sesh.add_all(data)
        sesh.commit()


async def normalize_amm_liquidity():
    """
    Fetches latest values of AmmLiquidity, converts them to DexNormalizedLiquidity
    and uploads them to database.
    """
    try:
        tokens = get_tokens_address_to_info_map()
        entries = get_last_entries_per_dex_per_pair()

        timestamp = int(time.time())

        normalized_data = []

        for entry in entries:

            if not entry.token_y_amount and entry.token_x_amount:
                continue

            if not entry.dex:
                LOG.warning(f"Can't handle AmmLiquidity entry: {entry}")
                continue

            handler = RAW_DEX_DATA_HANDLERS.get(entry.dex)

            if not handler:
                LOG.error(f"Unable to find normalization handler for {entry.dex}")
                continue

            normalized_entry = await handler(entry, timestamp, tokens)

            if not normalized_entry:
                LOG.error("Received None entry when normalizing.")
                continue

            normalized_data.append(normalized_entry)

        upload_normalized_liquidity(normalized_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        tb_str = traceback.format_exc()
        # Log the error message along with the traceback
        LOG.error(f"An error occurred: {e}\nTraceback:\n{tb_str}")


def get_week_of_clob_data() -> pd.DataFrame:
    one_week_ago = time.time() - 7 * 86_400
    with db.get_db_session() as sesh:
        distinct_pairs = (
            sesh.query(db.CLOBLiqudity.dex, db.CLOBLiqudity.pair)
            .distinct(db.CLOBLiqudity.dex, db.CLOBLiqudity.pair)
            .all()
        )
        all_data = []
        
        for dex, pair in distinct_pairs:
            week_data = (
                sesh.query(db.CLOBLiqudity)
                .filter(db.CLOBLiqudity.dex == dex)
                .filter(db.CLOBLiqudity.pair == pair)
                .filter(db.CLOBLiqudity.timestamp >= one_week_ago)
            )

            df = pd.read_sql(week_data.statement, sesh.bind)
            all_data.append(df)
            
    df = pd.concat(all_data)
    df = df[~df['pair'].str.contains('PERP')]
    return df

def get_volume_at_five_percent(row: pd.Series) -> float:
    bids = row['bids']
    asks = row['asks']
    if not bids or not asks:
        return 0
        
    mid_price = (bids[0][0] + asks[0][0]) / 2

    volume = 0
    for price, amount in (bids + asks): 
        if math.isclose(price, mid_price, rel_tol=0.05):
            volume += amount

    if volume == 0:
        return (bids[0][1] + asks[0][1]) 

    return volume

def normalize_clob_liqudity(clob_data: pd.DataFrame) -> list[db.DexNormalizedLiquidity]:
    symbols = get_tokens_symbol_to_info_map()
    normalized_entries = []
    now = int(time.time())
    for dex, dex_df in list(clob_data.groupby('dex')):
        for pair, pair_df in list(dex_df.groupby('pair')):
            week_median_volume = pair_df.apply(lambda x: get_volume_at_five_percent(x), axis = 1).median()
            base_token, quote_token = pair.split('/')

            mid_price = pair_df.iloc[pair_df['timestamp'].idxmax()].to_frame().apply(lambda x: (x['bids'][0][0] + x['asks'][0][0]) / 2 if x['bids'] and x['asks'] else 0).iloc[0]

            if not mid_price: 
                logging.info(f'No mid price found for {dex}: {pair}')
                continue

            if not symbols.get(base_token) or not symbols.get(quote_token):
                logging.info(f"No address found for either of: {pair}")
                continue
            base_address = symbols[base_token]['address']
            quote_address = symbols[quote_token]['address']

            NUM_LEVELS = 1_000               
            # Create 1k price levels from -99% to 99%
            new_price_levels = np.linspace(mid_price * 0.01, mid_price * 1.99, NUM_LEVELS)
            
            volume_per_level = week_median_volume / (NUM_LEVELS * 0.05)

            new_bids = [
                (price, volume_per_level) for price in new_price_levels 
                if  price < mid_price
            ]
            new_asks = [
                (price, volume_per_level) for price in new_price_levels 
                if price > mid_price
            ]
            new_entry = db.DexNormalizedLiquidity(
                timestamp = now,
                dex = dex,
                market_address = pair,
                token_x_address = base_address,
                token_y_address = quote_address,
                bids = new_bids,
                asks = new_asks
            )       

            normalized_entries.append(new_entry)

            
    return normalized_entries

def normalize_clob_dex_liqudity():
    try: 
        df = get_week_of_clob_data()
        normalized = normalize_clob_liqudity(df)
        upload_normalized_liquidity(normalized)
    except Exception as e:
        tb_str = traceback.format_exc()
        # Log the error message along with the traceback
        LOG.error(f"An error occurred while normalizing clob liq: {e}\nTraceback:\n{tb_str}")

async def normalize_dex_data_continuously():
    """
    Normalizes dex data continuously, every n-seconds as defined by NORMALIZE_INTERVAL_SECONDS consts.
    """

    while True:
        time_start = time.time()

        await normalize_amm_liquidity()
        normalize_clob_dex_liqudity()

        execution_time = time.time() - time_start

        if execution_time <= NORMALIZE_INTERVAL_SECONDS:
            LOG.info(f"Normalized AMM Liquidity in {execution_time} seconds")
        else:
            LOG.warning(f"Normalized AMM Liquidity in {execution_time} seconds")

        time.sleep(max(0, NORMALIZE_INTERVAL_SECONDS - execution_time))
