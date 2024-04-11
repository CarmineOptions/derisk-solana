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
        transactions_to_update = []
        transactions_data = []

        # Minimize the DB session scope to only fetching necessary data
        with get_db_session() as session:
            transactions = session.query(MarginfiTransactionsList).filter_by(is_parsed=False).limit(BATCH_SIZE).all()
            LOGGER.info(f"Fetched {len(transactions)} transactions for processing.")

            for transaction in transactions:
                tx_data = session.query(TransactionStatusWithSignature.transaction_data).filter(
                    TransactionStatusWithSignature.signature == transaction.signature
                ).first()
                if tx_data and tx_data.transaction_data:
                    transactions_data.append((transaction, tx_data.transaction_data))

        # Process transactions outside the DB session
        for transaction, tx_data_json in transactions_data:
            transaction_data = EncodedTransactionWithStatusMeta.from_json(tx_data_json)
            # Set up the decoder processor function
            tx_decoder._processor = lambda x: tx_decoder.save_event_to_database(x, timestamp=transaction.block_time)
            # Decode the transaction data
            tx_decoder.decode_tx(transaction_data)
            # Collect transactions that have been successfully parsed
            transactions_to_update.append(transaction.signature)

        # Update the database in a single operation to mark transactions as parsed
        if transactions_to_update:
            with get_db_session() as session:
                session.query(MarginfiTransactionsList).filter(
                    MarginfiTransactionsList.signature.in_(transactions_to_update)).update({"is_parsed": True},
                                                                                    synchronize_session='fetch')
                session.commit()
                LOGGER.info(f"Successfully parsed and updated {len(transactions_to_update)} transactions.")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions()
