"""
Class for collection of transaction data from Solana chain
"""
from abc import abstractmethod
from typing import List
import logging
import os

from sqlalchemy.exc import IntegrityError
from solders.transaction_status import UiConfirmedBlock, EncodedConfirmedTransactionWithStatusMeta, \
    EncodedTransactionWithStatusMeta

from collection.shared.generic_collector import GenericSolanaConnector
import db


LOG = logging.getLogger(__name__)


class TXFromBlockCollector(GenericSolanaConnector):
    """
    Class to collect transaction data from Solana blocks.
    """
    protocol_public_keys: List[str] | None = None

    @property
    @abstractmethod
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:  # pylint: disable=invalid-name
        """Implement in subclasses to define the constant value"""
        raise NotImplementedError("Implement me!")

    def _get_data(self):
        """
        Collect transactions from blocks. Collected transactions are stored in `rel_transactions` attribute.
        """
        self.rel_transactions.clear()
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
        Obtains block numbers to fetch.
        """
        raise NotImplementedError("Implement me!")

    def _get_protocol_public_keys(self) -> None:
        """
        Get list of public keys for relevant protocol from env variables.
        :return:
        """
        # get list of public keys from env variables.
        keys = os.getenv("PROTOCOL_PUBLIC_KEYS", "").split(',')

        # check if new keys are added
        new_keys = set(keys) - set(self.protocol_public_keys)
        if new_keys:
            watershed_block = self._get_latest_finalized_block_on_chain()
            for new_key in new_keys:
                self._add_new_protocol(new_key, watershed_block)
            LOG.warning(f"New protocol(s) added to collection: {new_keys}")
        self.protocol_public_keys = keys

    @staticmethod
    def _add_new_protocol(public_key: str, watershed_block_number: int) -> None:
        """
        Adds new protocol to 'protocols' table, with last finalized block on chain serving as watershed block.
        """
        with db.get_db_session() as session:
            try:
                new_protocol = db.Protocols(
                    public_key=public_key,
                    watershed_block=watershed_block_number
                )

                # Add the new record to the session and commit it
                session.add(new_protocol)
                session.commit()
            except IntegrityError:
                session.rollback()  # roll back the session to a clean state
                LOG.error(f"A protocol with the public key `{public_key}` already exists in the database.")

    def _get_latest_finalized_block_on_chain(self) -> int:
        """
        Fetches number of the last finalized block.
        """
        self._rate_limit_calls()
        return self.solana_client.get_slot(commitment='finalized').value

    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        if self.rel_transactions:
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
                        # TODO: now we store new record for each source but  # pylint: disable=W0511
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
        self._report_collection()

    @abstractmethod
    def _report_collection(self):
        """
        Report collected blocks.
        :return:
        """
        raise NotImplementedError("Implement me!")

    def _is_transaction_relevant(
        self,
        transaction: EncodedTransactionWithStatusMeta | EncodedConfirmedTransactionWithStatusMeta,
    ) -> bool:
        """
        Decide if transaction is relevant based on the presence of relevant address between transactions account keys.
        """
        assert hasattr(transaction.transaction, 'message')
        relevant_pubkeys = [
            i for i in transaction.transaction.message.account_keys
            if str(i.pubkey) in self.protocol_public_keys  # type: ignore
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
            k for k in self.protocol_public_keys  # type: ignore
            if k in [str(i.pubkey) for i in transaction.value.transaction.transaction.message.account_keys]
        ]
        if not relevant_sources:
            LOG.error(f"Transaction `{transaction.value.transaction.transaction.signatures[0]}`"
                      f" does not contain any relevant public keys.")

        return relevant_sources
