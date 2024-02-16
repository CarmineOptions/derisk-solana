"""

"""
import logging
import os
import time
from typing import List

from solana.exceptions import SolanaRpcException
from solders.transaction_status import UiConfirmedBlock, EncodedConfirmedTransactionWithStatusMeta, \
    EncodedTransactionWithStatusMeta

import db
from collection.shared.generic_connector import GenericSolanaConnector


LOG = logging.getLogger(__name__)


class TXFromBlockConnector(GenericSolanaConnector):
    """
    Class to collect transaction data from Solana blocks.
    """
    protocol_public_keys: List[str] | None = None
    last_block_saved: int | None = None

    rel_transactions: List[EncodedConfirmedTransactionWithStatusMeta | EncodedTransactionWithStatusMeta] | None = None

    def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        raise NotImplementedError("Implement me!")

    def _get_protocol_public_keys(self) -> None:
        """
        Get list of public keys for relevant protocol from env variables.
        :return:
        """
        # get list of public keys from env variables.
        keys = os.getenv("PROTOCOL_PUBLIC_KEYS").split(',')
        if not self.protocol_public_keys:
            self.protocol_public_keys = keys
            return

        # check if new keys are added
        new_keys = set(keys) - set(self.protocol_public_keys)
        if new_keys:
            raise NotImplementedError("Implement storing new protocol watershed block!")

        self.protocol_public_keys = keys

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

    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        with db.get_db_session() as session:
            for transaction in self.rel_transactions:
                # Query for the record
                pass
        raise NotImplementedError("Implement me!")
