import os
import logging
import json
import asyncio
from decimal import Decimal

from orca_whirlpool.constants import ORCA_WHIRLPOOL_PROGRAM_ID
from orca_whirlpool.context import WhirlpoolContext
from orca_whirlpool.accounts import AccountFinder, AccountFetcher, Whirlpool, TickArray
from orca_whirlpool.utils import PriceMath
from orca_whirlpool.utils import PoolUtil
from orca_whirlpool.internal.utils.pool_util import LiquidityDistribution

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient

# from db import AmmLiquidity, get_db_session
import db
from src.protocols.dexes.amms.amm import Amm
from src.protocols.dexes.amms.utils import (
    get_mint_decimals,
    PriceLevel,
    diff_price_levels,
)

LOG = logging.getLogger(__name__)
SHIFT_64 = Decimal(2) ** 64

AUTHENTICATED_RPC_URL = os.environ.get("AUTHENTICATED_RPC_URL")
if AUTHENTICATED_RPC_URL is None:
    raise ValueError("No AUTHENTICATED_RPC_URL env var")


class OrcaPool:
    """
    Class that represents single orca pool.
    Takes care of converting the pool to OB-like data and provides properties
    such as bids and asks
    """
    # pylint: disable=too-many-instance-attributes
    @classmethod
    async def from_address(
        cls, address: Pubkey, connection: AsyncClient, ctx: WhirlpoolContext = None
    ) -> "OrcaPool":
        """
        Creates OrcaPool instance from Market address (as Pubkey) and connection (AsyncClient).

        Parameters:
        - address (Pubkey): Address of Orca pool.
        - connection (AsyncClient): Solana AsyncClient
        - ctx (WhirlpoolContext): Orca WhirlPool context. Optional.

        Returns:
        - OrcaPool instance
        """

        if ctx is None:
            ctx = WhirlpoolContext(ORCA_WHIRLPOOL_PROGRAM_ID, connection, Keypair())

        # Helper classes for getting onchain info
        fetcher = AccountFetcher(connection)
        finder = AccountFinder(connection)

        # Fetch on-chain pool info
        pool = await ctx.fetcher.get_whirlpool(address)

        # Fetch underlyings decimals
        decimals_a = await get_mint_decimals(pool.token_mint_a, connection)
        decimals_b = await get_mint_decimals(pool.token_mint_b, connection)

        # Fetch list of TickArrays
        # stored like that because only 88 ticks fit into single onchain account
        ticker_arrays = await finder.find_tick_arrays_by_whirlpool(
            ORCA_WHIRLPOOL_PROGRAM_ID, address
        )

        # Calculate individual Liquidity Distributions
        liqdist = PoolUtil.get_liquidity_distribution(pool, ticker_arrays)

        # Construct and return OrcaPoool
        return OrcaPool(
            pool,
            address,
            connection,
            ctx,
            finder,
            fetcher,
            ticker_arrays,
            liqdist,
            decimals_a,
            decimals_b,
        )

    def __init__(
        self,
        pool: Whirlpool,
        address: Pubkey,
        connection: AsyncClient,
        ctx: WhirlpoolContext,
        finder: AccountFinder,
        fetcher: AccountFetcher,
        ticker_arrays: list[TickArray],
        liquidity_distribution: list[LiquidityDistribution],
        decimals_a: int,
        decimals_b: int,
    ):
        """
        Takes in all the needed parameters and calculates asks and bids.
        """

        # Assign function parameters to private attributes
        self._pool = pool
        self._address = address
        self._connection = connection
        self._ctx = ctx
        self._finder = finder
        self._fetcher = fetcher
        self._ticker_arrays = ticker_arrays
        self._liquidity_distribution = liquidity_distribution
        self._decimals_a = decimals_a
        self._decimals_b = decimals_b

        # Split liq distributions into the ones below and above current tick
        self._sorted_liqdist = (
            self.split_liquidity_distribution_into_lower_current_upper(
                liquidity_distribution, pool.sqrt_price
            )
        )
        self._liqdist_down = self._sorted_liqdist[0]
        self._liqdist_current = self._sorted_liqdist[1]  # Current tick returned as well
        self._liqdist_up = self._sorted_liqdist[2]

        # Calculate bids, asks
        self.load_bids()
        self.load_asks()

    @property
    def pool(self) -> Whirlpool:
        """
        Get the on-chain WhirlPool instance of a class provided
        by orca python library.

        Returns:
        - pool (WhirlPool) : Orca WhirlPool instance.
        """
        return self._pool

    @property
    def mints_decimals(self) -> tuple[int, int]:
        """
        Get underlying tokens decimals.

        Returns:
        - token a decimals (int) : Base token decimals
        - token b decimals (int) : Quote token decimals
        """
        return self._decimals_a, self._decimals_b

    @property
    def price(self) -> Decimal:
        """
        Get current pool price.

        Returns:
        - price (Decimal) : Current pool price in human readable format.
        """
        return PriceMath.sqrt_price_x64_to_price(
            self._pool.sqrt_price, self._decimals_a, self._decimals_b
        )

    @property
    def liquidity_distribution(self) -> list[LiquidityDistribution]:
        """
        Get list of pool's liquidity distributions.

        Returns:
        - liquidity distribution: List of pool's liquidity distributions
        """
        return self._liquidity_distribution

    @property
    def sorted_liquidity_distribution(
        self,
    ) -> tuple[
        list[LiquidityDistribution], LiquidityDistribution, list[LiquidityDistribution]
    ]:
        """
        Get liquidity distributions split into the ones that are below current tick, the current tick
        and the ones above current tick.

        Return:
        - below: LiquidityDistribtuions below current tick
        - current: Current LiquidityDistribution
        - above: LiquidityDistribtuions above current tick
        """
        return self._sorted_liqdist

    @property
    def liquidity_distribution_up_direction(self) -> list[LiquidityDistribution]:
        """
        Get liquidity distribtuions that are used when price moves up.
        In other terms, these liquidity distrubutions are used when user
        trades quote token for base token.

        Returns:
        - upper liqudity distribtuions
        """
        return self._liqdist_up

    @property
    def liquidity_distribution_down_direction(self) -> list[LiquidityDistribution]:
        """
        Get liquidity distribtuions that are used when price moves down.
        In other terms, these liquidity distrubutions are used when user
        trades base token for quote token.

        Returns:
        - lower liqudity distribtuions
        """
        return self._liqdist_down

    @property
    def liquidity_distribution_current(self) -> LiquidityDistribution:
        """
        Get current liquidity distribution. In other terms the one that
        encompasses current tick.

        Returns:
        - current liquidity distribution
        """
        return self._liqdist_current

    @property
    def bids(self) -> list[PriceLevel]:
        """
        Get bids approximated from liquidity distributions.

        Returns:
        - bids
        """
        return self._bids

    @property
    def asks(self) -> list[PriceLevel]:
        """
        Get asks approximated from liquidity distributions.

        Returns:
        - asks
        """
        return self._asks

    @staticmethod
    def split_liquidity_distribution_into_lower_current_upper(
        liqdist: list[LiquidityDistribution],
        sqrt_price: Decimal,
        bounds_percentage: Decimal | None = None,
    ) -> tuple[
        list[LiquidityDistribution], LiquidityDistribution, list[LiquidityDistribution]
    ]:
        """
        Splits list of liquidity distributions into ones that are below current price, the one
        encompassing the current price and the ones that are above current price.

        Parameters:
        - liqdist: List of liquidity distributions to be split
        - sqrt_price: Current sqrt price
        - bounds_percentage: Percentage that determines bounds around the current price for
                            which to filter the LiqDists. For example, if it's 10% then only the
                            distributions that are within +-10% of the current price are considered.
                            Optional, 0.95 (95%) by default.

        Returns:
        - lower: Liquidity distributions below current price
        - current: Liquidity distribution encompassing the current price
        - above: Liquidity distributions above current price
        """

        # Set default bounds percentage
        if bounds_percentage is None:
            bounds_percentage = Decimal("0.95")

        # Calculat upper and lower bound (keep in mind that price is in sqrt terms)
        upper_bound = sqrt_price * (Decimal(1) + bounds_percentage).sqrt()
        lower_bound = sqrt_price * (Decimal(1) - bounds_percentage).sqrt()

        # Create empty lists for split distributions
        liqdist_up = []
        liqdist_down = []

        # Create one for current  as well to later check that only
        # one current distribution was found
        liqdist_current = []

        for liq in liqdist:
            upper_tick_price = PriceMath.tick_index_to_sqrt_price_x64(
                liq.tick_upper_index
            )
            lower_tick_price = PriceMath.tick_index_to_sqrt_price_x64(
                liq.tick_lower_index
            )

            if upper_tick_price <= sqrt_price:
                if upper_tick_price >= lower_bound:
                    # If upper tick of the liquidity distribution is below current current price
                    # and higher than lower bound then append to lower distribution
                    liqdist_down.append(liq)

            elif lower_tick_price >= sqrt_price:
                # If lower tick of the liquidity distribution is above current current price
                # and lower than upper bound then append to upper distribution
                if lower_tick_price <= upper_bound:
                    liqdist_up.append(liq)

            elif lower_tick_price < sqrt_price < upper_tick_price:
                # In this case the liquidity encompasses the current price,
                # so it's current liqudity distribution
                liqdist_current.append(liq)

            else:
                LOG.error(f"Unmanageable liqdist found: {liq}")

        if len(liqdist_current) != 1:
            LOG.error(f"Found more than one current liqdist: {liqdist_current}")

        return (liqdist_down, liqdist_current[0], liqdist_up)

    @staticmethod
    def delta_y(
        current_price: Decimal, upper_price: Decimal, liquidity: int
    ) -> Decimal:
        """
        Calculates delta in token y (token A) when price goes up (and user trades quote token for base).

        Arguments:
        - current_price (Decimal): Current sqrt price
        - upper_price (Decimal): Upper sqrt price (to which to calculate the delta)
        - liquidity (int): Current liquidity (as defined by Orca/Uniswap)

        Returns:
        - token y amount: Token y that is available on given range. This is the amount that will be returned
                          by the AMM in order to go from current to upper price.
        """
        return (
            Decimal(liquidity)
            * SHIFT_64
            * (upper_price - current_price)
            / (current_price * upper_price)
        )

    @staticmethod
    def delta_x(
        current_price: Decimal, lower_price: Decimal, liquidity: int
    ) -> Decimal:
        """
        Calculates delta in token x (token B) when price goes down (and user trades base token for quote).

        Arguments:
        - current_price (Decimal): Current sqrt price
        - lower_price (Decimal): Lower sqrt price (to which to calculate the delta)
        - liquidity (int): Current liquidity (as defined by Orca/Uniswap)

        Returns:
        - token x amount: Token x that is available on given range. This is the amount that will be returned
                          by the AMM in order to go from current to lower price.
        """
        return Decimal(liquidity) * (current_price - lower_price) / SHIFT_64

    def load_bids(self):
        """
        Calculates approximated bids from the CLMM data and assignes them to '_bids' attribute
        (can be accessed via 'bids' property).
        """

        price_levels = []

        # First calculate bids from current range
        current_tick = self.pool.tick_current_index

        # Both values increased by one since the current tick is already stored and we want
        # to include the upper one (range function isn't inclusive)
        current_tick_range = range(
            current_tick + 1, self._liqdist_current.tick_upper_index + 1
        )
        current_price = PriceMath.tick_index_to_sqrt_price_x64(current_tick)

        # Liquidity on current liqudity distribution
        current_liquidity = self._liqdist_current.liquidity

        # Iterate over the list of ticks where the upper ticks go up to
        # the end of current liquidity distribution
        for next_tick in current_tick_range:
            # Current price is kept the same while the upper price is updated
            # during each iteration
            upper_price = PriceMath.tick_index_to_sqrt_price_x64(next_tick)

            # Calculate delta in y token for every upper tick
            delta_x = abs(self.delta_x(
                current_price, upper_price, current_liquidity
            ))

            # Create new PriceLevel entry
            price_level = PriceLevel(
                price=PriceMath.tick_index_to_price(
                    next_tick, self._decimals_a, self._decimals_b
                ),
                amount=delta_x / 10**self._decimals_a,
            )

            # Append PriceLevel to list
            price_levels.append(price_level)

        # Since the current tick is kept the same when calculating for individual
        # liquidity distributions, the data is basically cumulative available liquidity
        # So differentiate it to get the approximate liquidity at given price
        price_levels = diff_price_levels(price_levels)

        # Now iterate over other ranges in upper direction
        for upliq in self._liqdist_up:
            # Now the current liquidity distribution is always the one that's
            # next in line (when going up)
            current_tick = upliq.tick_lower_index
            current_price = PriceMath.tick_index_to_sqrt_price_x64(current_tick)

            current_tick_range = range(current_tick + 1, upliq.tick_upper_index + 1)
            current_liquidity = upliq.liquidity

            _levels = []

            for next_tick in current_tick_range:
                upper_price = PriceMath.tick_index_to_sqrt_price_x64(next_tick)
                delta_x = abs(self.delta_x(
                    current_price, upper_price, current_liquidity
                ))

                price_level = PriceLevel(
                    price=PriceMath.tick_index_to_price(
                        next_tick, self._decimals_a, self._decimals_b
                    ),
                    amount=delta_x / 10**self._decimals_a,
                )

                _levels.append(price_level)

            # Differentiate new price levels and append them to the ones before
            price_levels += diff_price_levels(_levels)

        self._bids = price_levels

    def load_asks(self):
        """
        Calculates approximated asks from the CLMM data and assignes them to '_asks' attribute
        (can be accessed via 'asks' property).
        """

        # Basically the same as load_bids function, just in opposite direction.

        price_levels = []

        current_tick = self.pool.tick_current_index
        current_price = PriceMath.tick_index_to_sqrt_price_x64(current_tick)
        current_tick_range = list(
            range(self._liqdist_current.tick_lower_index, current_tick)
        )[::-1]
        current_liquidity = self._liqdist_current.liquidity

        for next_tick in current_tick_range:
            lower_price = PriceMath.tick_index_to_sqrt_price_x64(next_tick)
            delta_x = self.delta_x(
                current_price, lower_price, current_liquidity
            )

            price_level = PriceLevel(
                price=PriceMath.tick_index_to_price(
                    next_tick, self._decimals_a, self._decimals_b
                ),
                amount=delta_x / 10**self._decimals_a,
            )

            price_levels.append(price_level)

        price_levels = diff_price_levels(price_levels)

        for downliq in self._liqdist_down:
            current_tick = downliq.tick_upper_index
            current_price = PriceMath.tick_index_to_sqrt_price_x64(current_tick)
            current_liquidity = downliq.liquidity

            current_tick_range = list(range(downliq.tick_lower_index, current_tick))[
                ::-1
            ]

            _levels = []

            for next_tick in current_tick_range:
                lower_price = PriceMath.tick_index_to_sqrt_price_x64(next_tick)
                delta_x = self.delta_x(
                    current_price, lower_price, current_liquidity
                )
                price_level = PriceLevel(
                    price=PriceMath.tick_index_to_price(
                        next_tick, self._decimals_a, self._decimals_b
                    ),
                    amount=delta_x / 10**self._decimals_a,
                )

                _levels.append(price_level)

            price_levels += diff_price_levels(_levels)

        self._asks = price_levels


