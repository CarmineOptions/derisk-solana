from dataclasses import dataclass
from decimal import Decimal

from solana.rpc.async_api import AsyncClient
from solders.account_decoder import ParsedAccount
from solders.pubkey import Pubkey


@dataclass
class PriceLevel:
    price: Decimal
    amount: Decimal


async def get_mint_decimals(mint: Pubkey, client: AsyncClient) -> int:
    account_info = await client.get_account_info_json_parsed(mint)

    if not account_info.value:
        raise ValueError(f"No value found for account: {mint}")

    account_info_data = account_info.value.data

    if not isinstance(account_info_data, ParsedAccount):
        raise ValueError(f"Unable to parse account: {mint}")

    decimals_parsed: dict = account_info_data.parsed
    decimals = decimals_parsed["info"]["decimals"]

    if not isinstance(decimals, int):
        raise ValueError(
            f"Expected decimals to be of type int, got {decimals} of type {type(decimals)}"
        )

    return int(decimals)


def diff_price_levels(cum_levels: list[PriceLevel]) -> list[PriceLevel]:
    return [
        (
            PriceLevel(
                price=level.price, amount=level.amount - cum_levels[ix - 1].amount
            )
            if ix != 0
            else level
        )
        for ix, level in enumerate(cum_levels)
    ]
