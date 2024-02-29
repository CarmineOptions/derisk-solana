"""
Module containg logic for fetching Solana onchain liquidity - 
both AMM and CLOB (in which case it also pushes it the database).
"""
import logging
import os
import time
import traceback

from src.protocols.dexes.clob import CLOB

# Ordebook-based DEXes
from src.protocols.dexes.clob import Phoenix
from src.protocols.dexes.clob import OpenBook
from src.protocols.dexes.clob import GooseFx
import db

# Collect and store orderbook liquidity every 5 minutes
COLLECT_INTERVAL_SECONDS: int = 5 * 60

AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")

# TODO: To be implemented. pylint: disable=W0511
class AMMs:
    """
    A class that describes the state of all relevant pools of all relevant swap AMMs.
    """

    def __init__(self) -> None:
        pass

    def fetch_pools(self) -> None:
        """
        Fetches all AMM liquidity on Solana.
        """


class CLOBs:
    """
    A class that updates and fetches the state of all relevant order books of all relevant CLOB dexes.
    List of CLOB to update orderbooks for provided during initialization.
    """

    def __init__(self, clob_list: list[CLOB]) -> None:
        self.clob_list = clob_list

    async def update_orderbooks(self) -> None:
        """
        Updates orderbooks of all provided CLOB dexes
        """
        timestamp = int(time.time())
        for dex in self.clob_list:
            await dex.update_orderbooks(timestamp)


async def update_ob_dex_data():
    """
    Updates CLOB liquidity once.
    """
    try:
        clobs = CLOBs(
            [
                Phoenix(endpoint=AUTHENTICATED_RPC_URL),
                OpenBook(endpoint=AUTHENTICATED_RPC_URL),
                GooseFx(endpoint=AUTHENTICATED_RPC_URL),
            ]
        )
        await clobs.update_orderbooks()
        logging.info("Successfuly updated CLOB liquidity")
    except Exception as err:  # pylint: disable=W0718
        # We want to log any error but we want the collector
        # to keep on running.

        # Program is designed to run in Docker container - so there is no need
        # to separately catch errors like KeyboardInterrupt since we can
        # always just stop the container
        err_msg = "".join(traceback.format_exception(err))
        logging.error(f"Following error occured:\n {err_msg}")


async def update_ob_dex_data_continuously():
    """
    Updates CLOB liquidity continuously, every n-seconds as defined by COLLECT_INTERVAL_SECONDS constant.
    """

    while True:
        time_start = time.time()

        await update_ob_dex_data()

        execution_time = time.time() - time_start

        if execution_time <= COLLECT_INTERVAL_SECONDS:
            logging.info(f"Collected OB Liquidity in {execution_time} seconds")
        else:
            logging.warning(f"Collected OB Liquidity in {execution_time} seconds")

        time.sleep(max(0, COLLECT_INTERVAL_SECONDS - execution_time))


def load_ob_dex_data(start_timestamp: int) -> list[db.CLOBLiqudity]:

    """
    Returns un-agreggated CLOB liquidity data starting from start_timestamp
    """
    with db.get_db_session() as session:
        entries = (
            session.query(
                db.CLOBLiqudity,
            )
            .filter(db.CLOBLiqudity.timestamp >= start_timestamp)
            .all()
        )

    return entries


# TODO: To be implemented. pylint: disable=W0511
# def load_amm_dex_data() -> AMMs:
# 	amm_dx = AMMs()
# 	amm_dx.fetch_pools()
# 	return amm_dx

# TODO: To be implemented. pylint: disable=W0511
# def load_dex_data() -> tuple[AMMs, CLOBs]:
# 	return load_amm_dex_data(), load_ob_dex_data()
