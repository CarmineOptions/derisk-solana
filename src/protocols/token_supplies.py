import os
import traceback
import time
from datetime import datetime
from dataclasses import dataclass
import asyncio
import logging
import abc
from decimal import Decimal
from typing import Any
import requests

from anchorpy.borsh_extension import BorshPubkey
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey
from solders.account_decoder import ParsedAccount
import borsh_construct as borsh
from construct.lib import Container

import db

from src.protocols.anchor_clients.marginfi_client.accounts.bank import (
    Bank as MarginfiBank,
)

from src.protocols.anchor_clients.kamino_client.accounts.lending_market import (
    LendingMarket as KaminoLendingMarket,
)
from src.protocols.anchor_clients.kamino_client.accounts.reserve import (
    Reserve as KaminoReserve,
)

from src.protocols.anchor_clients.mango_client.accounts.bank import Bank as MangoBank


LOG = logging.getLogger(__name__)

COLLECT_INTERVAL_SECONDS = 5 * 60
AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")

LOG = logging.getLogger(__name__)


@dataclass
class Vault:
    address: str
    market: str | None
    mint_address: str
    deposits: Decimal
    lent: Decimal
    available_to_borrow: Decimal


class TokenSupplyCollector(abc.ABC):
    client = AsyncClient(AUTHENTICATED_RPC_URL)

    def __init__(self, identifier: str, address: str):
        self.identifier = identifier
        self.address = address
        self.markets: list[Any] = []

    def info_log(self, msg: str):
        LOG.info(f"{self.identifier}: {msg}")

    def error_log(self, msg: str):
        LOG.error(f"{self.identifier}: {msg}")

    def warning_log(self, msg: str):
        LOG.warning(f"{self.identifier}: {msg}")

    def upload_token_supplies(self, entries: list[db.TokenLendingSupplies]) -> None:
        with db.get_db_session() as session:
            session.add_all(entries)
            session.commit()

    async def get_token_supplies(self, timestamp: int) -> list[db.TokenLendingSupplies]:
        vaults = await self.get_vaults()

        if len(vaults) == 0:
            self.info_log(f"Zero vaults received, len markets: {len(self.markets)}")

        return [
            db.TokenLendingSupplies(
                timestamp=timestamp,
                protocol_id=str(self.address),
                market=str(vault.market),
                vault=str(vault.address),
                underlying_mint_address=str(vault.mint_address),
                deposits_total=vault.deposits,  # type: ignore
                lent_total=vault.lent,  # type: ignore
                available_to_borrow=vault.available_to_borrow,  # type: ignore
            )
            for vault in vaults
        ]

    async def update_token_supplies(self, timestamp: int) -> None:
        try:
            entries = await self.get_token_supplies(timestamp)
            self.upload_token_supplies(entries)
        except Exception as err:  # pylint: disable=W0718
            err_msg = "".join(traceback.format_exception(err))
            self.error_log(f"Unable to update token supplies, reason:\n {err_msg}")
            
            time.sleep(30)
            self.update_token_supplies()

    async def collect_markets(self):
        try: 
            await self._collect_markets()
        except requests.exceptions.ReadTimeout:
            self.error_log("Received ReadTimeout when collecting markets, repeating in 30 seconds.")
            time.sleep(30)
            self.collect_markets()

    @abc.abstractmethod
    async def _collect_markets(self):
        """Implement me"""

    @abc.abstractmethod
    async def get_vaults(self) -> list[Vault]:
        """Implement me"""


