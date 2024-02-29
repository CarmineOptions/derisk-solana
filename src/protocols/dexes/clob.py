"""
Module containes classes containing functionality for fetching CLOB Liqudity 
and pushing it to the database.
"""
import logging
import abc

from solana.publickey import PublicKey
from solana.keypair import Keypair
from phoenix.client import PhoenixClient
from solana.rpc.commitment import Commitment
from solana.rpc.api import Client as SolanaClient
from solana.publickey import PublicKey  # pylint: disable=E0611
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

        # Set up Perp class
        _perp = Perp(self.client, "mainnet", Keypair.generate())
        mpgId = PublicKey(_perp.ADDRESSES["MPG_ID"])
        response = self.client.get_account_info(
            pubkey=PublicKey(mpgId), commitment="processed", encoding="base64"
        )

        # Since the client is broken atm we need to fetch mpg and mpgBytes manually and then pass it to new Perp class
        try:
            if response.value:
                r = response.value.data
                decoded = r[8:]
                mpg = MarketProductGroup.from_bytes(decoded)
                marketProductGroup = mpg
                mpgBytes = decoded
        except:
            raise KeyError("Wrong Market Product Group PublicKey")

        # Create new Perp class with complete info
        self.perp = Perp(self.client, "mainnet", Keypair.generate(), mpg, mpgBytes)

    async def get_onchain_orderbook(
        self, market_address: str
    ) -> dict[str, list[tuple[float, float]]]:
        try:
            product = Product(self.perp)
            product.init_by_name(market_address)

            bidKey = product.BIDS
            askKey = product.ASKS

            bidsData = self.client.get_account_info(
                pubkey=PublicKey(bidKey), commitment="processed", encoding="base64"
            )
            asksData = self.client.get_account_info(
                pubkey=PublicKey(askKey), commitment="processed", encoding="base64"
            )

            r1 = bidsData.value.data
            r2 = asksData.value.data

            bidDeserialized = Slab.deserialize(r1, 40)
            askDeserialized = Slab.deserialize(r2, 40)

            obBids = bidDeserialized.getL2DepthJS(1_000, True)
            obAsks = askDeserialized.getL2DepthJS(1_000, True)

            processedData = processOrderbook(
                obBids, obAsks, product.tick_size, product.decimals
            )

            return {
                key: [(i["price"], i["size"]) for i in value]
                for key, value in processedData.items()
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
