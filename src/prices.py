import datetime
import logging
from typing import TypeVar
import decimal
import requests

import streamlit

from src import kamino_vault_map

LOGGER = logging.getLogger(__name__)

BASE_API_URL = "https://api.jup.ag/price/v2"

T = TypeVar("T")


def split_into_chunks(lst: list[T], n: int) -> list[list[T]]:
    """
    Split a list into chunks of size n.

    Parameters:
        lst (list): The list to be split.
        n (int): The size of each chunk.

    Returns:
        list of lists: A list of chunks, where each chunk is a sublist of the original list.
    """
    return [lst[i : i + n] for i in range(0, len(lst), n)]


PricesType = dict[str, float | None]
@streamlit.cache_data(ttl=datetime.timedelta(minutes=10))
def get_prices_for_tokens(tokens: list[str]) -> PricesType:
    """
    Fetches prices for the list of tokens

    Args:
                  tokens (list[str]): List of ids or addresses of tokens

    Returns:
                  dict[str, float | None]: dict of id/address used as input as keys and prices in USDC as values
    """
    token_price_map: dict[str, float | None] = {}

    if len(tokens) == 0:
        return token_price_map

    chunks = split_into_chunks(tokens, 50)  # Jupiter allows max 100 ids per request

    for chunk in chunks:
        translated_ids = list(map(kamino_vault_map.kamino_address_to_mint_address, chunk))
        ids = ",".join(translated_ids)

        url = f"{BASE_API_URL}?ids={ids}"  # USDC prices

        response = requests.get(url, timeout=15)

        response.raise_for_status()

        data = response.json()["data"]

        for token_address in chunk:
            translated_token_address = kamino_vault_map.kamino_address_to_mint_address(token_address)
            price_dict = data.get(translated_token_address)
            try:
                if price_dict is not None and "price" in price_dict:
                    token_price_map[token_address] = float(price_dict["price"])
                else:
                    token_price_map[token_address] = None
            except (ValueError, TypeError) as e:
                # Handle cases where conversion fails
                LOGGER.warning(f"Error converting price for token {token_address}: {e}")
                token_price_map[token_address] = None

    return token_price_map


@streamlit.cache_data(ttl=datetime.timedelta(minutes=10))
def get_prices() -> dict[str, decimal.Decimal]:
    price_fetcher = PriceFetcher()
    price_fetcher.get_prices()
    return price_fetcher.prices


class PriceFetcher:

    # TODO: Move this mapping to `src.settings.TOKEN_SETTINGS`.
    TOKEN_SYMBOLS_IDS_MAPPING = {
        "ETH": "ethereum",
        "SOL": "solana",
        "JUP": "jupiter-exchange-solana",
        "USDC": "usd-coin",
        "USDT": "tether",
    }
    VS_CURRENCY = "usd"

    def __init__(self):
        self.prices: dict[str, decimal.Decimal] = {
            symbol: decimal.Decimal("NaN") for symbol in self.TOKEN_SYMBOLS_IDS_MAPPING
        }

    def get_prices(self):
        ids = ""
        for _id in self.TOKEN_SYMBOLS_IDS_MAPPING.values():
            ids += _id + ","
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={self.VS_CURRENCY}"
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            for symbol, _id in self.TOKEN_SYMBOLS_IDS_MAPPING.items():
                self.prices[symbol] = decimal.Decimal(data[_id][self.VS_CURRENCY])
        else:
            response.raise_for_status()
