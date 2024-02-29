"""

"""
import asyncio
import json
import os
from dataclasses import dataclass
from typing import List
import requests

from solana.rpc.async_api import AsyncClient
from orca_whirlpool.accounts import AccountFinder
from solders.pubkey import Pubkey
from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID, ORCA_WHIRLPOOLS_CONFIG


TOKEN_TO_PUBKEYS = {
	"SOL": [Pubkey.from_string("So11111111111111111111111111111111111111112")],
	"USDC": [Pubkey.from_string("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v")],
	"USDT": [Pubkey.from_string("BQcdHdAQW1hczDbBi9hiegXAR7A98Q9jx3X3iBBBDiq4")],
	"ETH": [
		Pubkey.from_string("2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk"),  # sollet
		Pubkey.from_string("FeGn77dhg1KXRRFeSwwMiykZnZPw5JXW6naf2aQgZDQf"),  # weth
		Pubkey.from_string("SL819j8K9FuFPL84UepVcFkEZqDUUvVzwDmJjCHySYj"),  # saber
		Pubkey.from_string("AaAEw2VCw1XzgvKB8Rj2DyK2ZVau9fbt2bE8hZFWsMyE"),  # allbridge
	],
	"JUP": [Pubkey.from_string("JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN")]
}


class Amms:
	"""
	A class that describes the state of all relevant pools of all relevant swap AMMs.
	"""
	PAIRS = [
		("ETH", "USDC"),
		("ETH", "USDT"),
		("SOL", "USDC"),
		("SOL", "USDT"),
		("JUP", "USDC"),
		("JUP", "USDT")
	]

	def __init__(self) -> None:
		self.pools = None
		self.liquidity = {pair: None for pair in self.PAIRS}

	def update_pools(self) -> None:
		pass


# TODO: To be implemented.
def load_amm_data() -> Amms:
	amms = Amms()
	amms.update_pools()
	return amms


@dataclass
class MeteoraPool:
	pool_address: str
	pool_token_mints: List[str]
	pool_token_amounts: List[float]
	pool_token_usd_amounts: List[str]
	lp_mint: str
	pool_tvl: str
	farm_tvl: str
	farming_pool: str
	farming_apy: str
	is_monitoring: bool
	pool_order: int
	farm_order: int
	pool_version: int
	pool_name: str
	lp_decimal: int
	farm_reward_duration_end: int
	farm_expire: bool
	pool_lp_price_in_usd: str
	trading_volume: str
	fee_volume: str
	weekly_trading_volume: str
	weekly_fee_volume: str
	yield_volume: str
	accumulated_trading_volume: str
	accumulated_fee_volume: str
	accumulated_yield_volume: str
	trade_apy: str
	weekly_trade_apy: str
	daily_base_apy: str
	weekly_base_apy: str
	farm_new: bool
	permissioned: bool
	unknown: bool
	total_fee_pct: str
	is_lst: bool
	is_forex: bool
	created_at: int

	def __post_init__(self):
		# Convert pool_token_amounts to a list of integers
		self.pool_token_amounts = [float(amount) for amount in self.pool_token_amounts]

	def get_token_amount(self, token_symbol: str) -> float:
		"""
		Returns the amount of the specified token in this pool, given the token symbol.
		"""
		# Find the public keys associated with the token symbol
		token_mints = TOKEN_TO_PUBKEYS.get(token_symbol, [])

		# Iterate through the pool's token mints to find a matching public key
		for i, mint in enumerate(self.pool_token_mints):
			if Pubkey.from_string(mint) in token_mints:
				# Return the corresponding amount from pool_token_amounts
				return self.pool_token_amounts[i]

		return 0  # Return "0" if the token is not found in this pool


class MeteoraAMM(Amms):
	def update_pools(self) -> None:
		# obtain pools' data
		response = requests.get("https://app.meteora.ag/amm/pools/")
		# get relevant pools
		all_pools = [MeteoraPool(**pool) for pool in json.loads(response.text)]
		self.get_relevant_pools(all_pools)
		self.get_liquidity()

	def get_liquidity(self):
		for mint_a_symbol, mint_b_symbol in self.PAIRS:
			amount_mint_a = 0
			amount_mint_b = 0
			if (mint_a_symbol, mint_b_symbol) in self.pools:
				for pool in self.pools[(mint_a_symbol, mint_b_symbol)]:
					amount_mint_a += pool.get_token_amount(mint_a_symbol)
					amount_mint_b += pool.get_token_amount(mint_b_symbol)
			self.liquidity[(mint_a_symbol, mint_b_symbol)] = (amount_mint_a, amount_mint_b)
			print(mint_a_symbol, amount_mint_a, mint_b_symbol, amount_mint_b)

	def get_relevant_pools(self, pools: List[MeteoraPool]) -> None:
		pubkey_to_token = {str(pubkey): token for token, pubkeys in TOKEN_TO_PUBKEYS.items() for pubkey in pubkeys}
		pair_to_pools = {pair: [] for pair in self.PAIRS}

		for pool in pools:
			pool_tokens = set(pool.pool_token_mints)
			matched_tokens = [pubkey_to_token[pubkey] for pubkey in pool_tokens if pubkey in pubkey_to_token]

			if len(matched_tokens) == 2:  # Ensure exactly two distinct tokens are identified
				matched_pair = tuple(sorted(matched_tokens))
				if matched_pair in self.PAIRS or matched_pair[::-1] in self.PAIRS:
					pair_to_pools[matched_pair].append(pool)

		# Return only the pairs that have at least one pool
		self.pools = {pair: pools for pair, pools in pair_to_pools.items() if pools}


class RaydiumAMM(Amms):
	def update_pools(self) -> None:
		# obtain pools' data
		result = requests.get('https://api.raydium.io/v2/ammV3/ammPools')
		decoded_result = result.content.decode('utf-8')
		pools = json.loads(decoded_result)
		# get relevant pools
		# ...


class OrcaAMM(Amms):
	def update_pools(self) -> None:
		pools = asyncio.run(self.get_all_pools())
		print(len(pools))

		# get relevant pools
		# ...

	async def get_all_pools(self):
		connection = AsyncClient(os.getenv('RPC_URL'))

		finder = AccountFinder(connection)
		return await finder.find_whirlpools_by_whirlpools_config(
			ORCA_WHIRLPOOL_PROGRAM_ID,
			ORCA_WHIRLPOOLS_CONFIG,
		)


if __name__ == "__main__":
	# met = MeteoraAMM()
	# met.update_pools()

	orca_amm = OrcaAMM()
	orca_amm.update_pools()
