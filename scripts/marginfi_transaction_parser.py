"""
Script for parsing Marginfi lending transactions.
"""
import logging

from db import MarginfiTransactionsList
from src.parser import MarginfiTransactionParser
from src.parser.transactions_parser import process_transactions

LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions(parser=MarginfiTransactionParser, signature_list_table=MarginfiTransactionsList)
