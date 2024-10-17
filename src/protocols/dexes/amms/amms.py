"""
Module dedicated to fetching and storing data from AMM pools.
"""

from typing import Any, Dict, List
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

from src.protocols.dexes.amms.amm import Amm
from src.protocols.dexes.amms.orca import OrcaAMM
from src.protocols.anchor_clients.bonkswap_client.accounts import Pool as BonkPool
from db import AmmLiquidity, get_db_session, check_bigint

AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")

LOG = logging.getLogger(__name__)

class Amms:
    """
    A class that describes the state of all relevant pools of all relevant swap AMMs.
    """

    def __init__(self, amms: list[Amm]) -> None:
        self.amms = amms

    async def update_pools(self) -> None:
        """
        Save pools data to database.
        :return:
        """
        # set timestamp
        timestamp = int(time.time())

        for amm in self.amms:
            # collect and store pools
            amm.timestamp = timestamp
            await amm.get_pools()
            amm.store_pools()


class RaydiumAMM(Amm):
    DEX_NAME = "Raydium"
    token_list: List

    async def get_pools(self):
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
            break

    def store_pool(self, pool: Dict[str, Any]) -> None:
        """
        Save pool data to database.
        """

        # Create a new AmmLiquidity record
        with get_db_session() as session:
            for pool in self.pools:
                market_address = pool.get("id", "Unknown")
            
                liquidity_entry = AmmLiquidity(
                    timestamp=self.timestamp,
                    dex=self.DEX_NAME,
                    market_address=market_address,
                    token_x_address= pool['mintA'],
                    token_y_address= pool['mintB'],
                    additional_info=json.dumps(pool),
                )
                session.add(liquidity_entry)

            # Add the new record to the session and commit
            session.commit()


class MeteoraAMM(Amm):
    DEX_NAME = "Meteora"

    async def get_pools(self):
        """
        Fetches pool data from the Meteora API and stores it in the `pools` attribute.
        """
        LOG.info("Fetching pools from Meteora API")
        try:
            response = requests.get("https://app.meteora.ag/amm/pools/", timeout=30)
            decoded_content = response.content.decode("utf-8")
            self.pools = json.loads(decoded_content)
            self.pools = [
                pool for pool in self.pools
                if len(pool['pool_token_mints']) == 2
            ]
            self.pools = [
                pool for pool in self.pools 
                if pool['weekly_trading_volume'] > 500
            ]
            LOG.info(f"Successfully fetched {len(self.pools)} pools")
        except requests.exceptions.Timeout:
            LOG.error("Request to Meteora pool API timed out")
            self.get_pools()

    def store_pool(self, pool: Dict[str, Any]) -> None:
        """
        Save pool data to database.
        """
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

        pool.update({
            'token_x_decimals': token_x_decimals,
            'token_y_decimals': token_y_decimals
        })

        # Create the AmmLiquidity object
        with get_db_session() as session:
            liquidity_entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                market_address=pool.get("pool_address"),
                token_x_amount=check_bigint(token_x) if token_x is not None else -1,
                token_y_amount=check_bigint(token_y) if token_y is not None else -1,
                token_x_address = pool['pool_token_mints'][0],
                token_y_address = pool['pool_token_mints'][1],
                additional_info=json.dumps(pool),
            )

            # Add to session and commit
            session.add(liquidity_entry)
            session.commit()