class MarginfiTokenSupplyCollector(TokenSupplyCollector):
    @staticmethod
    async def get_bank(
        client: AsyncClient, bank_address: Pubkey
    ) -> None | MarginfiBank:
        return await MarginfiBank.fetch(client, bank_address)

    async def get_vault_single(self, bank_address: Pubkey) -> Vault | None:
        bank = await self.get_bank(self.client, bank_address)

        if not bank:
            self.error_log(f"Unable to fetch Bank: {str(bank_address)}")
            return None

        asset_shares = Decimal(bank.total_asset_shares.value) / 2**48
        asset_share_value = Decimal(bank.asset_share_value.value) / 2**48
        assets = asset_shares * asset_share_value

        liability_shares = Decimal(bank.total_liability_shares.value) / 2**48
        liability_share_value = Decimal(bank.liability_share_value.value) / 2**48
        liabilities = liability_shares * liability_share_value

        total_available = min(
            assets - liabilities, bank.config.borrow_limit - liabilities
        )

        return Vault(
            address=str(bank_address),
            market=str(bank.group),
            mint_address=str(bank.mint),
            deposits=assets,
            lent=liabilities,
            available_to_borrow=total_available,
        )

    async def _collect_markets(self):
        response = requests.get(
            "https://storage.googleapis.com/mrgn-public/mrgn-bank-metadata-cache.json",
            timeout=30,
        )

        if response.status_code != 200:
            self.error_log(f"Unable to fetch banks: {response.text}")
            time.sleep(30)
            self._collect_markets()
            return

        self.markets = response.json()

    async def get_vaults(self) -> list[Vault]:

        tasks = [
            self.get_vault_single(Pubkey.from_string(i["bankAddress"]))
            for i in self.markets
        ]

        awaited_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        vaults = [vault for vault in awaited_tasks if isinstance(vault, Vault)]

        if len(tasks) != len(vaults):
            # This means there were some failures
            errors = [vault for vault in awaited_tasks if not isinstance(vault, Vault)]

            # Log amount of errors
            if errors:
                self.error_log(
                    f"Was unable to fetch {len(errors)} out of {len(tasks)} vaults, example: {errors[0]}"
                )

        return vaults


class KaminoTokenSupplyCollector(TokenSupplyCollector):
    @staticmethod
    async def get_lending_market(
        client: AsyncClient, address: Pubkey
    ) -> KaminoLendingMarket | None:
        return await KaminoLendingMarket.fetch(client, address)

    @staticmethod
    async def get_reserve(client: AsyncClient, address: Pubkey) -> KaminoReserve | None:
        return await KaminoReserve.fetch(client, address)

    async def _collect_markets(self):
        r = requests.get("https://api.hubbleprotocol.io/v2/kamino-market", timeout=30)

        if r.status_code != 200:
            self.error_log(f"Unable to fetch banks: {r.text}")
            time.sleep(30)
            self._collect_markets()
            return

        kamino_markets = []

        for market in r.json():
            address = Pubkey.from_string(market["lendingMarket"])
            lending_market = await self.get_lending_market(self.client, address)

            if not lending_market:
                self.error_log(f"Unable to fetch LendingMarket {str(address)}")
                continue

            kamino_markets.append({"address": address, "market": lending_market})

        self.markets = kamino_markets

    async def get_markets_with_reserves(self):

        for market in self.markets:

            filters = [
                KaminoReserve.layout.sizeof() + 8,
                MemcmpOpts(32, str(market["address"])),
            ]

            market_accounts = await self.client.get_program_accounts(
                Pubkey.from_string(self.address), encoding="base64", filters=filters
            )

            if not market_accounts.value:
                self.error_log(
                    f'Unable to fetch market accounts for: {market["address"]}'
                )
                continue

            market_reserves = [
                {"address": i.pubkey, "info": KaminoReserve.decode(i.account.data)}
                for i in market_accounts.value
            ]

            market["reserves"] = market_reserves

        return self.markets

    async def get_vaults(self):

        kamino_markets = await self.get_markets_with_reserves()
        vaults = []

        for market in kamino_markets:
            for reserve in market["reserves"]:
                available_assets = Decimal(reserve["info"].liquidity.available_amount)
                liabilities = (
                    Decimal(reserve["info"].liquidity.borrowed_amount_sf) / 2**60
                )
                assets = available_assets + liabilities
                total_available = min(
                    assets - liabilities,
                    reserve["info"].config.borrow_limit - liabilities,
                )

                vault = Vault(
                    address=reserve["address"],
                    market=market["address"],
                    mint_address=reserve["info"].liquidity.mint_pubkey,
                    deposits=assets,
                    lent=liabilities,
                    available_to_borrow=total_available,
                )
                vaults.append(vault)

        return vaults


RateLimiterLayout = borsh.CStruct(
    "maxOutflow" / borsh.U64,
    "windowDuration" / borsh.U64,
    "previousQuantity" / borsh.U128,
    "windowStart" / borsh.U64,
    "currentQuantity" / borsh.U128,
)

LastUpdateLayout = borsh.CStruct("slot" / borsh.U64, "stale" / borsh.U8)

