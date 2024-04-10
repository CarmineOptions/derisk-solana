from dataclasses import dataclass
from decimal import Decimal

import numpy as np

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
    """
    Differentiates list of cumulative price levels in order to tell how much
    liquidity is present at specific price.

    Parameters:
    - cum_levels (list[PriceLevel]) : List of cumulative price levels.

    Returns:
    - diffed levels (list[PriceLevels]) : List of differentiated price levels.
    """
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


def get_amm_delta_x(x1: Decimal, y1: Decimal, target_price: Decimal) -> Decimal:
    """
    For given amount of x and y calculates the change of amount of X token
    that will occur in order to move to the target price.

    Formulas present in the .md file in same directory as this file.

    Parameters:
    - x1 (Decimal)           : Amount of X reserves in the pool
    - y1 (Decimal)           : Amount of Y reserves in the pool
    - target_price (Decimal) : Target price for which to calculate the X amount change.

    Returns:
    - delta x (Decimal) : Change in X token amount.
    """
    return ((x1 * y1) / target_price).sqrt() - x1


def get_amm_delta_y(x1: Decimal, y1: Decimal, target_price: Decimal) -> Decimal:
    """
    For given amount of x and y calculates the change of amount of Y token
    that will occur in order to move to the target price.

    Formulas present in the .md file in same directory as this file.

    Parameters:
    - x1 (Decimal)           : Amount of X reserves in the pool
    - y1 (Decimal)           : Amount of Y reserves in the pool
    - target_price (Decimal) : Target price for which to calculate the Y amount change.

    Returns:
    - delta x (Decimal) : Change in X token amount.
    """
    delta_x = get_amm_delta_x(x1, y1, target_price)
    return ((x1 * y1) / (x1 + delta_x)) - y1


def convert_amm_reserves_to_bids_asks(
    x_reserves: Decimal, y_reserves: Decimal
) -> dict[str, list[PriceLevel]]:
    """
    Converts AMM data (y_reserves, x_reserves) to OB-like data (bids, asks).
    Only calculates it +-10% around current pool price.

    Bids and asks both denominated in X (base) token.

    Formulas present in the .md file in same directory as this file.

    Parameters:
    - y_reserves (Decimal) : Amount of Y token in the pool.
    - x_reserves (Decimal) : Amount of X token in the pool.

    Returns:
    - dict : Dict with two keys ('bids' and 'asks') containing available liquidity at
            given price levels (+-10% of current price).
    """

    # Price
    current_price = y_reserves / x_reserves

    # Generate list of price changes -+10%
    percentage_changes = np.linspace(0.001, 0.1, 100)
    price_percentage_changes_up = 1 + percentage_changes
    price_percentage_changes_down = 1 - percentage_changes

    # Generate lists of new target prices in up direction and down direction
    prices_up = [current_price * Decimal(str(i)) for i in price_percentage_changes_up]
    prices_down = [
        current_price * Decimal(str(i)) for i in price_percentage_changes_down
    ]

    asks = [
        PriceLevel(
            price=target_price,
            amount=abs(get_amm_delta_x(x_reserves, y_reserves, target_price)),
        )
        for target_price in prices_up
    ]

    bids = [
        PriceLevel(
            price=target_price,
            amount=get_amm_delta_x(x_reserves, y_reserves, target_price),
        )
        for target_price in prices_down
    ]

    return {"asks": diff_price_levels(asks), "bids": diff_price_levels(bids)}