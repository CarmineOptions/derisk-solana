"""
Module dedicated to transaction parser for Kamino protocol.
"""
import os
import time
import traceback
import logging

from sqlalchemy.exc import OperationalError
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


def _get_parsing_task(signature_list_table: TransactionsList):
    try:
        with get_db_session() as session:
            if not (START_INDEX and END_INDEX):
                transactions = session.query(
                    signature_list_table
                ).filter_by(
                    is_parsed=False
                ).order_by(
                    signature_list_table.id
                ).limit(BATCH_SIZE).all()
                return transactions

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
            return transactions
    except OperationalError as e:
        LOGGER.error("When fetching parsing task OperationalError occured: %s. Waiting 120 to retry."
                     "\n Traceback: %s", str(e), traceback.format_exc())
        time.sleep(120)
        return _get_parsing_task(signature_list_table)


def _get_transaction_info(transaction, protocol_key):
    try:
        with get_db_session() as session:
            tx_data = session.query(
                TransactionStatusWithSignature.transaction_data,
                TransactionStatusWithSignature.slot
            ).filter(
                TransactionStatusWithSignature.signature == transaction.signature
            ).filter(
                TransactionStatusWithSignature.source == protocol_key
            ).first()
            return tx_data
    except OperationalError as e:
        LOGGER.error("When getting txn info: txn signature = `%s`."
                     "\n OperationalError occured: %s. Waiting 120 to retry."
                     "\n Traceback: %s", str(transaction.signature), str(e), traceback.format_exc())
        time.sleep(120)
        return _get_transaction_info(transaction, protocol_key)


def _parse_transactions(transactions_data, tx_decoder):
    try:
        transactions_to_update = []
        with get_db_session() as session:
            for transaction, tx_data_json, slot_number in transactions_data:
                try:
                    if not tx_data_json:
                        LOGGER.warning(f" NO data for transaction: {transaction.signature}")
                        transactions_to_update.append(transaction.id)
                        continue

                    transaction_data = EncodedTransactionWithStatusMeta.from_json(tx_data_json)
                    # Set up the decoder processor function
                    tx_decoder._processor = lambda x, time=transaction.block_time, block_number=slot_number, sess=session: \
                        tx_decoder.save_event_to_database(x, timestamp=time, block_number=block_number,
                                                          session=sess)  # pylint: disable=protected-access
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
            return transactions_to_update

    except OperationalError as e:
        LOGGER.error("When parsing transactions OperationalError occured: %s. Waiting 120 to retry."
                     "\n Traceback: %s", str(transaction.signature), str(e), traceback.format_exc())
        time.sleep(120)
        return _parse_transactions(transactions_data, tx_decoder)


def _report_parsed_transactions(signature_list_table, transactions_to_update):
    try:
        with get_db_session() as session:
            session.query(signature_list_table).filter(
                signature_list_table.id.in_(transactions_to_update)
            ).update({"is_parsed": True}, synchronize_session=False)
            session.commit()
            LOGGER.info(f"Successfully parsed and updated {len(transactions_to_update)} "
                        f"transactions. Last parsed transaction = `{transactions_to_update[-1]}`")

    except OperationalError as e:
        LOGGER.error("When reporting parsed transactions OperationalError occured: %s. Waiting 120 to retry."
                     "\n Traceback: %s", str(e), traceback.format_exc())
        time.sleep(120)
        _report_parsed_transactions(signature_list_table, transactions_to_update)


def process_transactions(
        parser: TransactionDecoder, signature_list_table: TransactionsList, protocol_key: str):
    LOGGER.info('Initiate transactions parsing...')
    # Create parser
    tx_decoder = parser()
    while True:
        transactions_data = []

        # get set of transactions to parse
        transactions = _get_parsing_task(signature_list_table)
        LOGGER.info(f"Fetched {len(transactions)} transactions for processing.")
        if not transactions:
            # wait if no transactions ready for parsing
            time.sleep(60)
            continue

        # fetch raw transaction data
        for transaction in transactions:
            tx_data = _get_transaction_info(transaction, protocol_key)
            if tx_data and tx_data.transaction_data:
                transactions_data.append((transaction, tx_data.transaction_data, tx_data.slot))

        # Parse transactions
        transactions_to_update = _parse_transactions(transactions_data, tx_decoder)

        # Update the database to mark transactions as parsed
        if transactions_to_update:
            _report_parsed_transactions(signature_list_table, transactions_to_update)
