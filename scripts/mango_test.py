from pathlib import Path
from typing import Any, List, Tuple
import logging
import os
import re

from base58 import b58decode
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from db import MangoParsedTransactions, MangoLendingAccounts
from src.parser import MangoTransactionParser
from src.protocols.addresses import MANGO_ADDRESS
from src.protocols.idl_paths import MANGO_IDL_PATH




if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = MangoTransactionParser()

    token = os.getenv("RPC_URL")

    solana_client = Client(
        token)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '5j9q5EQc9GdgvQbSRh9ZMwEbyZdTEpPAEKE6HbAC6mKq6QcCBw7kjvvY4A3s1SMpFfWUnfNQwuQ5YPSzSXSCRC2y'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
