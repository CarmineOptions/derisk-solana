import logging
import sys

sys.path.append(".")

from src.loans.loan_state import process_events_continuously


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    process_events_continuously()
