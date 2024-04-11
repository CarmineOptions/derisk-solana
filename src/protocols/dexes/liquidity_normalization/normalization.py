import time
import logging
import traceback
from decimal import Decimal

import db
from src.protocols.dexes.amms.utils import convert_amm_reserves_to_bids_asks
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map

LOG = logging.getLogger(__name__)
NORMALIZE_INTERVAL_SECONDS: int = 5 * 60  # Five minutes


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

    return entries


def common_raw_amm_data_handler(
    amm_entry: db.AmmLiquidity, timestamp: int, tokens: dict[str, dict[str, str | int]]
) -> db.DexNormalizedLiquidity:
    """
    Converts raw amm data from AmmLiquidity to DexNormalizedLiquidity.

    Parameters:
    - amm_entry: AmmLiquidity table entry
    - timestamp: timestamp (to make all entries have the same one, better for grouping etc.)
    - tokens: mapping of token addresses to token info (in this case, 'decimals' is needed)

    Returns:
    - normalized liquidity: AmmLiquidity converted to DexNormalizedLiquidity
    """
    # Get tokens decimals
    token_x_decimals = int(tokens[str(amm_entry.token_x_address)].get("decimals", False))
    token_y_decimals = int(tokens[str(amm_entry.token_y_address)].get("decimals", False))

    if not token_x_decimals or not token_y_decimals:
        raise ValueError(
            f"Unable to find decimals for addresses: {amm_entry.token_x_address}, {amm_entry.token_y_address}"
        )

    # Convert token amounts to human readable values
    token_x_amount = Decimal(amm_entry.token_x_amount or 0) / 10**token_x_decimals
    token_y_amount = Decimal(amm_entry.token_y_amount or 0) / 10**token_y_decimals

    if token_x_amount * token_y_amount == 0:
        raise ValueError(f'One of the token amounts is zero: x is {token_x_amount}, y is {token_y_amount}')

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
}


def upload_normalized_liquidity(data: list[db.DexNormalizedLiquidity]):
    """
    Uploads list of DexNormalizedLiquidity to the database.

    Parameters:
    - data: list of DexNormalizedLiquidity entries
    """
    with db.get_db_session() as sesh:
        sesh.add_all(data)
        sesh.commit()


def normalize_amm_liquidity():
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
            
            if not entry.token_y_amount and entry.token_x_amount and entry.dex:
                continue

            handler = RAW_DEX_DATA_HANDLERS.get(entry.dex)

            if not handler:
                LOG.error(f'Unable to find normalization handler for {entry.dex}')
                continue

            normalized_data.append(handler(entry, timestamp, tokens))           

        upload_normalized_liquidity(normalized_data)

    except Exception as e:  # pylint: disable=broad-exception-caught
        tb_str = traceback.format_exc()
        # Log the error message along with the traceback
        LOG.error(f"An error occurred: {e}\nTraceback:\n{tb_str}")


def normalize_dex_data_continuously():
    """
    Normalizes dex data continuously, every n-seconds as defined by NORMALIZE_INTERVAL_SECONDS consts.
    """

    while True:
        time_start = time.time()

        normalize_amm_liquidity()

        execution_time = time.time() - time_start

        if execution_time <= NORMALIZE_INTERVAL_SECONDS:
            LOG.info(f"Normalized AMM Liquidity in {execution_time} seconds")
        else:
            LOG.warning(f"Normalized AMM Liquidity in {execution_time} seconds")

        time.sleep(max(0, NORMALIZE_INTERVAL_SECONDS - execution_time))