class OrcaAMM(Amm):
    DEX_NAME = "Orca"
    pools: list[OrcaPool]

    def __init__(self):
        self.client = AsyncClient(AUTHENTICATED_RPC_URL)

    async def get_pools(self) -> None:
        """
        Loads stored list of pools and gets it's liquidity distribution.
        """
        LOG.info("Loading Orca pools")

        with open("src/protocols/pools/orca_pools.json", "r", encoding='utf-8') as f:
            pools_list = json.load(f)

        # Get list of addresses
        adresses = [i["address"] for i in pools_list]

        # Create Coroutine tasks to be gathered
        tasks = [
            OrcaPool.from_address(Pubkey.from_string(pool), self.client)
            for pool in adresses
        ]

        # Gather and return exceptions so that the whole process doesn't
        # fail if there are some errors
        awaited_tasks = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter for successfully fetched pools
        self.pools = [pool for pool in awaited_tasks if isinstance(pool, OrcaPool)]

        if len(tasks) != len(self.pools):
            # This means there were some failures
            errors = [pool for pool in awaited_tasks if not isinstance(pool, OrcaPool)]

            # Log amount of errors
            if errors:
                LOG.error(
                    f"Was unable to fetch {len(errors)} Orca pools, example: {errors[0]}"
                )

        LOG.info(f"Fetched {len(self.pools)} Orca pools")

    def store_pool(self, pool: OrcaPool) -> None:
        """
        Save pool data to database.
        """
        # TODO: This function, after new table schema is setup
        with db.get_db_session() as session:
            # Creating an instance of AmmLiquidity
            liquidity_entry = db.DexNormalizedLiquidity(
                timestamp=self.timestamp,
                dex=self.DEX_NAME,
                market_address=str(pool.pool.pubkey),
                token_x_address=str(pool.pool.token_mint_a),
                token_y_address=str(pool.pool.token_mint_b),
                bids = [(float(i.price), float(i.amount)) for i in pool.bids],
                asks = [(float(i.price), float(i.amount)) for i in pool.asks],
            )
            # Add to session and commit
            session.add(liquidity_entry)
            session.commit()

    # timestamp = Column(BigInteger, nullable=False)
    # dex = Column(String, nullable=False)
    # market_address = Column(String, nullable=False)
    # token_x_address = Column(String, nullable=False)
    # token_y_address = Column(String, nullable=False)
    # bids = Column(PG_ARRAY(Float), nullable=False)
    # asks = Column(PG_ARRAY(Float), nullable=False)
