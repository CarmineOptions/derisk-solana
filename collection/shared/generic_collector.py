"""

"""
from abc import ABC, abstractmethod
from typing import List
import logging
import os
import time

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.transaction_status import EncodedTransactionWithStatusMeta, EncodedConfirmedTransactionWithStatusMeta, \
    UiConfirmedBlock

LOG = logging.getLogger(__name__)


class GenericSolanaConnector(ABC):
    """
    Abstract class with methods, that every Solana connector should implement.
    """
    assignment: List[int] | None = None

    def __init__(self):
        self._get_rpc_url()
        self.solana_client: solana.rpc.api.Client = solana.rpc.api.Client(self.authenticated_rpc_url)

        self.rel_transactions: List[EncodedConfirmedTransactionWithStatusMeta | EncodedTransactionWithStatusMeta] = list()
        LOG.info(f"{self.__class__.__name__} is all set to collect.")

    def _get_rpc_url(self) -> None:
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            LOG.error(f"RPC url was not found in environment variables.")
        self.authenticated_rpc_url = rpc_url

    def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        while not self._collection_completed:
            self._get_assignment()
            self._get_data()
            self._write_tx_data()
        LOG.info(f"Collection completed for {self.__class__.__name__}.")

    def _fetch_block(self, block_number: int) -> UiConfirmedBlock:
        """
        Use solana client to fetch block with provided number.
        """
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

        return block.value

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
