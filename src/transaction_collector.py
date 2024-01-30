import os
import logging
import time
from typing import List

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
from solders.transaction_status import EncodedConfirmedTransactionWithStatusMeta, EncodedTransactionWithStatusMeta

from db_model import get_db_session, TransactionStatusWithSignature, TransactionStatusError, TransactionStatusMemo

LOGGER = logging.getLogger(__name__)

TX_BATCH_SIZE = 1000


class TransactionCollector:
    def __init__(self, protocol_public_key: str, rate_limit: int = 5, source_token: str | None = None):
        self.protocol_public_key = protocol_public_key
        if not source_token:
            self.solana_client = solana.rpc.api.Client(os.getenv("QUICKNODE_TOKEN"))
        else:
            self.solana_client = solana.rpc.api.Client(source_token)

        self._last_completed_slot: int = 0
        self._last_tx_signature: Signature | None = None
        self._last_tx_hit: bool = False

        self.max_calls_per_second = rate_limit
        self._call_timestamps = []

    def _rate_limit_calls(self):
        """
        Enforces rate limiting for API calls.

        This method implements a rate-limiting mechanism to control the frequency of API calls.
        It ensures that the number of API calls does not exceed a predefined limit per second.
        If the limit is reached, it will pause the execution momentarily before allowing further API calls.
        """
        # Check if the number of calls made in the last second exceeds the maximum limit
        while len(self._call_timestamps) >= self.max_calls_per_second:
            # Calculate the time passed since the first call in the timestamp list
            time_passed = time.time() - self._call_timestamps[0]

            if time_passed > 1:
                # More than a second has passed since the first call, remove it from the list
                self._call_timestamps.pop(0)
            else:
                # Wait for the remainder of the second before allowing more calls
                time.sleep(1 - time_passed)

        # Record the timestamp of the current call
        self._call_timestamps.append(time.time())

    def _fetch_transaction_signatures(self) -> List[RpcConfirmedTransactionStatusWithSignature]:
        """
        Fetch transaction signatures.
        Fetch only transactions appeared before self._last_tx_signature. If None - fetch starting from the latest.
        :return: list of transactions.
        """
        self._rate_limit_calls()

        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(self.protocol_public_key),
                limit=TX_BATCH_SIZE,
                before=self._last_tx_signature
            )
            transactions = response.value
        except SolanaRpcException as e:  # Most likely to catch 503 here. If something else - we stuck in loop TODO fix
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(2)
            return self._fetch_transaction_signatures()

        if len(transactions) < TX_BATCH_SIZE:
            self._last_tx_hit = True

        # get last slot for which we fetched all transactions
        unique_slots = sorted(set([i.slot for i in transactions]))
        if len(unique_slots) < 2:
            LOGGER.warning(f"Last batch of size {TX_BATCH_SIZE} contains only transactions"
                           f" from single slot: {unique_slots[0]}")
            self._last_completed_slot = unique_slots[0]
        else:
            second_last_slot = unique_slots[1]
            self._last_completed_slot = second_last_slot

        return transactions

    def set_last_transaction_recorded(self):
        """ Obtain the last signature recorded for current protocol. """
        with get_db_session() as session:
            latest_transaction = session.query(TransactionStatusWithSignature.signature) \
                .filter(TransactionStatusWithSignature.source == self.protocol_public_key) \
                .order_by(TransactionStatusWithSignature.id.desc()) \
                .first()
            if not latest_transaction:
                LOGGER.warning(f"No signatures found for `{self.protocol_public_key}`."
                               f" Signatures will be collected from the latest at the moment.")
                return
            latest_signature = latest_transaction[0]
            LOGGER.info(f"The latest stored signature obtained: {latest_signature}")
            self._last_tx_signature = Signature.from_string(latest_signature)

    def _add_transactions_to_db(self, transactions: List[RpcConfirmedTransactionStatusWithSignature]) -> None:
        """
        Write transaction signatures to db
        :param transactions: fetched transactions
        """
        with get_db_session() as session:
            for transaction in transactions:
                # store only transactions from slot with complete transaction history fetched.
                if transaction.slot < self._last_completed_slot:
                    break

                tx_status_record = TransactionStatusWithSignature(
                    signature=str(transaction.signature),
                    source=self.protocol_public_key,
                    slot=transaction.slot,
                    block_time=transaction.block_time
                )
                session.add(tx_status_record)
                session.flush()  # Flush here to get the ID
                # store errors and/or memos to db if any
                if transaction.err:
                    tx_error_record = TransactionStatusError(
                        error_body=transaction.err.to_json(),
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_error_record)
                if transaction.memo:
                    tx_memo_record = TransactionStatusMemo(
                        memo_body=transaction.memo,
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_memo_record)

            self._last_tx_signature = transaction.signature
            session.commit()

    def collect_historic_transactions(self, last_tx_signature: Signature | None = None) -> Signature:
        """
        Fetch all transaction finilized before last_tx_signature.
        :param last_tx_signature:
        :return: Last available signature
        """
        LOGGER.info(f"Start collecting transactions for `{self.protocol_public_key}`.")
        if last_tx_signature:
            self._last_tx_signature = last_tx_signature

        while not self._last_tx_hit:
            transactions = self._fetch_transaction_signatures()
            if not transactions:
                break
            self._add_transactions_to_db(transactions)

        LOGGER.info(f"All available transactions are collected. The last signature: `{str(self._last_tx_signature)}`.")
        return last_tx_signature

    def collect_fresh_transactions(self):
        """
        Collection of fresh transactions, i.e. from the last on chain until the oldest (by block time) in database.
        """
        LOGGER.info("Start collecting fresh transactions.")
        while True:
            # get the freshest signature in database:
            with get_db_session() as session:
                try:
                    freshest_signature = session.query(TransactionStatusWithSignature.signature) \
                        .filter(TransactionStatusWithSignature.source == self.protocol_public_key) \
                        .order_by(TransactionStatusWithSignature.block_time.desc()) \
                        .first()[0]
                except TypeError:
                    LOGGER.error(f"No historical data in database for `{self.protocol_public_key}`.")

            # collect transactions until hit the freshest signature
            while True:
                transactions = self._fetch_fresh_transaction_signatures(freshest_signature)
                if not transactions:
                    break
                self._add_transactions_to_db(transactions)

    def _fetch_fresh_transaction_signatures(
            self, freshest_signature: Signature
    ) -> List[RpcConfirmedTransactionStatusWithSignature]:
        """
        Fetch transaction signatures.
        Fetch only transactions appeared before self._last_tx_signature. If None - fetch starting from the latest.
        :return: list of transactions.
        """
        self._rate_limit_calls()

        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(self.protocol_public_key),
                limit=TX_BATCH_SIZE,
                before=self._last_tx_signature,
                until=freshest_signature
            )
            transactions = response.value
        except SolanaRpcException as e:  # Most likely to catch 503 here. If something else - we stuck in loop TODO fix
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(2)
            return self._fetch_fresh_transaction_signatures(freshest_signature=freshest_signature)
            # get last slot for which we fetched all transactions

        unique_slots = sorted(set([i.slot for i in transactions]))
        if len(unique_slots) < 2:
            LOGGER.warning(f"Last batch of size {TX_BATCH_SIZE} contains only transactions"
                           f" from single slot: {unique_slots[0]}")
            self._last_completed_slot = unique_slots[0]
        else:
            second_last_slot = unique_slots[1]
            self._last_completed_slot = second_last_slot
        return transactions

    def _fetch_transactions_from_block(self, slot: int) -> List[EncodedConfirmedTransactionWithStatusMeta]:
        self._rate_limit_calls()

        # fetch block data
        try:
            block = self.solana_client.get_block(
                slot=slot,
                encoding='jsonParsed',
                max_supported_transaction_version=0
            )
        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return self._fetch_transactions_from_block(slot)

        # keep only transactions with protocol (program) public key involved.
        transactions = [tx for tx in block.value.transactions if self._is_transaction_relevant(tx)]
        return transactions

    def fetch_raw_transactions_by_block(self) -> None:
        """
        Fill transaction data to `tx_signatures.tx_raw` column if missing.
        """
        block_counter = 0
        start_time = time.time()

        with get_db_session() as session:
            while True:
                # Retrieve 200 transactions where tx_raw is NULL and source matches protocol_public_key
                slots = session.query(
                    TransactionStatusWithSignature.id,
                    TransactionStatusWithSignature.slot,
                ).filter(
                    TransactionStatusWithSignature.tx_raw.is_(None),
                    TransactionStatusWithSignature.source == self.protocol_public_key
                ).limit(200).all()

                if not slots:
                    time.sleep(5)
                    continue

                # fetch each slot one by one
                for slot in {slot for _, slot in slots}:
                    transactions = self._fetch_transactions_from_block(slot)

                    for transaction in transactions:
                        # update tx_raw for each transaction
                        signature = transaction.transaction.signatures[0]
                        self._update_tx_raw(signature, transaction.to_json())

                    block_counter += 1

                # Log every 10,000 slots
                if block_counter % 10000 == 0:
                    elapsed_time = time.time() - start_time
                    LOGGER.info(f"Processed {block_counter} slots in {elapsed_time:.2f} seconds")

    def _update_tx_raw(self, signature: Signature, new_tx_raw: str) -> None:
        """
        Update tx_signature (tx_raw) for given signature, if tx_raw is null, otherwise does nothing.
        :param signature: Signature
        :param new_tx_raw: jsonfyed transaction data
        """
        with get_db_session() as session:
            # Query for the record with the given signature and source
            record = session.query(TransactionStatusWithSignature).filter(
                TransactionStatusWithSignature.tx_raw.is_(None)
            ).filter_by(signature=str(signature), source=self.protocol_public_key).first()

            # Check if the record exists
            if record:
                # Update the tx_raw field
                record.tx_raw = new_tx_raw

                # Commit the changes
                session.commit()

    def fetch_raw_transactions_data(self) -> None:
        """
        Fill transaction data to `tx_signatures.tx_raw` column if missing.
        """
        transaction_counter = 0
        start_time = time.time()

        with get_db_session() as session:
            while True:
                # Retrieve 50 transactions where tx_raw is NULL and source matches protocol_public_key
                signatures = session.query(
                    TransactionStatusWithSignature.id,
                    TransactionStatusWithSignature.signature
                ).filter(
                    TransactionStatusWithSignature.tx_raw.is_(None),
                    TransactionStatusWithSignature.source == self.protocol_public_key
                ).limit(50).all()

                if not signatures:
                    time.sleep(5)
                    continue

                for tx_id, signature_str in signatures:
                    signature = Signature.from_string(signature_str)

                    transaction = self._fetch_tx_data(signature)

                    self._write_raw_tx(tx_id, transaction)
                    transaction_counter += 1

                    # Log every 10,000 transactions
                    if transaction_counter % 100000 == 0:
                        elapsed_time = time.time() - start_time
                        LOGGER.info(f"Processed {transaction_counter} transactions in {elapsed_time:.2f} seconds")

    @staticmethod
    def _write_raw_tx(transaction_id: int, transaction: EncodedConfirmedTransactionWithStatusMeta) -> None:
        """
        Write transaction data to`tx_signatute.tx_raw` for provided id
        :param transaction_id: `id` column
        :param transaction: EncodedConfirmedTransactionWithStatusMeta instance
        """
        try:
            # Serialize the transaction object to a JSON string
            tx_raw_data = transaction.to_json()
            with get_db_session() as session:
                # Find the transaction by ID and update its tx_raw field
                session.query(TransactionStatusWithSignature).filter(
                    TransactionStatusWithSignature.id == transaction_id
                ).update({"tx_raw": tx_raw_data})

                # Commit the changes to the database
                session.commit()

        except Exception as e:
            # Handle any exceptions (like serialization errors, database issues)  # TODO can be done better
            print(f"Error while writing raw transaction data for transaction ID {transaction_id}: {e}")

    def _fetch_tx_data(self, signature: Signature) -> EncodedConfirmedTransactionWithStatusMeta:
        """
        Use solana_client to get transaction data based on provided signature.
        :param signature: Signature
        :return: transaction data
        """
        self._rate_limit_calls()

        try:
            transaction = self.solana_client.get_transaction(
                signature,
                'jsonParsed',
                max_supported_transaction_version=0
            )
        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return self._fetch_tx_data(signature)

        return transaction.value

    def _is_transaction_relevant(
            self,
            transaction: EncodedTransactionWithStatusMeta | EncodedConfirmedTransactionWithStatusMeta
    ) -> bool:
        """
        Identify if transaction is relevant based on presence of program address between transactions account keys
        """

        relevant_pubkeys = [
            i for i in transaction.transaction.message.account_keys if str(i.pubkey) == self.protocol_public_key
        ]

        return bool(relevant_pubkeys)
