"""

"""
import logging
import time
from typing import List

from solana.exceptions import SolanaRpcException
from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
import solana.rpc.api
from solders.transaction_status import TransactionErrorFieldless

from collection.shared.generic_collector import GenericSolanaConnector
import db


LOGGER = logging.getLogger(__name__)

TX_BATCH_SIZE = 1000


class SignatureCollector(GenericSolanaConnector):
    def __init__(self, protocol: str):
        super().__init__()
        self.protocol = protocol  # TODO fixit
        self._oldest_signature: Signature | None = None  # The oldest signature from the oldest completed block
        self._signatures_completed: bool = False
        self._oldest_completed_slot: int = 0
        self._collected_signatures: List[RpcConfirmedTransactionStatusWithSignature] | None = None

    @property
    def _collection_completed(self) -> bool:
        """
        Flag to mark completion of collection.
        """
        return self._signatures_completed

    def _get_assignment(self) -> None:
        """
        Obtain assignment for data collection.
        """
        # if oldest obtained signature is defined, proceed to collection
        if self._oldest_signature:
            return
        # otherwise, get retrieve oldest signature from database.
        with db.get_db_session() as session:
            LOGGER.info("Getting the oldest stored signature for protocol = {}.".format(self.protocol))
            # Get the last signature collector recorded by `SignatureCollector` for given protocol
            oldest_signature = session.query(db.TransactionStatusWithSignature.signature) \
                .filter(db.TransactionStatusWithSignature.source == self.protocol) \
                .filter(db.TransactionStatusWithSignature.collection_stream == "signature") \
                .order_by(db.TransactionStatusWithSignature.id.desc()) \
                .first()
            # If no signatures collected yet, get signature from watershed block
            if not oldest_signature:
                LOGGER.warning(
                    "No signatures found for protocol = {}.".format(self.protocol)
                )
                self._get_watershed_block_signature()
                return

            oldest_signature = oldest_signature.signature
            LOGGER.info("The oldest stored signature = {} for protocol = {}.".format(oldest_signature, self.protocol))
            self._oldest_signature = Signature.from_string(oldest_signature)

    def _get_data(self) -> None:
        """
        Collect signatures with metadata through Solana API.
        """
        self._fetch_signatures()

    def _write_tx_data(self) -> None:
        """
        Write signatures and tx meta data to database.
        """
        with db.get_db_session() as session:
            if not self._collected_signatures:
                return
            for signature in self._collected_signatures:
                # store only transactions from slot with complete transaction history fetched.
                if signature.slot < self._oldest_completed_slot:
                    break

                tx_status_record = db.TransactionStatusWithSignature(
                    signature=str(signature.signature),
                    source=self.protocol,
                    slot=signature.slot,
                    block_time=signature.block_time,
                    collection_stream="signature"
                )
                session.add(tx_status_record)
                session.flush()  # Flush here to get the ID
                # store errors and/or memos to db if any
                if signature.err:
                    error = signature.err.to_json() if not isinstance(signature.err, TransactionErrorFieldless) else ""
                    tx_error_record = db.TransactionStatusError(
                        error_body=error,
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_error_record)
                if signature.memo:
                    tx_memo_record = db.TransactionStatusMemo(
                        memo_body=signature.memo,
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_memo_record)

                self._oldest_signature = signature.signature
            session.commit()

    def _fetch_signatures(self):
        """
        Fetch transaction signatures.
        Fetch only signatures that occurs before `self._oldest_signature` for the given protocol. If
        `self._oldest_signature` is None, fetch signatures starting from the latest one.
        """
        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(self.protocol),
                limit=TX_BATCH_SIZE,
                before=self._oldest_signature,
            )
            signatures = response.value
        except SolanaRpcException as e:  # Most likely to catch 503 here. If something else - we stuck in loop TODO fix
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(2)
            return self._fetch_signatures()

        if len(signatures) < TX_BATCH_SIZE:
            self._signatures_completed = True

        # Get the oldest block for which it is certain that we fetched all signatures.
        unique_slots = sorted(set([i.slot for i in signatures]))
        if len(unique_slots) < 2:  # TODO: take care of blocks hat contain more than 1000 transactions for one protocol
            LOGGER.warning(
                "Last batch for protocol = {} contains only signatures from a single slot = {}.".format(
                    self.protocol,
                    unique_slots[0],
                )
            )
            self._oldest_completed_slot = unique_slots[0]
        else:
            second_oldest_slot = unique_slots[1]
            self._oldest_completed_slot = second_oldest_slot

        self._collected_signatures = signatures

    def _get_watershed_block_signature(self):
        """
        Get signature from watershed block. Signature does not have to be from relevant protocol.
        """
        with db.get_db_session() as session:
            # Query the database for protocols with the given public keys
            watershed_block_record = session.query(db.Protocols.watershed_block).\
                filter(db.Protocols.public_key == self.protocol).first()
            if watershed_block_record:
                watershed_block_number = watershed_block_record[0]

        watershed_block = self._fetch_block(watershed_block_number)
        self._oldest_signature = watershed_block.transactions[0].transaction.signatures[0]  # type: ignore
        LOGGER.info("Signature = {} collected from watershed block `{}` for protocol = {}.".format(
            self._oldest_signature, watershed_block_number, self.protocol)
        )
