"""

"""
import logging
import os
import time
from abc import abstractmethod
from typing import List

from solana.exceptions import SolanaRpcException
from solders.transaction_status import UiConfirmedBlock, EncodedConfirmedTransactionWithStatusMeta, \
    EncodedTransactionWithStatusMeta

import db
from collection.shared.generic_connector import GenericSolanaConnector


LOG = logging.getLogger(__name__)

BATCH_SIZE = 100


class TXFromBlockConnector(GenericSolanaConnector):
    """
    Class to collect transaction data from Solana blocks.
    """
    protocol_public_keys: List[str] | None = None
    last_block_saved: int | None = None


    @property
    @abstractmethod
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:
        """Implement in subclasses to define the constant value"""
        pass

    def _get_data(self):
        """
        Collect transactions from blocks. Collected transactions are stored in `rel_transactions` attribute.
        """
        self.rel_transactions = list()
        for block_number in self.assignment:
            block = self._fetch_block(block_number)
            self._select_relevant_tx_from_block(block)

    def _select_relevant_tx_from_block(self, block: UiConfirmedBlock) -> None:
        """
        Select only relevant transactions based on public keys involved.
        """
        if block.transactions:
            transactions = [tx for tx in block.transactions if self._is_transaction_relevant(tx)]
            self.rel_transactions.extend(transactions)

    def _get_assignment(self) -> None:
        """
        Obtain assignment for data collection.
        """
        # Update for relevant PPKs
        self._get_protocol_public_keys()
        # receive block numbers ready for collection
        self._get_assigned_blocks()

    @abstractmethod
    def _get_assigned_blocks(self) -> None:
        """

        :return:
        """
        self.assignment = list()
        # TODO: make it more flexible. we want to be able to get assignments indirectly
        #  from db so several collectors can serve at once / or change status of tx while fetching tx_raw
        # Fetch first n blocks that contain transactions without tx_raw.
        with db.get_db_session() as session:
            distinct_slots = session.query(
                db.TransactionStatusWithSignature.slot
            ).filter(
                db.TransactionStatusWithSignature.tx_raw.is_(None)
            ).distinct().subquery()

            # Outer query to order the distinct slots and limit the results
            slots = session.query(
                distinct_slots.c.slot
            ).order_by(
                distinct_slots.c.slot
            ).limit(BATCH_SIZE).all()

        self.assignment = [i.slot for i in slots]

    def _get_protocol_public_keys(self) -> None:
        """
        Get list of public keys for relevant protocol from env variables.
        :return:
        """
        # get list of public keys from env variables.
        keys = os.getenv("PROTOCOL_PUBLIC_KEYS", "").split(',')
        if not self.protocol_public_keys:
            self.protocol_public_keys = keys
            return

        # check if new keys are added
        new_keys = set(keys) - set(self.protocol_public_keys)
        if new_keys:
            LOG.warning(f"New protocol(s) added to collection: {new_keys}")
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
                assert hasattr(transaction, 'value')
                signature = transaction.value.transaction.transaction.signatures[0]
                record = session.query(db.TransactionStatusWithSignature).filter_by(signature=str(signature)).first()

                # Check if the record exists.
                if record:
                    # Update the tx_raw field.
                    record.tx_raw = transaction.to_json()
                else:
                    # get sources from pubkeys
                    sources = self._get_tx_source(transaction)
                    # TODO: now we store new record for each source but
                    #  it's possible that some sources already can have record with the same signature
                    #  and we only need to assign tx_raw to this records
                    for source in sources:
                        new_record = db.TransactionStatusWithSignature(
                            source=source,
                            slot=transaction.value.slot,
                            signature=signature,
                            block_time=transaction.value.block_time,
                            tx_raw=transaction.to_json(),
                            collection_stream=self.COLLECTION_STREAM
                        )
                        session.add(new_record)

            # Commit the changes.
            session.commit()

    def _is_transaction_relevant(
        self,
        transaction: EncodedTransactionWithStatusMeta | EncodedConfirmedTransactionWithStatusMeta,
    ) -> bool:
        """
        Decide if transaction is relevant based on the presence of relevant address between transactions account keys.
        """
        relevant_pubkeys = [
            i for i in transaction.transaction.message.account_keys if str(i.pubkey) in self.protocol_public_keys  # type: ignore
        ]
        return bool(relevant_pubkeys)

    def _get_tx_source(
        self,
        transaction: EncodedTransactionWithStatusMeta | EncodedConfirmedTransactionWithStatusMeta
    ) -> List[str]:
        """
        Identify transaction source by matching present public keys with relevant protocols' public keys
        """
        assert hasattr(transaction, 'value')
        relevant_sources = [
            k for k in self.protocol_public_keys
            if k in [str(i.pubkey) for i in transaction.value.transaction.transaction.message.account_keys]
        ]
        if not relevant_sources:
            LOG.error(f"Transaction `{transaction.value.transaction.transaction.signatures[0]}`"
                      f" does not contain any relevant public keys.")

        return relevant_sources
