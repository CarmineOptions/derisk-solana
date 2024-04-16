import logging
import sys

sys.path.append(".")

import src.loans


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    src.loans.loan_state.process_events_continuously()
