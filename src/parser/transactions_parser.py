from typing import Type
import logging

from solders.transaction_status import EncodedTransactionWithStatusMeta

from db import (
    TransactionStatusWithSignature,
    get_db_session,
    TransactionsList
)
from src.parser import TransactionDecoder

LOGGER = logging.getLogger(__name__)

BATCH_SIZE = 1000


def process_transactions(parser: Type[TransactionDecoder], signature_list_table: Type[TransactionsList]):
    LOGGER.info('Initiate transactions parsing...')
    # Create parser
    tx_decoder = parser()
    while True:
        transactions_to_update = []
        transactions_data = []

        # Minimize the DB session scope to only fetching necessary data
        with get_db_session() as session:
            transactions = session.query(signature_list_table).filter_by(is_parsed=False).limit(BATCH_SIZE).all()
            LOGGER.info(f"Fetched {len(transactions)} transactions for processing.")

            for transaction in transactions:
                tx_data = session.query(TransactionStatusWithSignature.transaction_data, TransactionStatusWithSignature.slot).filter(
                    TransactionStatusWithSignature.signature == transaction.signature
                ).first()
                if tx_data and tx_data.transaction_data:
                    transactions_data.append((transaction, tx_data.transaction_data, tx_data.slot))

        # Parse transactions
        with get_db_session() as session:
            for transaction, tx_data_json, slot_number in transactions_data:
                transaction_data = EncodedTransactionWithStatusMeta.from_json(tx_data_json)
                # Set up the decoder processor function
                tx_decoder._processor = lambda x, block_time=transaction.block_time, block_number=slot_number, sess=session:\
                    tx_decoder.save_event_to_database(x, timestamp=block_time, block_number=block_number, session=sess)  # pylint: disable=protected-access
                # Decode the transaction data
                tx_decoder.parse_transaction(transaction_data)
                # Collect transactions that have been successfully parsed
                transactions_to_update.append(transaction.signature)
            session.commit()

        # Update the database in a single operation to mark transactions as parsed
        if transactions_to_update:
            with get_db_session() as session:
                session.query(signature_list_table).filter(
                    signature_list_table.signature.in_(transactions_to_update)
                ).update({"is_parsed": True}, synchronize_session=False)
                session.commit()
                LOGGER.info(f"Successfully parsed and updated {len(transactions_to_update)} "
                            f"transactions. Last parsed transaction = `{transactions_to_update[-1]}`")
