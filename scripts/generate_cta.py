import logging
import sys

sys.path.append(".")

import src.cta.cta


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	src.cta.cta.generate_cta_continuously()