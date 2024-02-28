"""
Module contains `SignatureCollector`, class dedicated to collection history of transaction on Solana chain for
lending protocols.
Collection logic:
    t_O - watershed block, block that we assign as divider of historical and current data.
    Takes `t_0` from db.
    PPK (protocol public key) is collected from environmental variable.
    Collects all historical data as follows:
    1) starts from any transaction (`tx_0`) from block `t_0`.
    2) Collects 1000 tx signatures starting with `tx_0`.
    3) Collected transactions belong to sequence of blocks from `t_0` to `t_0 - k`.
    Store to tx_signatures table all transactions from blocks `t_0 - 1` to `t_0 - k + 1` with flag `from signatures`.
    If signature already exists - change flag to `from_signatures`.
    Transactions from block `t_0` are handled in current data collector.
    4) we get presumably the earliest transaction signature from `t_0 - k + 1` block and collect next 1000 tx.
    5) repeat 3-4 until reaching the first transaction.
    6) As first (earliest) transaction is reached - consider historical data (signatures only) for given PPK
    at time t_0 collected.
    If being restarted - fetch block number from last tx signature for given PPK and flag `signature`.
    Use this block instead of `t_0`
"""
import logging
import os
import time
from typing import List

from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
from solders.transaction_status import TransactionErrorFieldless
from solana.exceptions import SolanaRpcException
import solana.rpc.api

from collection.shared.generic_collector import GenericSolanaConnector
import db


LOGGER = logging.getLogger(__name__)

TX_BATCH_SIZE = 1000


class SignatureCollector(GenericSolanaConnector):
    def __init__(self):
        super().__init__()
        self.protocol = os.getenv("PROTOCOL_PUBLIC_KEY")
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
                .filter(db.TransactionStatusWithSignature.collection_stream == db.CollectionStreamTypes.SIGNATURE) \
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
        LOGGER.info(f"Collected {len(self._collected_signatures)} signatures for `{self.protocol}")

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
                    collection_stream=db.CollectionStreamTypes.SIGNATURE
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
        LOGGER.info(f"Signatures successfully stored to database.")

    def _fetch_signatures(self) -> None:
        """
        Fetch transaction signatures.
        Fetch only signatures that occurs before `self._oldest_signature` for the given protocol.
        """
        self._rate_limit_calls()

        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(self.protocol),
                limit=TX_BATCH_SIZE,
                before=self._oldest_signature,
            )
            signatures = response.value
        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(0.5)
            self._fetch_signatures()
            return

        if len(signatures) < TX_BATCH_SIZE:
            self._signatures_completed = True

        # Get the oldest block for which it is certain that we fetched all signatures.
        unique_slots = sorted(list({i.slot for i in signatures}))
        if len(unique_slots) < 2:  # TODO: take care of blocks hat contain more than 1000 transactions for one protocol  # pylint: disable=W0511
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

    def _get_watershed_block_signature(self) -> None:
        """
        Get signature from watershed block. Signature does not have to be from relevant protocol.
        """
        with db.get_db_session() as session:
            # Query the database for protocols with the given public keys
            watershed_block_record = session.query(db.Protocols.watershed_block).\
                filter(db.Protocols.public_key == self.protocol).first()
            if watershed_block_record:
                watershed_block_number = watershed_block_record[0]
            else:
                LOGGER.warning(f"Protocol {self.protocol} is not in the `protocols` table. "
                               f"Failing to collect watershed block number.")
                time.sleep(10)
                self._get_watershed_block_signature()
                return

        watershed_block, _ = self._fetch_block(watershed_block_number)
        watershed_block_transactions = watershed_block.transactions
        self._oldest_signature = watershed_block_transactions[0].transaction.signatures[0]
        LOGGER.info("Signature = {} collected from watershed block `{}` for protocol = {}.".format(
            self._oldest_signature, watershed_block_number, self.protocol)
        )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print('Start collecting signatures from Solana chain: ...')
    tx_collector = SignatureCollector()
    tx_collector.run()
