"""
Module containes classes containing functionality for fetching CLOB Liqudity 
and pushing it to the database.
"""
import logging
import abc

from solana.keypair import Keypair # pylint: disable=E0611
from solana.publickey import PublicKey  # pylint: disable=E0611
from solana.rpc.commitment import Commitment
from solana.rpc.api import Client as SolanaClient

from phoenix.client import PhoenixClient
from pyserum.market import Market

# ^^ Ignoring pylint here because correct solana version is installed in
# the docker container

from gfx_perp_sdk import Perp, Product
from gfx_perp_sdk.types import MarketProductGroup
from gfx_perp_sdk.agnostic import Slab
from gfx_perp_sdk.utils import processOrderbook

from src.protocols.dexes.pairs import get_relevant_tickers
import db

LOGGER = logging.getLogger(__name__)


class CLOB(abc.ABC):
    @abc.abstractmethod
    async def get_onchain_orderbook(
        self, market_address: str
    ) -> dict[str, list[tuple[float, float]]]:
        """
        Retrieves onchain orderbook data for single market.

        Parameters:
        - market_address: Address of market for which to get the data.

        Returns:
        - dict: Dictionary with two keys - bids and asks where both keys map to
                list of two sized tuples (price, size) representing single price level
        """

    @abc.abstractmethod
    async def update_orderbooks(self, timestamp: int) -> None:
        """
        Fetches orderbook data for all provided markets and pushes it to the database.

        Parameters:
        - timestamp: Timestamp to use when storing data. Used to make some aggregations easier
                    accross all the different markets, since we don't need high precision.
        """


class Phoenix(CLOB):
    def __init__(
        self,
        commitment: Commitment = Commitment("finalized"),
        endpoint: str | None = None,
    ):

        if endpoint is None:
            endpoint = "https://api.mainnet-beta.solana.com"

        self.identifier = "PHOENIX"
        self.tickers = get_relevant_tickers(self.identifier)
        self.client = PhoenixClient(commitment=commitment, endpoint=endpoint)

    async def get_onchain_orderbook(
        self, market_address: str
    ) -> dict[str, list[tuple[float, float]]]:
        market_pubkey = PublicKey(market_address)

        try:

            # Set levels to 1_000 to fetch as much as possible
            ob = await self.client.get_l2_book(market_pubkey, levels=1_000)  # type: ignore
            return {
                "bids": [(float(i.price), float(i.size)) for i in ob.bids],
                "asks": [(float(i.price), float(i.size)) for i in ob.asks],
            }

        except AttributeError:
            LOGGER.error(f"Unknown Phoenix market address: {market_address}")
            return {"bids": [], "asks": []}

    async def update_orderbooks(self, timestamp: int) -> None:
        order_books = {
            ticker: await self.get_onchain_orderbook(address)
            for ticker, address in self.tickers.items()
        }
        with db.get_db_session() as session:

            for ticker, orderbook in order_books.items():
                ob_liq_record = db.CLOBLiqudity(
                    dex=self.identifier,
                    pair=ticker,
                    market_address=self.tickers[ticker],
                    bids=orderbook["bids"],
                    asks=orderbook["asks"],
                    timestamp=timestamp,
                )
                session.add(ob_liq_record)
            session.commit()


