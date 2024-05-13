import logging
import sys

sys.path.append(".")

import src.loans.loan_state


if __name__ == "__main__":
    protocol = sys.argv[1]
    valid_protocols = {"marginfi", "mango", "kamino", "solend"}
    if protocol not in valid_protocols:
        raise ValueError(f"{protocol} is not a valid protocol")

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    src.loans.loan_state.process_events_continuously(protocol)