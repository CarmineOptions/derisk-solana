import datetime
import decimal
import requests

import streamlit



@streamlit.cache_data(ttl=datetime.timedelta(minutes=1))
def get_prices() -> dict[str, decimal.Decimal]:
	price_fetcher = PriceFetcher()
	price_fetcher.get_prices()
	return price_fetcher.prices



class BadResponse(Exception)

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
