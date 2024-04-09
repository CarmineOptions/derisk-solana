"""
Script for parsing Marginfi lending transactions.
"""
import logging
from pathlib import Path

from solders.pubkey import Pubkey

from src.parser import MarginfiTransactionParser
from src.protocols.idl_paths import MARGINFI_IDL_PATH
from src.protocols.addresses import MARGINFI_ADDRESS

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    tx_decoder = MarginfiTransactionParser(
        Path(MARGINFI_IDL_PATH),
        Pubkey.from_string(MARGINFI_ADDRESS)
    )
