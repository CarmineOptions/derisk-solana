# TODO: To be implemented.
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

import requests

from db import AmmLiquidity, get_db_session


class Amms:
	"""
	A class that describes the state of all relevant pools of all relevant swap AMMs.
	"""

	def __init__(self) -> None:
		pass

	def update_pools(self) -> None:
		pass


# TODO: To be implemented.
def load_amm_data() -> Amms:
	amms = Amms()
	amms.update_pools()
	return amms


class Amm(ABC):
	# dex_name: str = ''
	pools: List[Dict[str, Any]]
	timestamp = int(time.time())

	def __init__(self):
		pass

	@abstractmethod
	def get_pools(self):
		raise NotImplementedError('Implement me!')

	def store_pools(self):
		for pool in self.pools:
			self.store_pool(pool)

	def store_pool(self, pool: Dict[str, Any]) -> bool:
		raise NotImplementedError('Implement me!')

	@staticmethod
	def convert_to_big_integer_and_decimals(amount_str: str | None) -> Tuple[int | None, int | None]:
		if amount_str is None:
			return None, None
		# Check if there is a decimal point in the amount_str
		if '.' in amount_str:
			# Split the string into whole and fractional parts
			whole_part, fractional_part = amount_str.split('.')
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
	DEX_NAME = 'Orca'

	def get_pools(self) -> None:
		result = requests.get('https://api.mainnet.orca.so/v1/whirlpool/list')
		decoded_result = result.content.decode('utf-8')
		self.pools = json.loads(decoded_result)['whirlpools']

	def store_pool(self, pool: Dict[str, Any]) -> None:
		pair = f"{pool['tokenA']['symbol']}-{pool['tokenB']['symbol']}"
		market_address = pool.get('address')

		with get_db_session() as session:
			# Creating an instance of AmmLiquidity
			liquidity_entry = AmmLiquidity(
				timestamp=self.timestamp,
				dex=self.DEX_NAME,
				pair=pair,
				market_address=market_address,
				additional_info=json.dumps(pool)
			)
			# Add to session and commit
			session.add(liquidity_entry)
			session.commit()


class RaydiumAMM(Amm):
	DEX_NAME = 'Orca'
	pairs = None

	def get_pools(self):
		result = requests.get('https://api.raydium.io/v2/ammV3/ammPools')
		decoded_result = result.content.decode('utf-8')
		self.pools = json.loads(decoded_result)['data']

	def store_pool(self, pool: Dict[str, Any]) -> None:
		market_address = pool.get('id')
		pair = f"{pool['mintA']}/{pool['mintB']}"  # TODO

		# Create a new AmmLiquidity record
		with get_db_session() as session:
			liquidity_entry = AmmLiquidity(
				timestamp=self.timestamp,
				dex=self.DEX_NAME,
				pair=pair,
				market_address=market_address,
				additional_info=json.dumps(pool)
			)

			# Add the new record to the session and commit
			session.add(liquidity_entry)
			session.commit()


class MeteoraAMM(Amm):
	DEX_NAME = 'Meteora'

	def get_pools(self):
		response = requests.get("https://app.meteora.ag/amm/pools/")
		decoded_content = response.content.decode('utf-8')
		self.pools = json.loads(decoded_content)
		return self.pools

	def store_pool(self, pool: Dict[str, Any]) -> None:
		pair = pool['pool_name']
		token_x_amount, token_y_amount = pool.get('pool_token_amounts')

		# Convert amounts to BigInteger and decimals
		token_x, token_x_decimals = self.convert_to_big_integer_and_decimals(token_x_amount)
		token_y, token_y_decimals = self.convert_to_big_integer_and_decimals(token_y_amount)

		# Create the AmmLiquidity object
		with get_db_session() as session:
			liquidity_entry = AmmLiquidity(
				timestamp=self.timestamp,
				dex=self.DEX_NAME,
				pair=pair,
				market_address=pool.get('pool_address'),
				token_x=token_x,
				token_y=token_y,
				token_x_decimals=token_x_decimals,
				token_y_decimals=token_y_decimals,
				additional_info=json.dumps(pool)
			)

			# Add to session and commit
			session.add(liquidity_entry)
			session.commit()