class BonkAMM(Amm):
    DEX_NAME = "BonkSwap"
    POOLS_INFO: dict[str, dict[str, str | int]] = {
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

        for ticker, pool_info in self.POOLS_INFO.items():
            pool = await BonkPool.fetch(
                AsyncClient(AUTHENTICATED_RPC_URL),
                Pubkey.from_string(str(pool_info["market_address"])),
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
                market_address=str(self.POOLS_INFO[ticker]["market_address"]),
                token_x_amount=pool_info.token_x_reserve.v,
                token_y_amount=pool_info.token_y_reserve.v,
                token_x_address=str(pool_info.token_x),
                token_y_address=str(pool_info.token_y),
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

    async def get_pools(self):
        self.pools: list[tuple[str, dict[str, Any]]] = []
        client = Client(AUTHENTICATED_RPC_URL)

        for ticker, pool_info in self.TICKERS.items():
            token_x_account = client.get_account_info_json_parsed(
                pool_info["token_x_account"]
            )
            token_y_account = client.get_account_info_json_parsed(
                pool_info["token_y_account"]
            )

            if not token_x_account.value:
                LOG.warning(f"No value found for token X of {self.DEX_NAME}:{ticker}")
                continue

            if not token_y_account.value:
                LOG.warning(f"No value found for token Y of {self.DEX_NAME}:{ticker}")
                continue

            token_x_data = token_x_account.value.data
            token_y_data = token_y_account.value.data

            if not isinstance(token_x_data, ParsedAccount):
                LOG.warning(f"Unable to parse X of {self.DEX_NAME}:{ticker}")
                continue

            if not isinstance(token_y_data, ParsedAccount):
                LOG.warning(f"Unable to parse Y of {self.DEX_NAME}:{ticker}")
                continue

            token_x_parsed: dict = token_x_data.parsed
            token_y_parsed: dict = token_y_data.parsed

            token_x_amount = token_x_parsed["info"]["tokenAmount"]["amount"]
            token_y_amount = token_y_parsed["info"]["tokenAmount"]["amount"]

            token_x_mint = token_x_parsed["info"]["mint"]
            token_y_mint = token_y_parsed["info"]["mint"]

            self.pools.append(
                (
                    ticker,
                    {
                        "token_x_amount": token_x_amount,
                        "token_y_amount": token_y_amount,
                        "token_x_mint": token_x_mint,
                        "token_y_mint": token_y_mint,
                    },
                )
            )

    def store_pool(self, pool: tuple[str, dict[str, Any]]):

        _, pool_info = pool

        with get_db_session() as session:
            entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                market_address="",
                token_x_amount=pool_info["token_x_amount"],
                token_y_amount=pool_info["token_y_amount"],
                token_x_address=pool_info["token_x_mint"],
                token_y_address=pool_info["token_y_mint"],
                additional_info="{}",
            )

            # Add to session
            session.add(entry)

            #  Commit
            session.commit()


class FluxBeam(Amm):
    DEX_NAME = "FluxBeam"

    async def get_pools(self):  # pylint: disable=W0236
        LOG.info("Fetching FLUXBEAM pools.")
        client = AsyncClient(AUTHENTICATED_RPC_URL)

        with open("src/protocols/pools/fluxbeam_pools.json", "rb") as f:
            pool_infos = json.load(f)

        async def _fetch_pool(pool):
            return {
                "pool_info": pool,
                "tokenA": await client.get_account_info_json_parsed(
                    Pubkey.from_string(pool["tokenAccountA"])
                ),
                "tokenB": await client.get_account_info_json_parsed(
                    Pubkey.from_string(pool["tokenAccountB"])
                ),
            }

        tasks = [_fetch_pool(i) for i in pool_infos]

        # Separate tasks list into chunks so we don't exceed RPC limit
        chunk_size = 20
        tasks_chunks = [
            tasks[i : i + chunk_size] for i in range(0, len(tasks), chunk_size)
        ]

        self.pools = []
        for chunk in tasks_chunks:
            self.pools += await asyncio.gather(*chunk, return_exceptions=True)
            time.sleep(2)

    def store_pool(self, pool: dict[str, Any]) -> None:

        if isinstance(pool, Exception):
            LOG.error(f"FluxBeam error: {pool}")
            return

        token_x_account = pool["tokenA"]
        token_y_account = pool["tokenB"]

        if not token_x_account.value:
            LOG.warning(
                f"No value found for token X of {self.DEX_NAME}:{pool['pool_info']['ticker']}"
            )
            return

        if not token_y_account.value:
            LOG.warning(
                f"No value found for token Y of {self.DEX_NAME}:{pool['pool_info']['ticker']}"
            )
            return

        token_x_data = token_x_account.value.data
        token_y_data = token_y_account.value.data

        if not isinstance(token_x_data, ParsedAccount):
            LOG.warning(
                f"Unable to parse X of {self.DEX_NAME}:{pool['pool_info']['ticker']}"
            )
            return

        if not isinstance(token_y_data, ParsedAccount):
            LOG.warning(
                f"Unable to parse Y of {self.DEX_NAME}:{pool['pool_info']['ticker']}"
            )
            return

        token_x_parsed: dict = token_x_data.parsed
        token_y_parsed: dict = token_y_data.parsed

        token_x_amount = token_x_parsed["info"]["tokenAmount"]["amount"]
        token_y_amount = token_y_parsed["info"]["tokenAmount"]["amount"]

        token_x_mint = token_x_parsed["info"]["mint"]
        token_y_mint = token_y_parsed["info"]["mint"]

        with get_db_session() as session:
            entry = AmmLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                market_address=pool["pool_info"]["address"],
                token_x_amount=token_x_amount,
                token_y_amount=token_y_amount,
                token_x_address=token_x_mint,
                token_y_address=token_y_mint,
                additional_info="{}",
            )

            # Add to session
            session.add(entry)

            #  Commit
            session.commit()


async def update_amm_dex_data_continuously():
    LOG.info("Start collecting AMM pools.")
    while True:
        try:
            amms = Amms(
                [
                    OrcaAMM(),
                    MeteoraAMM(),
                    BonkAMM(),
                    DooarAMM(),
                    FluxBeam(),
                    RaydiumAMM(),
                ]
            )
            await amms.update_pools()
            LOG.info(
                "Successfully processed all pools. Waiting 5 minutes before next update."
            )
            time.sleep(1200)
        except Exception as e:  # pylint: disable=broad-exception-caught
            tb_str = traceback.format_exc()
            # Log the error message along with the traceback
            LOG.error(f"An error occurred: {e}\nTraceback:\n{tb_str}")
            time.sleep(1200)
