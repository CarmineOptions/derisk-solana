import sys
import logging

from sqlalchemy import text

from db import get_db_session
from src.protocols.addresses import MANGO_ADDRESS, MARGINFI_ADDRESS, KAMINO_ADDRESS, SOLEND_ADDRESS

LOGGER = logging.getLogger(__name__)
BATCH_SIZE = 200


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
        with get_db_session() as session:
            last_record = session.execute(text(f"""
                 SELECT * FROM lenders.{transaction_reporting_table} ORDER BY id DESC limit 1;
             """)).fetchall()

            last_signature = last_record[0].signature

        with get_db_session() as session:
            last_collected_transaction = session.execute(text(f"""
                 SELECT *
                 FROM lenders.transactions
                 WHERE signature = '{last_signature}'
                     AND source = '{protocol_pubkey}'
                 limit 1;
             """)).fetchall()
            last_block = last_collected_transaction[0].slot

        with get_db_session() as session:
            batch_to_collect = session.execute(text(f"""
                 SELECT distinct slot
                 FROM lenders.transactions
                 WHERE 
                     slot > {last_block}
                     AND source = '{protocol_pubkey}'
                 ORDER BY slot
                 LIMIT {BATCH_SIZE};
             """)).fetchall()
            if not batch_to_collect:
                continue
            blocks_batch = [r.slot for r in batch_to_collect]

        with get_db_session() as session:
            session.execute(text(f"""
                 INSERT INTO lenders.{transaction_reporting_table} (signature, block_time, is_parsed)
                 SELECT 
                     signature, 
                     MIN(block_time) AS block_time,
                     FALSE AS is_parsed
                 FROM lenders.transactions
                 WHERE source = '{protocol_pubkey}' 
                 AND slot >= {min(blocks_batch)}
                 AND slot <= {max(blocks_batch)}
                 AND NOT EXISTS (
                    SELECT 1 FROM lenders.{transaction_reporting_table} t
                    WHERE t.signature = lenders.transactions.signature
                )
                 GROUP BY signature
                 ORDER BY MIN(block_time);
             """))
            session.commit()
        LOGGER.info(f"Transactions for {protocol} from block {min(blocks_batch)} up to block {max(blocks_batch)} ready to be parsed.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    protocol = sys.argv[1]
    valid_protocols = {"marginfi", "mango", "kamino", "solend"}
    if protocol not in valid_protocols:
        raise ValueError(f"{protocol} is not a valid protocol")

    data_pipeline(protocol)
