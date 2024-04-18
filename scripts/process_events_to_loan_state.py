import logging
import sys

sys.path.append(".")

from src.loans.loan_state import process_events_continuously


if __name__ == "__main__":
    protocol = sys.argv[1]
    valid_protocols = {"marginfi", "mango", "kamino", "solend"}
    if protocol not in valid_protocols:
        raise ValueError(f"{protocol} is not a valid protocol")

    logging.basicConfig(level=logging.INFO)

    process_events_continuously(protocol)
