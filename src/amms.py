"""
Module dedicated to fetching and storing data from AMM pools.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple
import json
import logging
import time
import traceback
import requests  # type: ignore

from db import AmmLiquidity, get_db_session


LOG = logging.getLogger(__name__)


class Amms:
	"""
	A class that describes the state of all relevant pools of all relevant swap AMMs.
	"""

	def __init__(self) -> None:
		pass

	def update_pools(self) -> None:
		"""
		Save pools data to database.
		:return:
		"""
		# set timestamp
		timestamp = int(time.time())

		# collect and store pools
		orca_amm = OrcaAMM()
		orca_amm.timestamp = timestamp
		orca_amm.get_pools()
		orca_amm.store_pools()

		raydium_amm = RaydiumAMM()
		raydium_amm.timestamp = timestamp
		raydium_amm.get_pools()
		raydium_amm.store_pools()

		meteora_amm = MeteoraAMM()
		meteora_amm.timestamp = timestamp
		meteora_amm.get_pools()
		meteora_amm.store_pools()


class Amm(ABC):
	# dex_name: str = ''
	pools: List[Dict[str, Any]]
	timestamp = int(time.time())

	def __init__(self):
		pass

	@abstractmethod
	def get_pools(self):
		"""
		Fetch pools data.
		"""
		raise NotImplementedError('Implement me!')

	def store_pools(self):
		"""
		Save pools data to database.
		"""
		for pool in self.pools:
			self.store_pool(pool)

	@abstractmethod
	def store_pool(self, pool: Dict[str, Any]) -> None:
		"""
		Save pool data to database.
		"""
		raise NotImplementedError('Implement me!')

	@staticmethod
	def convert_to_big_integer_and_decimals(amount_str: str | None) -> Tuple[int | None, int | None]:
		"""
		Convert string containing numerical value into integer and number of decimals.
		"""
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
		"""
		Fetches pool data from the Orca API and stores it in the `pools` attribute.
		"""
		LOG.info("Fetching pools from Orca API")
		try:
			result = requests.get('https://api.mainnet.orca.so/v1/whirlpool/list', timeout=30)
			decoded_result = result.content.decode('utf-8')
			self.pools = json.loads(decoded_result)['whirlpools']
			LOG.info(f"Successfully fetched {len(self.pools)} pools")
		except requests.exceptions.Timeout:
			LOG.error("Request to Orca whirlpool API timed out")
			self.get_pools()

	def store_pool(self, pool: Dict[str, Any]) -> None:
		"""
		Save pool data to database.
		"""
		pair = f"{pool['tokenA']['symbol']}-{pool['tokenB']['symbol']}"
		market_address = pool.get('address', 'Unknown')

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
	token_list: List

	def get_pools(self):
		"""
		Fetches pool data from the Radium API and stores it in the `pools` attribute.
		"""
		LOG.info("Fetching pools from Raydium API")
		try:
			result = requests.get('https://api.raydium.io/v2/ammV3/ammPools', timeout=30)
			decoded_result = result.content.decode('utf-8')
			self.pools = json.loads(decoded_result)['data']
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
			result = requests.get('https://api.mainnet.orca.so/v1/token/list', timeout=30)
			decoded_result = result.content.decode('utf-8')
			self.token_list = json.loads(decoded_result)['tokens']
		except requests.exceptions.Timeout:
			LOG.error("Request to Raydium pool API timed out")
			self.get_token_list()

	def store_pools(self):
		"""
		Save pools data to database.
		"""
		self.get_token_list()
		for pool in self.pools:
			self.store_pool(pool)

	def store_pool(self, pool: Dict[str, Any]) -> None:
		"""
		Save pool data to database.
		"""
		market_address = pool.get('id', 'Unknown')

		# get token symbols
		try:
			token_x_symbol = next(i for i in self.token_list if i['mint'] == pool['mintA']).get('symbol')
		except StopIteration:
			token_x_symbol = 'Unknown'
		try:
			token_y_symbol = next(i for i in self.token_list if i['mint'] == pool['mintB']).get('symbol')
		except StopIteration:
			token_y_symbol = 'Unknown'

		pair = f"{token_x_symbol}-{token_y_symbol}"

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
		"""
		Fetches pool data from the Meteora API and stores it in the `pools` attribute.
		"""
		try:
			response = requests.get("https://app.meteora.ag/amm/pools/", timeout=30)
			decoded_content = response.content.decode('utf-8')
			self.pools = json.loads(decoded_content)
			LOG.info(f"Successfully fetched {len(self.pools)} pools")
		except requests.exceptions.Timeout:
			LOG.error("Request to Meteora pool API timed out")
			self.get_pools()

	def store_pool(self, pool: Dict[str, Any]) -> None:
		"""
		Save pool data to database.
		"""
		pair = pool['pool_name']
		token_x_amount, token_y_amount = pool.get('pool_token_amounts', (None, None))[:2]

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
				token_x=token_x if token_x is not None else -1,
				token_y=token_y if token_y is not None else -1,
				token_x_decimals=token_x_decimals if token_x_decimals is not None else -1,
				token_y_decimals=token_y_decimals if token_y_decimals is not None else -1,
				additional_info=json.dumps(pool)
			)

			# Add to session and commit
			session.add(liquidity_entry)
			session.commit()


if __name__ == '__main__':
	LOG.info("Start collecting AMM pools.")
	amms = Amms()
	while True:
		try:
			amms.update_pools()
			LOG.info("Successfully processed all pools. Waiting 5 minutes before next update.")
			time.sleep(300)
		except Exception as e:  # pylint: disable=broad-exception-caught
			tb_str = traceback.format_exc()
			# Log the error message along with the traceback
			LOG.error(f"An error occurred: {e}\nTraceback:\n{tb_str}")
			time.sleep(300)
