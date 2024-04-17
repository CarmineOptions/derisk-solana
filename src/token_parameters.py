import asyncio
from decimal import Decimal
from dataclasses import dataclass
import os
from requests import get
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import MemcmpOpts
from solders.pubkey import Pubkey


from src.protocols.anchor_clients.kamino_client.accounts.lending_market import (
    LendingMarket,
)
from src.protocols.anchor_clients.kamino_client.accounts.reserve import Reserve
from src.protocols.anchor_clients.marginfi_client.accounts import Bank
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map


@dataclass
class MarginfyBankParameters:
    liability_weight_initial: Decimal
    liability_weight_maintain: Decimal
    asset_weight_initial: Decimal
    asset_weight_maintain: Decimal


AUTHENTICATED_RPC_URL = os.getenv("AUTHENTICATED_RPC_URL")
MARGINFI_BANK_PUBKEY = "9dpu8KL5ABYiD3WP2Cnajzg1XaotcJvZspv29Y1Y3tn1"
BASE = 2**48

if AUTHENTICATED_RPC_URL is None:
    raise KeyError("No AUTHENTICATED_RPC_URL env var")

client = AsyncClient(AUTHENTICATED_RPC_URL)
tokens = get_tokens_address_to_info_map()


async def get_single_marginfy_parameters(bank: str) -> MarginfyBankParameters | None:
    b = await Bank.fetch(client, Pubkey.from_string(bank))

    if b is None:
        return None

    return MarginfyBankParameters(
        Decimal(b.config.liability_weight_init.value) / BASE,
        Decimal(b.config.liability_weight_maint.value) / BASE,
        Decimal(b.config.asset_weight_init.value) / BASE,
        Decimal(b.config.asset_weight_maint.value) / BASE,
    )


async def get_marginfy_loan_parameters(
    mints: list[str],
) -> dict[str, MarginfyBankParameters | None]:
    """
    Fetches Marginfi configuration and parses loan parameters from it

    Arguments:
      mint_address (str): Address of the token for which we need the data

    Returns:
      MarginfyBankParameters | None: DataClass with liability and asset data or None if bank for token does not exist
    """
    banks: list[dict] = get(
        "https://storage.googleapis.com/mrgn-public/mrgn-bank-metadata-cache.json",
        timeout=10,
    ).json()

    mint_bank_map: dict[str, MarginfyBankParameters | None] = {}

    for mint in mints:
        bank = next((bank["bankAddress"] for bank in banks if bank["tokenAddress"] == mint), None)

        mint_bank_map[mint] = bank

    tasks = [get_single_marginfy_parameters(bank) for bank in mint_bank_map.values()]
    results = await asyncio.gather(*tasks)
    processed_results = dict(zip(mint_bank_map.keys(), results))

    return processed_results


async def get_kamino_reserves() -> dict[str, Reserve]:
    kamino_id = Pubkey.from_string("KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD")

    markets: list[dict] = get(
        "https://api.hubbleprotocol.io/v2/kamino-market",
        timeout=10,
    ).json()

    kamino_markets = [
        {
            "address": Pubkey.from_string(i["lendingMarket"]),
            "market": await LendingMarket.fetch(
                client, Pubkey.from_string(i["lendingMarket"])
            ),
        }
        for i in markets
    ]

    reserves: dict[str, Reserve] = {}

    for market in kamino_markets:
        filters = [Reserve.layout.sizeof() + 8, MemcmpOpts(32, str(market["address"]))]

        market_accounts = await client.get_program_accounts(
            kamino_id, encoding="base64", filters=filters
        )

        for i in market_accounts.value:
            pubkey = str(i.pubkey)
            reserve = Reserve.decode(i.account.data)
            reserves[pubkey] = reserve

    return reserves


@dataclass
class KaminoReserveParameters:
  loan_to_value: Decimal


def kamino_reserve_to_parameters(reserve: Reserve) -> KaminoReserveParameters:
    # TODO: add more relevant data to KaminoReserveParameters
    loan_to_value = Decimal(reserve.config.loan_to_value_pct / 100)
    return KaminoReserveParameters(loan_to_value)

async def get_kamino_loan_parameters(reserve_pubkeys: list[str]) -> dict[str, KaminoReserveParameters | None]:
    """
    Fetches Kamino configuration and parses loan parameters from it.

    Arguments:
      reserve_pubkeys (list[str]): Kamino reserve Pubkey list.

    Returns:
      dict[str, KaminoReserveParameters | None]: Reserve to KaminoReserveParameters map, None if no reserve for given pubkey
    """
    reserves = await get_kamino_reserves()

    pubkey_reserve_parameters_map: dict[str, KaminoReserveParameters | None] = {}

    for key in reserve_pubkeys:
        reserve = reserves.get(key)

        if reserve is not None:
            pubkey_reserve_parameters_map[key] = kamino_reserve_to_parameters(reserve)
        else:
            pubkey_reserve_parameters_map[key] = None


    return pubkey_reserve_parameters_map
