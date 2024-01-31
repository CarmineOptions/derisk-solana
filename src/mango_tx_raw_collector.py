"""
script to run tx_raw collection for mango transactions.
Transaction signatures are expected to be stored in the database.
"""
import argparse
import logging
import sys

sys.path.append(".")

from src.transaction_collector import TransactionCollector



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # parse arguments if any
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--authenticated_rpc_url', type=str, required=False, help='RPC access token')
    parser.add_argument('-r', '--rate', type=int, required=False, help='Rate limit')
    args = parser.parse_args()

    print('Start collecting tx from mango protocol: ...')
    tx_collector = TransactionCollector(
        addresses={'Mango': '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'},
        authenticated_rpc_url=args.authenticated_rpc_url,
        rate_limit=args.rate if args.rate else 5,
    )
    tx_collector.fetch_raw_transactions_by_block()

    print('Done')

