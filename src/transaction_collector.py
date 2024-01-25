import os
import logging
import time
from typing import List

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature

from db_model import get_db_session, TransactionStatusWithSignature, TransactionStatusError, TransactionStatusMemo

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


# pk = '6LtLpnUFNByNXLyCoK9wA2MykKAmQNZKBdY8s47dehDc'
PPK = '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'

TX_BATCH_SIZE = 1000


class TransactionCollector:
    def __init__(self, protocol_public_key: str):
        self.protocol_public_key = protocol_public_key
        self.solana_client = solana.rpc.api.Client(os.getenv("QUICKNODE_TOKEN"))

        self._last_tx_signature: Signature | None = None
        self._last_tx_hit: bool = False

    def _fetch_transactions(self) -> List[RpcConfirmedTransactionStatusWithSignature]:
        """
        Fetch transaction signatures.
        Fetch only transactions appeared before self._last_tx_signature. If None - fetch starting from the latest.
        :return: list of transactions.
        """
        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(self.protocol_public_key),
                limit=TX_BATCH_SIZE,
                before=self._last_tx_signature
            )
            transactions = response.value
        except SolanaRpcException as e:  # Most likely to catch 503 here. If something else - we stuck in loop TODO fix
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(3)
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


if __name__ == '__main__':
    print('Start collecting tx from mango protocol: ...')
    tx_collector = TransactionCollector(protocol_public_key=PPK)
    tx_collector.set_last_transaction_recorded()

    last_tx_sign = tx_collector.collect_transactions()

    print(last_tx_sign)

