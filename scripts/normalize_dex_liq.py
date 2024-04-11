"""
Script for running AMM liquidity collector.
"""

import logging

import sys
sys.path.append(".")

from src.protocols.dexes.liquidity_normalization.normalization import (
    normalize_dex_data_continuously,
)  # pylint: disable=C0413

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    normalize_dex_data_continuously()
