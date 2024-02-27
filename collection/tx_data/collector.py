"""
Class for collection of transaction data from Solana chain
"""
from abc import abstractmethod
from typing import List
import logging
import os

from solana.rpc.commitment import Commitment
from sqlalchemy.exc import IntegrityError

from collection.shared.generic_collector import GenericSolanaConnector, SolanaTransaction
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
            transactions = self._fetch_block(block_number)
            self._select_relevant_tx_from_block(transactions)

    def _select_relevant_tx_from_block(self, transactions: List[SolanaTransaction]) -> None:
        """
        Select only relevant transactions based on public keys involved.
        """
        if transactions:
            relevant_transactions = [tx for tx in transactions if tx.is_relevant(self.protocol_public_keys)]
            self.rel_transactions.extend(relevant_transactions)

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
        if not self.protocol_public_keys:
            self.protocol_public_keys = list()
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
        return self.solana_client.get_slot(commitment=Commitment('finalized')).value

    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        # if relevant transactions were not found in current iteration, do nothing.
        if not self.rel_transactions:
            return
        with db.get_db_session() as session:
            for transaction in self.rel_transactions:
                sources = transaction.sources(self.protocol_public_keys if self.protocol_public_keys else [])
                signature = transaction.signature
                # Same transaction has to be recorded once per each relevant protocol
                for source in sources:
                    record = session.query(db.TransactionStatusWithSignature).filter_by(
                        signature=str(signature),
                        source=source
                    ).first()

                    # Check if the record exists.
                    if record:
                        # Update the tx_raw field.
                        record.tx_raw = transaction.tx_body.to_json()
                    else:
                        new_record = db.TransactionStatusWithSignature(
                            source=source,
                            slot=transaction.block_number,
                            signature=str(signature),
                            block_time=transaction.block_time,
                            tx_raw=transaction.tx_body.to_json(),
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
