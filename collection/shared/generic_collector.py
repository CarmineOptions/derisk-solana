"""

"""
from abc import ABC, abstractmethod
import logging
import os
from typing import List

import solana.rpc.api
from solders.transaction_status import EncodedTransactionWithStatusMeta, EncodedConfirmedTransactionWithStatusMeta

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
        while True:
            self._get_assignment()
            self._get_data()
            self._write_tx_data()

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
