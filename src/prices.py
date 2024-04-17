import datetime
import decimal
import requests

import streamlit

from src import kamino_vault_map

BASE_API_URL = "https://price.jup.ag/v4/price"

def token_list_to_ids(l: list[str]) -> str:
  ids = ""
  for index, token in enumerate(l):
    # if kamino vault or reserve map to its mint
    token = kamino_vault_map.kamino_address_to_mint_address(token)

    if index > 0:
      ids+= ","
    ids += token

  return ids

def get_prices_for_tokens(tokens: list[str]) -> dict[str, float | None]:
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

  ids = token_list_to_ids(tokens)
  url = f"{BASE_API_URL}?ids={ids}&vsToken=USDC"
  response = requests.get(url, timeout=15)

  if response.status_code == 200:
    data = response.json()["data"]
  else:
    response.raise_for_status()

  for token_address in tokens:
    validated_token_address = kamino_vault_map.kamino_address_to_mint_address(token_address)

    price_dict = data.get(validated_token_address)

    if price_dict is not None and "price" in price_dict:
      token_price_map[token_address] = price_dict["price"]
    else:
      token_price_map[token_address] = None

  return token_price_map

@streamlit.cache_data(ttl=datetime.timedelta(minutes=1))
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
			symbol: decimal.Decimal('NaN')
			for symbol
			in self.TOKEN_SYMBOLS_IDS_MAPPING
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