SolendReserveLayout = borsh.CStruct(
    "version" / borsh.U8,
    "last_update" / LastUpdateLayout,
    "lendingMarket" / BorshPubkey,
    "liquidityMintPubkey" / BorshPubkey,
    "liquidityMintDecimals" / borsh.U8,
    "liquiditySupplyPubkey" / BorshPubkey,
    "liquidityPythOracle" / BorshPubkey,
    "liquiditySwitchboardOracle" / BorshPubkey,
    "liquidityAvailableAmount" / borsh.U64,
    "liquidityBorrowedAmountWads" / borsh.U128,
    "liqudityCumulativeBorrowRateWads" / borsh.U128,
    "liqudityMarketPrice" / borsh.U128,
    "collateralMintPubkey" / BorshPubkey,
    "collateralMintTotalSupply" / borsh.U64,
    "collateralSupplyPubkey" / BorshPubkey,
    "optimalUtilizationRate" / borsh.U8,
    "loanToValueRatio" / borsh.U8,
    "liquidationBonus" / borsh.U8,
    "liquidationThreshold" / borsh.U8,
    "minBorrowRate" / borsh.U8,
    "optimalBorrowRate" / borsh.U8,
    "maxBorrowRate" / borsh.U8,
    "borrowFeeWad" / borsh.U64,
    "flashLoanFeeWad" / borsh.U64,
    "hostFeePercentage" / borsh.U8,
    "depositLimit" / borsh.U64,
    "borrowLimit" / borsh.U64,
    "feeReceiver" / BorshPubkey,
    "protocolLiquidationFee" / borsh.U8,
    "protocolTakeRate" / borsh.U8,
    "accumulatedProtocolFeesWads" / borsh.U128,
    "rate_limiter" / RateLimiterLayout,
    "addedBorrowWeightBPS" / borsh.U64,
    "liquiditySmoothedMarketPrice" / borsh.U128,
    "reserveType" / borsh.U8,
    "maxUtilizationRate" / borsh.U8,
    "superMaxBorrowRate" / borsh.U64,
    "maxLiquidationBonus" / borsh.U8,
    "maxLiquidationThreshold" / borsh.U8,
    # "padding" / borsh.U8[64]
)


class SolendTokenSupplyCollector(TokenSupplyCollector):
    @staticmethod
    async def get_reserve(client: AsyncClient, address: Pubkey) -> Container | None:
        fetched = await client.get_account_info(address)
        if not fetched.value:
            return None

        return SolendReserveLayout.parse(fetched.value.data)

    async def _collect_markets(self):
        base = "https://api.solend.fi"
        resp = requests.get(
            base + "/v1/markets/configs?scope=all&deployment=production", timeout=30
        )

        if resp.status_code != 200:
            self.error_log("Unable to update markets")

            time.sleep(30)
            self._collect_markets()
            return

        self.markets = resp.json()

    async def get_vault_single(self, address: Pubkey, market: Pubkey) -> Vault | None:

        reserve = await self.get_reserve(self.client, address)

        if not reserve:
            self.error_log(f"Unable to fetch reserve: {address}")
            return None

        liabilities = Decimal(reserve.liquidityBorrowedAmountWads) / 10**18
        assets = Decimal(reserve.liquidityAvailableAmount) + liabilities

        total_available = min(assets - liabilities, reserve.borrowLimit - liabilities)

        vault = Vault(
            address=str(address),
            market=str(market),
            mint_address=str(reserve.liquidityMintPubkey),
            deposits=assets,
            lent=liabilities,
            available_to_borrow=total_available,
        )

        return vault

    async def get_vaults(self) -> list[Vault]:
        vaults = []

        for market in self.markets:
            market_addr = market["address"]

            reserves = [i["address"] for i in market["reserves"]]

            tasks = [
                self.get_vault_single(Pubkey.from_string(i), market_addr)
                for i in reserves
            ]

            awaited_tasks = await asyncio.gather(*tasks, return_exceptions=True)

            _vaults = [vault for vault in awaited_tasks if isinstance(vault, Vault)]

            if len(tasks) != len(_vaults):
                errors = [
                    vault for vault in awaited_tasks if not isinstance(vault, Vault)
                ]

                self.error_log(
                    f"Was unable to fetch {len(errors)} out of {len(tasks)} vaults, example: {errors[0]}"
                )

            vaults += _vaults

        return vaults


