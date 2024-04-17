from decimal import Decimal
from dataclasses import dataclass
import os

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from requests import get

from src.protocols.anchor_clients.marginfi_client.accounts import Bank
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map


@dataclass
class MarginfiLoanParameters:
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


async def get_marginfy_loan_parameters(token_address: str) -> MarginfiLoanParameters | None:
    """
    Fetches Marginfi configuration and parses loan parameters from it

    Arguments:
      token_address (str): Address of the token for which we need the data

    Returns:
      MarginfiLoanParameters | None: DataClass with liability and asset data or None if bank for token does not exist
    """
    banks: list[dict] = get(
        "https://storage.googleapis.com/mrgn-public/mrgn-bank-metadata-cache.json",
        timeout=10,
    ).json()

    bank_address: str | None = None

    for bank in banks:
        if bank.get("tokenAddress") == token_address:
            bank_address = bank.get("bankAddress")

    if bank_address is None:
        return None

    b = await Bank.fetch(client, Pubkey.from_string(bank_address))

    if b is None:
        return None

    return MarginfiLoanParameters(
        Decimal(b.config.liability_weight_init.value) / BASE,
        Decimal(b.config.liability_weight_maint.value) / BASE,
        Decimal(b.config.asset_weight_init.value) / BASE,
        Decimal(b.config.asset_weight_maint.value) / BASE,
    )
