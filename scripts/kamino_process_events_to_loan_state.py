import logging
import sys

sys.path.append(".")

import src.loans.loan_state


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    src.loans.loan_state.process_events_continuously(protocol='kamino')