class MangoTokenSupplyCollector(TokenSupplyCollector):
    @staticmethod
    async def get_bank(client: AsyncClient, address: Pubkey) -> MangoBank | None:
        return await MangoBank.fetch(client, address)

    async def _collect_markets(self):

        r = requests.get("https://api.mngo.cloud/data/v4/group-metadata", timeout=30)

        if r.status_code != 200:
            self.error_log("Unable to fetch markets")
            time.sleep(30)
            self._collect_markets()
            return

        self.markets = r.json()["groups"]

    async def get_vault_single(
        self, market_address: Pubkey, bank_address: Pubkey
    ) -> Vault | None:
        bank = await self.get_bank(self.client, bank_address)

        if not bank:
            self.error_log(f"Unable to fetch bank: {bank_address}")
            return None

        deposits = (Decimal(bank.indexed_deposits.val) / 2**48) * (
            Decimal(bank.deposit_index.val) / 2**48
        )
        liabs = (Decimal(bank.indexed_borrows.val) / 2**48) * (
            Decimal(bank.borrow_index.val) / 2**48
        )

        supply_vault = await self.client.get_account_info_json_parsed(bank.vault)
        if not supply_vault.value:
            self.error_log(f"Unable to fetch vault: {bank.vault}")
            return None

        if not isinstance(supply_vault.value.data, ParsedAccount):
            self.error_log(f"Unable to parse account: {bank_address}")
            return None

        parsed_vault: dict = supply_vault.value.data.parsed

        balance = Decimal(parsed_vault["info"]["tokenAmount"]["amount"])
        min_vault_to_deposit_ratio = Decimal(str(bank.min_vault_to_deposits_ratio))

        available_to_borrow = balance - (deposits * min_vault_to_deposit_ratio)

        vault = Vault(
            address=str(bank_address),
            market=str(market_address),
            mint_address=str(bank.mint),
            deposits=deposits,
            lent=liabs,
            available_to_borrow=available_to_borrow,
        )
        return vault

    async def get_vaults(self) -> list[Vault]:
        vaults = []

        for group in self.markets:
            market_address = group["publicKey"]
            banks = [i["banks"][0]["publicKey"] for i in group["tokens"]]
            tasks = [
                self.get_vault_single(market_address, Pubkey.from_string(i))
                for i in banks
            ]
            awaited_tasks = await asyncio.gather(*tasks, return_exceptions=True)

            _vaults = [vault for vault in awaited_tasks if isinstance(vault, Vault)]

            if len(tasks) != len(_vaults):
                # This means there were some failures
                errors = [
                    vault for vault in awaited_tasks if not isinstance(vault, Vault)
                ]

                # Log amount of errors
                self.error_log(
                    f"Was unable to fetch {len(errors)} out of {len(tasks)} vaults, example: {errors[0]}"
                )

            vaults += _vaults

        return vaults


async def update_token_supplies_continuously():

    # Initialize list of token Supply Collectors
    collectors: list[TokenSupplyCollector] = [
        MarginfiTokenSupplyCollector(
            "Marginfi", "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA"
        ),
        KaminoTokenSupplyCollector(
            "Kamino", "KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD"
        ),
        SolendTokenSupplyCollector(
            "Solend", "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo"
        ),
        MangoTokenSupplyCollector(
            "Solend", "4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg"
        ),
    ]

    # Update lists of markets
    for prot in collectors:
        await prot.collect_markets()

    # Main loop
    while True:
        time_start = time.time()
        LOG.info("Starting collection")

        # Once every 12 hours, update list of markets
        if datetime.now().hour % 12 == 0:
            for prot in collectors:
                await prot.collect_markets()

        for prot in collectors:
            await prot.update_token_supplies(int(time_start))

        execution_time = time.time() - time_start

        if execution_time <= COLLECT_INTERVAL_SECONDS:
            LOG.info(f"Collected token supplies in {execution_time} seconds")
        else:
            LOG.warning(f"Collected token supplies in {execution_time} seconds")

        LOG.info(
            f"Sleeping {max(0, COLLECT_INTERVAL_SECONDS - execution_time)} seconds."
        )

        time.sleep(max(0, COLLECT_INTERVAL_SECONDS - execution_time))
