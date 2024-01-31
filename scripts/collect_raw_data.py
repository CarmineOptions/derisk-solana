import logging
import os
import sys

sys.path.append(".")

import src.protocols.addresses
import src.transaction_collector



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    RPC_TOKEN = os.environ.get("RPC_TOKEN")
    if RPC_TOKEN is None:
        raise ValueError("no RPC_TOKEN env var")
    RATE_LIMIT = os.environ.get("RATE_LIMIT")
    if RATE_LIMIT is None:
        raise ValueError("no RATE_LIMIT env var")
    RATE_LIMIT = int(RATE_LIMIT)

    # Collect signatures and transactions for each lending protocol since origin.
    src.transaction_collector.collect_signatures_and_transactions(
        start_signatures={address: None for address in src.protocols.addresses.ALL_ADDRESSES.values()},
        rpc_token=RPC_TOKEN,
        rate=RATE_LIMIT,
    )