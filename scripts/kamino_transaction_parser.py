"""
Script for parsing Marginfi lending transactions.
"""
import logging

from db import KaminoTransactionsList
from src.parser import KaminoTransactionParser, process_transactions


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    process_transactions(parser=KaminoTransactionParser, signature_list_table=KaminoTransactionsList)
