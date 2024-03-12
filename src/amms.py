"""
Module dedicated to fetching and storing data from AMM pools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import json
import logging
import time
import traceback
import asyncio
import os
import requests  # type: ignore

from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from solders.pubkey import Pubkey
from solders.account_decoder import ParsedAccount

from db import AmmLiquidity, get_db_session
from src.protocols.anchor_clients.bonkswap_client.accounts import Pool as BonkPool

AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")

LOG = logging.getLogger(__name__)


def check_bigint(value: int) -> int:
    """
    Checks if the given integer value fits within the PostgreSQL bigint range.

    Args:
            value (int): The integer value to check.

    Returns:
            int: Returns -2 if the value exceeds the PostgreSQL bigint range
    """
    # Define the bigint limits in PostgreSQL
    bigint_min = -9223372036854775808
    bigint_max = 9223372036854775807

    # Check if the value is within the bigint range
    if not bigint_min <= value <= bigint_max:
        return -2  # Return -2 if the value is outside the bigint range
    return value


class Amms:
    """
    A class that describes the state of all relevant pools of all relevant swap AMMs.
    """

    def __init__(self) -> None:
        pass

    async def update_pools(self) -> None:
        """
        Save pools data to database.
        :return:
        """
        # set timestamp
        timestamp = int(time.time())

        # collect and store pools
        orca_amm = OrcaAMM()
        orca_amm.timestamp = timestamp
        orca_amm.get_pools()
        orca_amm.store_pools()

        raydium_amm = RaydiumAMM()
        raydium_amm.timestamp = timestamp
        raydium_amm.get_pools()
        raydium_amm.store_pools()

        meteora_amm = MeteoraAMM()
        meteora_amm.timestamp = timestamp
        meteora_amm.get_pools()
        meteora_amm.store_pools()

        bonk_amm = BonkAMM()
        bonk_amm.timestamp = timestamp
        await bonk_amm.get_pools()
        bonk_amm.store_pools()

        doaar_amm = DooarAMM()
        doaar_amm.timestamp = timestamp
        doaar_amm.get_pools()
        doaar_amm.store_pools()


# TODO: To be implemented.
# def load_amm_data() -> Amms:
#     swap_amms = Amms()
#     swap_amms.update_pools()
#     return swap_amms


class Amm(ABC):
    # dex_name: str = ''
    pools: Any
    timestamp = int(time.time())

    def __init__(self):
        pass

    @abstractmethod
    def get_pools(self):
        """
        Fetch pools data.
        """
        raise NotImplementedError("Implement me!")

    def store_pools(self):
        """
        Save pools data to database.
        """
        for pool in self.pools:
            self.store_pool(pool)

    @abstractmethod
    def store_pool(self, pool: Any) -> None:
        """
        Save pool data to database.
        """
        raise NotImplementedError("Implement me!")

    @staticmethod
    def convert_to_big_integer_and_decimals(
        amount_str: str | None,
    ) -> Tuple[int | None, int | None]:
        """
        Convert string containing numerical value into integer and number of decimals.
        """
        if amount_str is None:
            return None, None
        # Check if there is a decimal point in the amount_str
        if "." in amount_str:
            # Split the string into whole and fractional parts
            whole_part, fractional_part = amount_str.split(".")
            # Calculate the number of decimals as the length of the fractional part
            decimals = len(fractional_part)
            # Remove the decimal point and convert the remaining string to an integer
            amount_big_integer = int(whole_part + fractional_part)
        else:
            # If there is no decimal point, there are no decimals and the conversion is straightforward
            decimals = 0
            amount_big_integer = int(amount_str)

        return amount_big_integer, decimals


class OrcaAMM(Amm):
    DEX_NAME = "Orca"

    def get_pools(self) -> None:
        """
        Fetches pool data from the Orca API and stores it in the `pools` attribute.
        """
        LOG.info("Fetching pools from Orca API")
        try:
            result = requests.get(
                "https://api.mainnet.orca.so/v1/whirlpool/list", timeout=30
            )
            decoded_result = result.content.decode("utf-8")
            self.pools = json.loads(decoded_result)["whirlpools"]
            LOG.info(f"Successfully fetched {len(self.pools)} pools")
        except requests.exceptions.Timeout:
            LOG.error("Request to Orca whirlpool API timed out")
            self.get_pools()

    def store_pool(self, pool: Dict[str, Any]) -> None:
        """
        Save pool data to database.
        """
        pair = f"{pool['tokenA']['symbol']}-{pool['tokenB']['symbol']}"
        market_address = pool.get("address", "Unknown")

        with get_db_session() as session:
            # Creating an instance of AmmLiquidity
            liquidity_entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                pair=pair,
                market_address=market_address,
                additional_info=json.dumps(pool),
            )
            # Add to session and commit
            session.add(liquidity_entry)
            session.commit()


class RaydiumAMM(Amm):
    DEX_NAME = "Orca"
    token_list: List

    def get_pools(self):
        """
        Fetches pool data from the Radium API and stores it in the `pools` attribute.
        """
        LOG.info("Fetching pools from Raydium API")
        try:
            result = requests.get(
                "https://api.raydium.io/v2/ammV3/ammPools", timeout=30
            )
            decoded_result = result.content.decode("utf-8")
            self.pools = json.loads(decoded_result)["data"]
            LOG.info(f"Successfully fetched {len(self.pools)} pools")
        except requests.exceptions.Timeout:
            LOG.error("Request to Raydium pool API timed out")
            self.get_pools()

    def get_token_list(self) -> None:
        """
        Get list of token with symbols from Orca API.
        """
        LOG.info("Fetching token info API")
        try:
            result = requests.get(
                "https://api.mainnet.orca.so/v1/token/list", timeout=30
            )
            decoded_result = result.content.decode("utf-8")
            self.token_list = json.loads(decoded_result)["tokens"]
        except requests.exceptions.Timeout:
            LOG.error("Request to token API timed out")
            self.get_token_list()

    def store_pools(self):
        """
        Save pools data to database.
        """
        self.get_token_list()
        for pool in self.pools:
            self.store_pool(pool)

    def store_pool(self, pool: Dict[str, Any]) -> None:
        """
        Save pool data to database.
        """
        market_address = pool.get("id", "Unknown")

        # get token symbols
        try:
            token_x_symbol = next(
                i for i in self.token_list if i["mint"] == pool["mintA"]
            ).get("symbol")
        except StopIteration:
            token_x_symbol = "Unknown"
        try:
            token_y_symbol = next(
                i for i in self.token_list if i["mint"] == pool["mintB"]
            ).get("symbol")
        except StopIteration:
            token_y_symbol = "Unknown"

        pair = f"{token_x_symbol}-{token_y_symbol}"

        # Create a new AmmLiquidity record
        with get_db_session() as session:
            liquidity_entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                pair=pair,
                market_address=market_address,
                additional_info=json.dumps(pool),
            )

            # Add the new record to the session and commit
            session.add(liquidity_entry)
            session.commit()


class MeteoraAMM(Amm):
    DEX_NAME = "Meteora"

    def get_pools(self):
        """
        Fetches pool data from the Meteora API and stores it in the `pools` attribute.
        """
        LOG.info("Fetching pools from Meteora API")
        try:
            response = requests.get("https://app.meteora.ag/amm/pools/", timeout=30)
            decoded_content = response.content.decode("utf-8")
            self.pools = json.loads(decoded_content)
            LOG.info(f"Successfully fetched {len(self.pools)} pools")
        except requests.exceptions.Timeout:
            LOG.error("Request to Meteora pool API timed out")
            self.get_pools()

    def store_pool(self, pool: Dict[str, Any]) -> None:
        """
        Save pool data to database.
        """
        pair = pool["pool_name"]
        token_x_amount, token_y_amount = pool.get("pool_token_amounts", (None, None))[
            :2
        ]

        # Convert amounts to BigInteger and decimals
        token_x, token_x_decimals = self.convert_to_big_integer_and_decimals(
            token_x_amount
        )
        token_y, token_y_decimals = self.convert_to_big_integer_and_decimals(
            token_y_amount
        )

        # Create the AmmLiquidity object
        with get_db_session() as session:
            liquidity_entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                pair=pair,
                market_address=pool.get("pool_address"),
                token_x=check_bigint(token_x) if token_x is not None else -1,
                token_y=check_bigint(token_y) if token_y is not None else -1,
                token_x_decimals=token_x_decimals
                if token_x_decimals is not None
                else -1,
                token_y_decimals=token_y_decimals
                if token_y_decimals is not None
                else -1,
                additional_info=json.dumps(pool),
            )

            # Add to session and commit
            session.add(liquidity_entry)
            session.commit()


class BonkAMM(Amm):
    DEX_NAME = "BONKSWAP"
    TICKERS: dict[str, dict[str, Any]] = {
        "BONK-USDC": {
            "market_address": "5MMaArf3NgUjaDqYZiwYP2wbXLd8myKmmYzBzzqdfYSb",
            "token_x_decimals": 5,
            "token_y_decimals": 6,
        },
        "BONK-SOL": {
            "market_address": "GBmzQL7BTKwSV9Qg7h5iXQad1q61xwMSzMpdbBkCyo2p",
            "token_x_decimals": 5,
            "token_y_decimals": 9,
        },
        "BONK-bSOL": {
            "market_address": "HxhY3cDvaHDnsv7JhdeVPNYPjDSeTcKhnpLuZyfPXYwc",
            "token_x_decimals": 5,
            "token_y_decimals": 9,
        },
        "BONK-mSOL": {
            "market_address": "Fji6MQKCxUbaTQQHPx3uxymAG6EKodCYphatx9JYeY2R",
            "token_x_decimals": 5,
            "token_y_decimals": 9,
        },
        "BONK-HXRO": {
            "market_address": "3siFX23uETx7pfMgW8ZAN8GZLdkT1b8fzhXQmuDoKjCB",
            "token_x_decimals": 5,
            "token_y_decimals": 8,
        },
    }

    async def get_pools(self):  # pylint: disable=W0236
        self.pools: list[tuple[str, BonkPool]] = []

        for ticker, pool_info in self.TICKERS.items():
            pool = await BonkPool.fetch(
                AsyncClient(AUTHENTICATED_RPC_URL),
                Pubkey.from_string(pool_info["market_address"]),
            )
            if not pool:
                LOG.error(f"No pool found for address: {pool_info['market_address']}")
                continue

            self.pools.append((ticker, pool))

        LOG.info(f"Fetched BonkSwap pools: {[i[0] for i in self.pools]}")

    def store_pool(self, pool: tuple[str, BonkPool]):

        ticker, pool_info = pool

        with get_db_session() as session:
            entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                pair=ticker,
                market_address=self.TICKERS[ticker]["market_address"],
                token_x=pool_info.token_x_reserve.v,
                token_y=pool_info.token_y_reserve.v,
                token_x_decimals=self.TICKERS[ticker]["token_x_decimals"],
                token_y_decimals=self.TICKERS[ticker]["token_y_decimals"],
                additional_info="{}",
            )

            # Add to session
            session.add(entry)

            #  Commit
            session.commit()


class DooarAMM(Amm):
    DEX_NAME = "DOOAR"
    TICKERS = {
        "SOL-USDC": {
            "token_x_account": Pubkey.from_string(
                "GVfKYBNMdaER21wwuqa4CSQV8ajVpuPbNZVV3wcuKWhE"
            ),
            "token_y_account": Pubkey.from_string(
                "ARryk4nSoS6bu7nyv6BgQah8oU23svFm7Rek7kR4fy3X"
            ),
        }
    }

    def get_pools(self):
        self.pools: list[tuple[str, dict[str, Any]]] = []
        client = Client(AUTHENTICATED_RPC_URL)

        for ticker, pool_info in self.TICKERS.items():
            token_x_acc = client.get_account_info_json_parsed(
                pool_info["token_x_account"]
            )
            token_y_acc = client.get_account_info_json_parsed(
                pool_info["token_y_account"]
            )

            if not token_x_acc.value:
                LOG.warning(f"No value found for X of {self.DEX_NAME}:{ticker}")
                continue

            if not token_y_acc.value:
                LOG.warning(f"No value found for Y of {self.DEX_NAME}:{ticker}")
                continue

            token_x_data = token_x_acc.value.data
            token_y_data = token_y_acc.value.data

            if not isinstance(token_x_data, ParsedAccount):
                LOG.warning(f"Unable to parse X of {self.DEX_NAME}:{ticker}")
                continue

            if not isinstance(token_y_data, ParsedAccount):
                LOG.warning(f"Unable to parse Y of {self.DEX_NAME}:{ticker}")
                continue

            token_x_parsed: dict = token_x_data.parsed
            token_y_parsed: dict = token_y_data.parsed

            token_x_amt = token_x_parsed["info"]["tokenAmount"]["amount"]
            token_y_amt = token_y_parsed["info"]["tokenAmount"]["amount"]

            token_x_decimals = token_x_parsed["info"]["tokenAmount"]["decimals"]
            token_y_decimals = token_y_parsed["info"]["tokenAmount"]["decimals"]

            self.pools.append(
                (
                    ticker,
                    {
                        "token_x_amount": token_x_amt,
                        "token_y_amount": token_y_amt,
                        "token_x_decimals": token_x_decimals,
                        "token_y_decimals": token_y_decimals,
                    },
                )
            )

    def store_pool(self, pool: tuple[str, dict[str, Any]]):

        ticker, pool_info = pool

        with get_db_session() as session:
            entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                pair=ticker,
                market_address="",
                token_x=pool_info["token_x_amount"],
                token_y=pool_info["token_y_amount"],
                token_x_decimals=pool_info["token_x_decimals"],
                token_y_decimals=pool_info["token_y_decimals"],
                additional_info="{}",
            )

            # Add to session
            session.add(entry)

            #  Commit
            session.commit()


async def main():
    amms = Amms()
    while True:
        try:
            await amms.update_pools()
            LOG.info(
                "Successfully processed all pools. Waiting 5 minutes before next update."
            )
            time.sleep(300)
        except Exception as e:  # pylint: disable=broad-exception-caught
            tb_str = traceback.format_exc()
            # Log the error message along with the traceback
            LOG.error(f"An error occurred: {e}\nTraceback:\n{tb_str}")
            time.sleep(300)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    LOG.info("Start collecting AMM pools.")
    asyncio.run(main())
