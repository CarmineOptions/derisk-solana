"""
Generic class for data collection from Solana chain
"""
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple
import logging
import os
import time

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiConfirmedBlock

LOGGER = logging.getLogger(__name__)


def log_performance_time(logger = LOGGER):
    """
    Decorator for logging performance time of subjected function.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            log_message = f"START: function '{func.__name__}'."
            # Log the start of the function
            logger.info(log_message)

            # Call the actual function
            result = func(*args, **kwargs)

            # Calculate elapsed time and log the end of the function
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"DONE: function '{func.__name__}' in {elapsed_time:.2f} seconds")

            return result

        return wrapper
    return decorator


@dataclass
class SolanaTransaction:
    block_time: int
    block_number: int
    tx_body: EncodedTransactionWithStatusMeta

    def sources(self, ppks: List[str]) -> List[str]:
        """
        Identify transaction source by matching present public keys with provided protocols' public keys
        """
        relevant_sources = [
            k for k in ppks
            if k in [str(i.pubkey) for i in self.tx_body.transaction.message.account_keys]  # type: ignore
        ]
        if not relevant_sources:
            LOGGER.error(f"Transaction `{self.tx_body.transaction.signatures[0]}`"
                         f" does not contain any relevant public keys.")

        return relevant_sources

    @property
    def first_signature(self) -> Signature:
        """ Returns transaction signature. """
        return self.tx_body.transaction.signatures[0]


class GenericSolanaConnector(ABC):
    """
    Abstract class with methods, that every Solana connector should implement.
    """

    def __init__(self):
        self._get_rpc_url()
        self.solana_client: solana.rpc.api.Client = solana.rpc.api.Client(self.authenticated_rpc_url)

        self.assignment: List[int] = list()

        # attribute for storing transactions before assigning to db.
        self.relevant_transactions: List[SolanaTransaction] = list()

        # rate limiter
        self._set_rate_limit()
        self._call_timestamps: deque[float] = deque(maxlen=self.rate_limit)

        LOGGER.info(f"{self.__class__.__name__} is all set to collect.")

    def _get_rpc_url(self) -> None:
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            LOGGER.error("RPC url was not found in environment variables.")
        self.authenticated_rpc_url = rpc_url

    def _set_rate_limit(self) -> None:
        rate_limit = os.getenv("RATE_LIMIT", None)
        if not rate_limit:
            LOGGER.error("Rate limit was not found in environment variables and set to 1.")
            self.rate_limit = 1
            return
        self.rate_limit = int(rate_limit)

    def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        k = 0
        start_time = time.time()
        while not self._collection_completed:
            if k % 10000 == 0:
                LOGGER.info(f"Iterations completed: {k}, in {time.time() - start_time:.1f} seconds.")
            self._get_assignment()
            self._get_data()
            self._write_data()
            k += 1
        LOGGER.info(f"Collection completed for {self.__class__.__name__}.")

    def _fetch_block(self, block_number: int) -> Tuple[UiConfirmedBlock, int]:
        """
        Use solana client to fetch block with provided number.
        """
        self._rate_limit_calls()
        # Fetch block data.
        try:
            block = self.solana_client.get_block(
                slot=block_number,
                encoding='jsonParsed',
                max_supported_transaction_version=0,
            )
        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return self._fetch_block(block_number)

        return block.value, block_number

    def _rate_limit_calls(self) -> None:
        """
        This method implements a rate-limiting mechanism to control the frequency of API calls.
        It ensures that the number of API calls does not exceed a predefined limit per second.
        If the limit is reached, it will pause the execution momentarily before allowing further API calls.
        """
        now = time.time()

        # Calculate the time to wait until making the next call
        time_to_wait = 1 - (now - self._call_timestamps[0])
        # If we've reached the rate limit and the time to wait is above 0.
        if len(self._call_timestamps) == self.rate_limit and time_to_wait > 0:
            # Wait for the required time
            time.sleep(time_to_wait)

        # Record the timestamp of the current call, discarding the oldest one.
        self._call_timestamps.append(time.time())

    @property
    def _collection_completed(self) -> bool:
        """
        Flag to mark completion of collection.
        """
        return False

    @abstractmethod
    def _get_assignment(self) -> None:
        """
        Obtain assignment for data collection.
        """
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def _get_data(self) -> None:
        """
        Collect required data through Solana API.
        """
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def _write_data(self) -> None:
        """
        Write raw tx data to database.
        """
        raise NotImplementedError("Implement me!")
