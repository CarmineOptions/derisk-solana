import os
import logging
import time
from typing import List

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
from solders.transaction_status import EncodedConfirmedTransactionWithStatusMeta

from db_model import get_db_session, TransactionStatusWithSignature, TransactionStatusError, TransactionStatusMemo

LOGGER = logging.getLogger(__name__)

# pk = '6LtLpnUFNByNXLyCoK9wA2MykKAmQNZKBdY8s47dehDc'
PPK = '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'

TX_BATCH_SIZE = 1000


class TransactionCollector:
    def __init__(self, protocol_public_key: str, rate_limit: int = 5):
        self.protocol_public_key = protocol_public_key
        self.solana_client = solana.rpc.api.Client(os.getenv("QUICKNODE_TOKEN"))

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

    def _fetch_transactions(self) -> List[RpcConfirmedTransactionStatusWithSignature]:
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
            return self._fetch_transactions()

        if len(transactions) < TX_BATCH_SIZE:
            self._last_tx_hit = True

        return transactions

    def set_last_transaction_recorded(self):
        with get_db_session() as session:
            latest_transaction = session.query(TransactionStatusWithSignature.signature) \
                .filter(TransactionStatusWithSignature.source == self.protocol_public_key) \
                .order_by(TransactionStatusWithSignature.id.desc()) \
                .first()[0]
            LOGGER.info(f"Latest stored signature obtained: {latest_transaction}")
            self._last_tx_signature = Signature.from_string(latest_transaction)

    def _add_transactions_to_db(self, transactions: List[RpcConfirmedTransactionStatusWithSignature]) -> None:
        """
        Write transaction signatures to db
        :param transactions: fetched transactions
        """
        with get_db_session() as session:
            for transaction in transactions:
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

            session.commit()
        self._last_tx_signature = transactions[-1].signature

    def collect_transactions(self, last_tx_signature: Signature | None = None) -> Signature:
        """
        Fetch all transaction finilized before last_tx_signature.
        :param last_tx_signature:
        :return: Last available signature
        """
        LOGGER.info(f"Start collecting transactions for `{self.protocol_public_key}`.")
        if last_tx_signature:
            self._last_tx_signature = last_tx_signature

        while not self._last_tx_hit:
            transactions = self._fetch_transactions()
            if not transactions:
                break
            self._add_transactions_to_db(transactions)

        LOGGER.info(f'All available transactions are collected. The last signature: `{str(self._last_tx_signature)}`.')
        return last_tx_signature

    def fetch_raw_transactions_data(self) -> None:
        """
        Fill transaction data to `tx_signatures.tx_raw` column if missing.
        """
        LOGGER.info(f"Start collecting transaction raw data for `{self.protocol_public_key}`.")
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
                    time.sleep(3)
                    continue

                for tx_id, signature_str in signatures:
                    signature = Signature.from_string(signature_str)

                    transaction = self._fetch_tx_data(signature)

                    self._write_raw_tx(tx_id, transaction)
                    transaction_counter += 1

                    # Log every 10,000 transactions
                    if transaction_counter % 10000 == 0:
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    print('Start collecting tx from mango protocol: ...')
    tx_collector = TransactionCollector(protocol_public_key=PPK)
    tx_collector.set_last_transaction_recorded()

    last_tx_sign = tx_collector.collect_transactions()

    print(last_tx_sign)

