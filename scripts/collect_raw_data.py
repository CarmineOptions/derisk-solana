import argparse
import logging
import sys

sys.path.append(".")

import src.protocols.addresses
import src.transaction_collector



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--rpc_token', type=str, required=False, help='RPC access token')
    parser.add_argument('-r', '--rate', type=int, required=False, help='Rate limit')
    args = parser.parse_args()

    # Collect signatures and transactions for each lending protocol since origin.
    src.transaction_collector.collect_signatures_and_transactions(
        start_signatures={address: None for address in src.protocols.addresses.ALL_ADDRESSES.values()},
        rpc_token=args.rpc_token, 
        rate=args.rate, 
    )