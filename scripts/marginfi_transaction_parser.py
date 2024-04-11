"""
Script for parsing Marginfi lending transactions.
"""
import logging
from pathlib import Path

from solders.pubkey import Pubkey
from solders.transaction_status import EncodedTransactionWithStatusMeta

from db import (
    TransactionStatusWithSignature,
    get_db_session,
    MarginfiTransactionsList
)
from src.parser import MarginfiTransactionParser
from src.protocols.idl_paths import MARGINFI_IDL_PATH
from src.protocols.addresses import MARGINFI_ADDRESS


LOGGER = logging.getLogger(__name__)

BATCH_SIZE = 500


def process_transactions():
    LOGGER.info('Initiate Marginfi transactions parsing...')
    # Create parser
    tx_decoder = MarginfiTransactionParser(
        Path(MARGINFI_IDL_PATH),
        Pubkey.from_string(MARGINFI_ADDRESS)
    )
    while True:
        # get transactions that are not yet parsed
        with get_db_session() as session:

            # Select a batch of transactions that haven't been parsed yet
            transactions = session.query(MarginfiTransactionsList).filter_by(is_parsed=False).limit(BATCH_SIZE).all()

            LOGGER.info(f"Start processing {len(transactions)} transactions.")
            for transaction in transactions:
                # Fetch the corresponding transaction_data from table for transactions.
                tx_data = session.query(TransactionStatusWithSignature.transaction_data).filter(
                    TransactionStatusWithSignature.signature == transaction.signature
                ).first()

                if tx_data and tx_data.transaction_data:
                    # get transaction from JSON
                    transaction_data = EncodedTransactionWithStatusMeta.from_json(tx_data.transaction_data)

                    # Decode the transaction data
                    # Decode the transaction data
                    tx_decoder._processor = lambda x: tx_decoder.save_event_to_database(x, timestamp=transaction.block_time)
                    tx_decoder.decode_tx(transaction_data)

                    # Mark the transaction as parsed
                    transaction.is_parsed = True

            # Commit the changes once all transactions in the batch have been processed
            session.commit()
        LOGGER.info("Transaction batch has been successfully parsed.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions()
