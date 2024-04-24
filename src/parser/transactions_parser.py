"""
Module dedicated to transaction parser for Kamino protocol.
"""
import os
import time
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

START_INDEX = os.getenv('START_INDEX', None)
END_INDEX = os.getenv('END_INDEX', None)


def process_transactions(
        parser: Type[TransactionDecoder], signature_list_table: Type[TransactionsList], protocol_key: str):
    LOGGER.info('Initiate transactions parsing...')
    # Create parser
    tx_decoder = parser()
    while True:
        transactions_to_update = []
        transactions_data = []

        # Minimize the DB session scope to only fetching necessary data
        with get_db_session() as session:
            if not (START_INDEX and END_INDEX):
                transactions = session.query(
                    signature_list_table
                ).filter_by(
                    is_parsed=False
                ).order_by(
                    signature_list_table.id
                ).limit(BATCH_SIZE).all()
            else:
                LOGGER.info(f"Processing transactions {START_INDEX} - {END_INDEX}")
                transactions = (
                    session.query(signature_list_table)
                    .filter_by(is_parsed=False)
                    .filter(signature_list_table.id >= START_INDEX)
                    .filter(signature_list_table.id <= END_INDEX)
                    .order_by(signature_list_table.id)
                    .limit(BATCH_SIZE)
                    .all()
                )
            LOGGER.info(f"Fetched {len(transactions)} transactions for processing.")
            if not transactions:
                time.sleep(60)
                continue

            for transaction in transactions:
                tx_data = session.query(
                    TransactionStatusWithSignature.transaction_data,
                    TransactionStatusWithSignature.slot
                ).filter(
                    TransactionStatusWithSignature.signature == transaction.signature
                ).filter(
                    TransactionStatusWithSignature.source == protocol_key
                ).first()
                if tx_data and tx_data.transaction_data:
                    transactions_data.append((transaction, tx_data.transaction_data, tx_data.slot))

        # Parse transactions
        with get_db_session() as session:
            for transaction, tx_data_json, slot_number in transactions_data:
                try:
                    if not tx_data_json:
                        LOGGER.warning(f" NO data for transaction: {transaction.signature}")
                        transactions_to_update.append(transaction.id)
                        continue

                    transaction_data = EncodedTransactionWithStatusMeta.from_json(tx_data_json)
                    # Set up the decoder processor function
                    tx_decoder._processor = lambda x, time=transaction.block_time, block_number=slot_number, sess=session:\
                        tx_decoder.save_event_to_database(x, timestamp=time, block_number=block_number, session=sess)  # pylint: disable=protected-access
                    # Decode the transaction data
                    tx_decoder.parse_transaction(transaction_data)
                    # Collect transactions that have been successfully parsed
                    transactions_to_update.append(transaction.id)
                except KeyboardInterrupt as exc:
                    raise KeyboardInterrupt from exc
                except Exception as e:  # pylint: disable=broad-exception-caught
                    LOGGER.error(  # pylint: disable=logging-too-many-args
                        "While parsing transaction = `%s` \n an error occurred: %s",
                        str(transaction.signature),
                        str(e),
                        exc_info=True
                    )
                    transactions_to_update.append(transaction.id)
            session.commit()

        # Update the database in a single operation to mark transactions as parsed
        if transactions_to_update:
            with get_db_session() as session:
                session.query(signature_list_table).filter(
                    signature_list_table.id.in_(transactions_to_update)
                ).update({"is_parsed": True}, synchronize_session=False)
                session.commit()
                LOGGER.info(f"Successfully parsed and updated {len(transactions_to_update)} "
                            f"transactions. Last parsed transaction = `{transactions_to_update[-1]}`")
