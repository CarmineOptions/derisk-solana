"""
script to run signature collection for mango transactions.
Collection will start from the last stored to db or from the latest finalized on chain if db contains no signatures yet.
"""
import argparse
import logging
import sys

sys.path.append(".")

from src.transaction_collector import TransactionCollector



PPK = '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # parse arguments if any
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--rpc_token', type=str, required=False, help='RPC access token')
    parser.add_argument('-r', '--rate', type=int, required=False, help='Rate limit')
    args = parser.parse_args()

    print('Start collecting signatures from mango protocol: ...')
    tx_collector = TransactionCollector(
        addresses={'Mango': PPK},
        rpc_token=args.rpc_token,
        rate_limit=args.rate if args.rate else 5,
    )
    tx_collector.set_last_transaction_recorded()

    last_tx_sign = tx_collector.collect_historic_transactions()

    print(f"Oldest transaction found: `{last_tx_sign}`")

    # create new instance to reset internal counters
    tx_collector = TransactionCollector(
        addresses={'Mango': PPK},
        rpc_token=args.rpc_token,
        rate_limit=args.rate if args.rate else 5,
    )
    # collect fresh transactions
    tx_collector.collect_fresh_transactions()
