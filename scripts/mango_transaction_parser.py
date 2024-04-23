"""
Script for parsing Mango V4 lending transactions.
"""
import logging

from db import MangoTransactionsList
from src.parser.mango_parser_v2 import MangoTransactionParserV2
from src.parser.transactions_parser import process_transactions
from src.protocols.addresses import MANGO_ADDRESS


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions(
        parser=MangoTransactionParserV2, signature_list_table=MangoTransactionsList, protocol_key=MANGO_ADDRESS)  # type: ignore
