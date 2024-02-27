"""
Generic class for data collection from Solana chain
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import logging
import os
import time

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta

LOG = logging.getLogger(__name__)


@dataclass
class SolanaTransaction:
    block_time: int
    block_number: int
    tx_body: EncodedTransactionWithStatusMeta

    def is_relevant(self, ppks: List[str] | None) -> bool:
        """
        Determines if the transaction involves any of the specified public keys.

        This method checks if any of the public keys provided in the 'ppks' list
        are present in the transaction's account keys. It is used to filter transactions
        based on the involvement of specific protocols identified by their public keys.

        Parameters:
        - ppks (List[str]): A list of public key strings to check against the transaction's account keys.
        """
        if not ppks:
            ppks = []
        relevant_public_keys = [i for i in self.tx_body.transaction.message.account_keys if str(i.pubkey) in ppks]  # type: ignore
        return bool(relevant_public_keys)

    def sources(self, ppks: List[str]) -> List[str]:
        """
        Identify transaction source by matching present public keys with provided protocols' public keys
        """
        relevant_sources = [
            k for k in ppks
            if k in [str(i.pubkey) for i in self.tx_body.transaction.message.account_keys]  # type: ignore
        ]
        if not relevant_sources:
            LOG.error(f"Transaction `{self.tx_body.transaction.signatures[0]}`"
                      f" does not contain any relevant public keys.")

        return relevant_sources

    @property
    def signature(self) -> Signature:
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
        self.rel_transactions: List[SolanaTransaction] = list()

        # rate limiter
        self.rate_limit: int = int(os.getenv("RATE_LIMIT", ""))
        self._call_timestamps = []

        LOG.info(f"{self.__class__.__name__} is all set to collect.")

    def _get_rpc_url(self) -> None:
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            LOG.error("RPC url was not found in environment variables.")
        self.authenticated_rpc_url = rpc_url

    def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        k = 0
        start_time = time.time()
        while not self._collection_completed:
            if k % 10000 == 0:
                LOG.info(f"Iterations completed: {k}, in {time.time() - start_time:.1f} seconds.")
            self._get_assignment()
            self._get_data()
            self._write_tx_data()
            k += 1
        LOG.info(f"Collection completed for {self.__class__.__name__}.")

    def _fetch_block(self, block_number: int) -> List[SolanaTransaction]:
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
            LOG.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return self._fetch_block(block_number)

        return [
            SolanaTransaction(
                block_number=block_number,
                block_time=block.value.block_time if block.value.block_time else -1,
                tx_body=tx
            ) for tx in block.value.transactions if block.value.transactions  # type: ignore
        ]

    def _rate_limit_calls(self) -> None:
        """
        This method implements a rate-limiting mechanism to control the frequency of API calls.
        It ensures that the number of API calls does not exceed a predefined limit per second.
        If the limit is reached, it will pause the execution momentarily before allowing further API calls.
        """
        # Check if the number of calls made in the last second exceeds the maximum limit.
        while len(self._call_timestamps) >= self.rate_limit:
            # Calculate the time passed since the first call in the timestamp list.
            time_passed = time.time() - self._call_timestamps[0]

            if time_passed > 1:
                # More than a second has passed since the first call, remove it from the list.
                self._call_timestamps.pop(0)
            else:
                # Wait for the remainder of the second before allowing more calls.
                time.sleep(1 - time_passed)

        # Record the timestamp of the current call.
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
    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        raise NotImplementedError("Implement me!")
