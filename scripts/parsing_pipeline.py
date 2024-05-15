import sys
import logging
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from db import get_db_session
from src.protocols.addresses import MANGO_ADDRESS, MARGINFI_ADDRESS, KAMINO_ADDRESS, SOLEND_ADDRESS

LOGGER = logging.getLogger(__name__)
BATCH_SIZE = 200


def fetch_last_record(table_name):
    try:
        with get_db_session() as session:
            last_record = session.execute(text(f"""
                SELECT * FROM lenders.{table_name} ORDER BY id DESC limit 1;
            """)).fetchall()
            return last_record[0].signature
    except OperationalError as e:
        LOGGER.error(f"Operational Error fetching last record: {e}. Wait 60s...")
        time.sleep(60)
        return fetch_last_record(table_name)


def fetch_last_transaction(signature, pubkey):
    try:
        with get_db_session() as session:
            last_transaction = session.execute(text(f"""
                SELECT *
                FROM lenders.transactions
                WHERE signature = '{signature}'
                    AND source = '{pubkey}'
                limit 1;
            """)).fetchall()
            return last_transaction[0].slot if last_transaction else None
    except OperationalError as e:
        LOGGER.error(f"Operational Error fetching last transaction: {e}. Wait 60s...")
        time.sleep(60)
        return fetch_last_transaction(signature, pubkey)


def fetch_batch_to_collect(block, pubkey, batch_size):
    try:
        with get_db_session() as session:
            batch = session.execute(text(f"""
                SELECT distinct slot
                FROM lenders.transactions
                WHERE 
                    slot > {block}
                    AND source = '{pubkey}'
                ORDER BY slot
                LIMIT {batch_size};
            """)).fetchall()
            return [r.slot for r in batch]
    except OperationalError as e:
        LOGGER.error(f"Operational Error fetching batch of blocks: {e}. Wait 60s...")
        time.sleep(60)
        return fetch_batch_to_collect(block, pubkey, batch_size)


def insert_transactions(table_name, pubkey, blocks_batch):
    try:
        with get_db_session() as session:
            session.execute(text(f"""
                INSERT INTO lenders.{table_name} (signature, block_time, is_parsed)
                SELECT 
                    signature, 
                    MIN(block_time) AS block_time,
                    FALSE AS is_parsed
                FROM lenders.transactions
                WHERE source = '{pubkey}' 
                AND slot >= {min(blocks_batch)}
                AND slot <= {max(blocks_batch)}
                AND NOT EXISTS (
                   SELECT 1 FROM lenders.{table_name} t
                   WHERE t.signature = lenders.transactions.signature
                )
                GROUP BY signature
                ORDER BY MIN(block_time);
            """))
            session.commit()
    except OperationalError as e:
        LOGGER.error(f"Operational Error when inserting signatures: {e}. Wait 60s...")
        time.sleep(60)
        return insert_transactions(table_name, pubkey, blocks_batch)


def data_pipeline(protocol):
    if protocol == 'marginfi':
        protocol_pubkey = MARGINFI_ADDRESS
        transaction_reporting_table = 'marginfi_hist_transaction_list_v2'
    elif protocol == 'solend':
        protocol_pubkey = SOLEND_ADDRESS
        transaction_reporting_table = 'solend_hist_transaction_list'
    elif protocol == 'kamino':
        protocol_pubkey = KAMINO_ADDRESS
        transaction_reporting_table = 'kamino_hist_transaction_list_v3'
    elif protocol == 'mango':
        protocol_pubkey = MANGO_ADDRESS
        transaction_reporting_table = 'mango_hist_transaction_list_v3'

    else:
        raise Exception(f"Wrong protocol selection: {protocol}")

    while True:
        LOGGER.info('Getting new batch...')

        # get the last transaction
        last_signature = fetch_last_record(transaction_reporting_table)
        if not last_signature:
            continue

        # get the last block
        last_block = fetch_last_transaction(last_signature, protocol_pubkey)
        if last_block is None:
            continue

        # get batch of blocks for collection
        blocks_batch = fetch_batch_to_collect(last_block, protocol_pubkey, BATCH_SIZE)
        if not blocks_batch:
            continue

        # add transactions to <protocol>_hist_transactions_table with is_parsed flag set to `False`
        insert_transactions(transaction_reporting_table, protocol_pubkey, blocks_batch)

        LOGGER.info(f"Transactions for {protocol} from block {min(blocks_batch)} "
                    f"up to block {max(blocks_batch)} ready to be parsed.")

        time.sleep(30)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    protocol = sys.argv[1]
    valid_protocols = {"marginfi", "mango", "kamino", "solend"}
    if protocol not in valid_protocols:
        raise ValueError(f"{protocol} is not a valid protocol")

    data_pipeline(protocol)
