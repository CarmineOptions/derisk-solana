# TODO: To be implemented.
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import requests


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


class OrcaAMM(Amm):
	dex_name = 'Orca'
	def get_pools(self) -> None:
		result = requests.get('https://api.mainnet.orca.so/v1/whirlpool/list')
		decoded_result = result.content.decode('utf-8')
		self.pools = json.loads(decoded_result)['whirlpools']

	def store_pool(self, pool: Dict[str, Any]) -> bool:
		raise NotImplementedError('Implement me!')


class RaydiumAMM(Amm):
	dex_name = 'Orca'

	def get_pools(self):
		result = requests.get('https://api.raydium.io/v2/ammV3/ammPools')
		decoded_result = result.content.decode('utf-8')
		self.pools = json.loads(decoded_result)['data']

	def store_pool(self, pool: Dict[str, Any]) -> bool:
		raise NotImplementedError('Implement me!')


class MeteoraAMM(Amm):

	def get_pools(self):
		response = requests.get("https://app.meteora.ag/amm/pools/")
		decoded_content = response.content.decode('utf-8')
		self.pools = json.loads(decoded_content)
		return self.pools

	def store_pool(self, pool: Dict[str, Any]) -> bool:
		raise NotImplementedError('Implement me!')
