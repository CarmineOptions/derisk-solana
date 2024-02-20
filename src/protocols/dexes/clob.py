
import logging
import abc

from phoenix.client import PhoenixClient
from solana.rpc.commitment import Commitment
from solana.rpc.api import Client as SolanaClient
from pyserum.market import Market
from solana.publickey import PublicKey

from src.protocols.dexes.pairs import get_relevant_tickers
import db

LOGGER = logging.getLogger(__name__)

class CLOB():
    @abc.abstractmethod
    async def get_onchain_orderbook(self, market_address: str) -> dict[str, list[tuple[float, float]]]:
        pass
    
    @abc.abstractmethod
    async def update_orderbooks(self, timestamp: int) -> None:
        pass
    

class Phoenix(CLOB):
    def __init__(
            self,  
            commitment: Commitment = Commitment("finalized")
        ):
        self.identifier = "PHOENIX"
        self.tickers = get_relevant_tickers(self.identifier)
        self.client = PhoenixClient(commitment = commitment)

    async def get_onchain_orderbook(self, market_address: str) -> dict[str, list[tuple[float, float]]]:
        """
        Retrieves onchain orderbook data for single market.

        Parameters: 
        - market_address: Address of market for which to get the data.

        Returns: 
        - dict: Dictionary with two keys - bids and asks where both keys map to 
                list of two sized tuples (price, size) representing single price level 
        """
        market_pubkey = PublicKey(market_address)

        try: 
            
            # Set levels to 1_000 to fetch as much as possible
            ob =  await self.client.get_l2_book(market_pubkey, levels = 1_000) # type: ignore
            return {
                'bids': [(float(i.price), float(i.size)) for i in ob.bids],
                'asks': [(float(i.price), float(i.size)) for i in ob.asks]
            }
            
        except AttributeError:

            LOGGER.error(f"Unknown Phoenix market address: {market_address}")
            return {
                'bids': [],
                'asks': []
            }

    async def update_orderbooks(self, timestamp: int) -> None:
        '''
        Fetches orderbook data for all provided markets and pushes it to the database.

        Parameters: 
        - timestamp: Timestamp to use when storing data. Used to make some aggregations easier
                    accross all the different markets, since we don't need high precision.
        '''
        order_books = { 
            ticker: await self.get_onchain_orderbook(address)
            for ticker, address in self.tickers.items()
        }
        with db.get_db_session() as session:
            
            for ticker, orderbook in order_books.items():
                ob_liq_record = db.CLOBLiqudity(
                    dex = self.identifier,
                    pair = ticker,
                    market_address = self.tickers[ticker],
                    bids = orderbook['bids'],
                    asks = orderbook['asks'],
                    timestamp = timestamp
                )
                session.add(ob_liq_record)
            session.commit()

# TODO: To be implemented.
class OpenBook(CLOB):
    def __init__(
            self,  
            commitment: Commitment = Commitment("finalized")
        ):
        self.identifier = 'OPENBOOK'
        self.tickers = get_relevant_tickers(self.identifier)
        self.client = SolanaClient(
            "https://api.mainnet-beta.solana.com/", # Good enough for this use 
            commitment = commitment
        )

    async def get_onchain_orderbook(self, market_address: str) -> dict[str, list[tuple[float, float]]]:
        """
        Retrieves onchain orderbook data for single market.

        Parameters: 
        - market_address: Address of market for which to get the data.

        Returns: 
        - dict: Dictionary with two keys - bids and asks where both keys map to 
                list of two sized tuples (price, size) representing single price level 
        """

        market_pubkey = PublicKey(market_address)


        try: 
            
            # Set levels to 1_000 to fetch as much as possible
            market = Market.load(
                self.client, market_pubkey
            )

            bids = market.load_bids().get_l2(1_000)
            asks = market.load_asks().get_l2(1_000)

            return {
                'bids': [(i.price, i.size) for i in bids],
                'asks': [(i.price, i.size) for i in asks]
            }
            
        except AttributeError:

            LOGGER.error(f"Unknown OpenBook market address: {market_address}")
            return {
                'bids': [],
                'asks': []
            }
    
    async def update_orderbooks(self, timestamp: int) -> None:
        '''
        Fetches orderbook data for all provided markets and pushes it to the database.

        Parameters: 
        - timestamp: Timestamp to use when storing data. Used to make some aggregations easier
                    accross all the different markets, since we don't need high precision.
        '''
        order_books = { 
            ticker: await self.get_onchain_orderbook(address)
            for ticker, address in self.tickers.items()
        }   
        
        with db.get_db_session() as session:
            
            for ticker, orderbook in order_books.items():
                ob_liq_record = db.CLOBLiqudity(
                    dex = self.identifier,
                    pair = ticker,
                    market_address = self.tickers[ticker],
                    bids = orderbook['bids'],
                    asks = orderbook['asks'],
                    timestamp = timestamp
                )
                session.add(ob_liq_record)
            session.commit()

