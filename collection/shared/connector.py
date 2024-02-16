"""

"""
from abc import ABC, abstractmethod
import logging
import os

import solana.rpc.api

LOG = logging.getLogger(__name__)


class GenericSolanaConnector(ABC):
    """
    Abstract class with methods, that every Solana connector should implement.
    """

    def __init__(self):
        self._get_rpc_url()
        self.solana_client: solana.rpc.api.Client = solana.rpc.api.Client(self.authenticated_rpc_url)
        LOG.info(f"{self.__class__.__name__} is all set to collect.")

    def _get_rpc_url(self):
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            LOG.error(f"RPC url was not found in environment variables.")
        self.authenticated_rpc_url = rpc_url

    @abstractmethod
    def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        raise NotImplementedError("Implement me!")