class OpenBook(CLOB):
    def __init__(
        self,
        commitment: Commitment = Commitment("finalized"),
        endpoint: str | None = None,
    ):

        if endpoint is None:
            endpoint = "https://api.mainnet-beta.solana.com"

        self.identifier = "OPENBOOK"
        self.tickers = get_relevant_tickers(self.identifier)
        self.client = SolanaClient(
            endpoint=endpoint,  # Good enough for this use
            commitment=commitment,
        )

    async def get_onchain_orderbook(
        self, market_address: str
    ) -> dict[str, list[tuple[float, float]]]:
        market_pubkey = PublicKey(market_address)

        try:

            # Set levels to 1_000 to fetch as much as possible
            market = Market.load(self.client, market_pubkey)

            bids = market.load_bids().get_l2(1_000)
            asks = market.load_asks().get_l2(1_000)

            return {
                "bids": [(i.price, i.size) for i in bids],
                "asks": [(i.price, i.size) for i in asks],
            }

        except AttributeError:

            LOGGER.error(f"Unknown OpenBook market address: {market_address}")
            return {"bids": [], "asks": []}

    async def update_orderbooks(self, timestamp: int) -> None:
        order_books = {
            ticker: await self.get_onchain_orderbook(address)
            for ticker, address in self.tickers.items()
        }

        with db.get_db_session() as session:

            for ticker, orderbook in order_books.items():
                ob_liq_record = db.CLOBLiqudity(
                    dex=self.identifier,
                    pair=ticker,
                    market_address=self.tickers[ticker],
                    bids=orderbook["bids"],
                    asks=orderbook["asks"],
                    timestamp=timestamp,
                )
                session.add(ob_liq_record)
            session.commit()


class GooseFx(CLOB):
    def __init__(
        self,
        commitment: Commitment = Commitment("finalized"),
        endpoint: str | None = None,
    ):
        if endpoint is None:
            endpoint = "https://api.mainnet-beta.solana.com"

        self.identifier = "GOOSEFX"
        self.tickers = ["SOL-PERP"]
        self.client = SolanaClient(endpoint=endpoint, commitment=commitment)
        self.commitment = commitment

        # Set up Perp class
        _perp = Perp(self.client, "mainnet", Keypair.generate())
        mpg_id = PublicKey(_perp.ADDRESSES["MPG_ID"])
        response = self.client.get_account_info(
            pubkey=PublicKey(mpg_id), commitment=commitment, encoding="base64"
        )

        # Since the client is broken atm we need to fetch mpg and mpgBytes manually and then pass it to new Perp class
        try:
            if response.value:
                r = response.value.data
                decoded = r[8:]
                mpg = MarketProductGroup.from_bytes(decoded)
                mpg_bytes = decoded
        except Exception as exc:
            raise KeyError("Wrong Market Product Group PublicKey") from exc

        # Create new Perp class with complete info
        self.perp = Perp(self.client, "mainnet", Keypair.generate(), mpg, mpg_bytes)

    async def get_onchain_orderbook(
        self, market_address: str
    ) -> dict[str, list[tuple[float, float]]]:
        try:
            product = Product(self.perp)
            product.init_by_name(market_address)

            bid_key = product.BIDS
            ask_key = product.ASKS

            bids_data = self.client.get_account_info(
                pubkey=PublicKey(bid_key), commitment=self.commitment, encoding="base64"
            )
            asks_data = self.client.get_account_info(
                pubkey=PublicKey(ask_key), commitment=self.commitment, encoding="base64"
            )

            if (not bids_data.value) or (not asks_data.value):
                LOGGER.error(f'GooseFX unable to load bids/asks for market {market_address}')
                raise ValueError

            r1 = bids_data.value.data
            r2 = asks_data.value.data

            bid_deserialized = Slab.deserialize(r1, 40)
            ask_deserialized = Slab.deserialize(r2, 40)

            ob_bids = bid_deserialized.getL2DepthJS(1_000, True)
            ob_asks = ask_deserialized.getL2DepthJS(1_000, True)

            processed_data = processOrderbook(
                ob_bids, ob_asks, product.tick_size, product.decimals
            )

            return {
                key: [(i["price"], i["size"]) for i in value]
                for key, value in processed_data.items()
            }
        except AttributeError:
            LOGGER.error(f"Error while collecting GooseFx {market_address} orderbook")
            return {"bids": [], "asks": []}

    async def update_orderbooks(self, timestamp: int) -> None:
        order_books = {
            ticker: await self.get_onchain_orderbook(ticker) for ticker in self.tickers
        }

        with db.get_db_session() as session:
            for ticker, orderbook in order_books.items():
                ob_liq_record = db.CLOBLiqudity(
                    dex=self.identifier,
                    pair=ticker,
                    market_address=ticker,
                    bids=orderbook["bids"],
                    asks=orderbook["asks"],
                    timestamp=timestamp,
                )
                session.add(ob_liq_record)
            session.commit()
