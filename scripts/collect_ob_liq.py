"""
Script for running CLOB liquidity collector.
"""

import logging
import asyncio

import sys
sys.path.append(".")

from src.protocols.dexes.dexes import update_ob_dex_data_continuously # pylint: disable=C0413

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(update_ob_dex_data_continuously())
