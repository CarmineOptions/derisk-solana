"""
Script for parsing Marginfi lending transactions.
"""
import logging

from db import MarginfiTransactionsListV2
from src.parser.marginfi_parser_v2 import MarginfiTransactionParserV2
from src.parser.transactions_parser import process_transactions
from src.protocols.addresses import MARGINFI_ADDRESS


LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions(
        parser=MarginfiTransactionParserV2, signature_list_table=MarginfiTransactionsListV2, protocol_key=MARGINFI_ADDRESS)
