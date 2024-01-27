"""
script to run tx_raw collection for mango transactions.
Transaction signatures are expected to be stored in the database.
"""
import logging

from src.transaction_collector import TransactionCollector

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    PPK = '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'

    print('Start collecting tx from mango protocol: ...')
    tx_collector = TransactionCollector(protocol_public_key=PPK, rate_limit = 1)

    tx_collector.fetch_raw_transactions_data()

    print('Done')

