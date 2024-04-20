"""
Kamino transaction parser.
"""
from pathlib import Path
import logging
import os
from typing import Iterable

from anchorpy import EventParser
from anchorpy.program.common import Event
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta
import construct.core

from db import MangoParsedEvents
from src.parser.parser import TransactionDecoder
from src.protocols.addresses import MANGO_ADDRESS
from src.protocols.idl_paths import MANGO_IDL_PATH

LOGGER = logging.getLogger(__name__)


# moke function `construct.core.stream_read` to avoid StreamError while parsing mango event `UpdateIndexLog`
def stream_read_muted(stream, length, path):
    if length < 0:
        raise construct.core.StreamError("length must be non-negative, found %s" % length, path=path)
    try:
        data = stream.read(length)
    except Exception:
        raise construct.core.StreamError("stream.read() failed, requested %s bytes" % (length,), path=path)  # pylint: disable=raise-missing-from
    return data

construct.core.stream_read = stream_read_muted


def namedtuple_to_dict(obj):
    """Recursively convert nested namedtuple to dictionary."""
    if hasattr(obj, "_asdict"):  # Check if it's a namedtuple
        return {key: namedtuple_to_dict(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, dict)):
        return [namedtuple_to_dict(item) for item in obj]
    elif isinstance(obj, dict):  # Process values in the dictionary recursively
        return {key: namedtuple_to_dict(value) for key, value in obj.items()}
    else:
        return str(obj)


class MangoTransactionParserV2(TransactionDecoder):

    def __init__(
        self,
        path_to_idl: Path = Path(MANGO_IDL_PATH),
        program_id: Pubkey = Pubkey.from_string(MANGO_ADDRESS)
    ):
        self.event_counter: int | None = None
        super().__init__(path_to_idl, program_id)

    def save_event(self, event: Event) -> None:
        """
        Save event.
        """
        if event.name in [
            'PerpBalanceLog',
            'TokenBalanceLog',
            'FlashLoanLog',
            'FlashLoanLogV2',
            'FlashLoanLogV3',
            'WithdrawLog',
            'DepositLog',
            'FillLog',
            'FillLogV2',
            'FillLogV3',
            'PerpUpdateFundingLog',
            'PerpUpdateFundingLogV2',
            'UpdateIndexLog',
            'UpdateRateLog',
            'UpdateRateLogV2',
            'TokenLiqWithTokenLog',
            'TokenLiqWithTokenLogV2',
            'WithdrawLoanLog',
            'PerpLiqBaseOrPositivePnlLog',
            'PerpLiqBaseOrPositivePnlLogV2',
            'PerpLiqBaseOrPositivePnlLogV3',
            'PerpLiqBankruptcyLog',
            'PerpLiqNegativePnlOrBankruptcyLog',
            'PerpSettlePnlLog',
            'PerpSettleFeesLog',
            'FilledPerpOrderLog',
            'PerpTakerTradeLog',
            'PerpForceClosePositionLog',
            'TokenForceCloseBorrowsWithTokenLog',
            'TokenLiqBankruptcyLog',
            'TokenForceCloseBorrowsWithTokenLogV2',
            'TokenConditionalSwapCreateLog',
            'TokenConditionalSwapCreateLogV2',
            'TokenConditionalSwapCreateLogV3',
            'TokenConditionalSwapTriggerLog',
            'TokenConditionalSwapTriggerLogV2',
            'TokenConditionalSwapTriggerLogV3',
            'TokenConditionalSwapCancelLog',
            'TokenConditionalSwapStartLog',
            'DeactivateTokenPositionLog',
            'DeactivatePerpPositionLog',
            'TokenMetaDataLog',
            'TokenMetaDataLogV2',
            'PerpMarketMetaDataLog',
            'TokenCollateralFeeLog',
            'ForceWithdrawLog'
            'AccountBuybackFeesWithMngoLog',
            'Serum3OpenOrdersBalanceLog',
            'Serum3OpenOrdersBalanceLogV2'
        ]:
            event_name = event.name
            event_data = namedtuple_to_dict(event.data)
            event = MangoParsedEvents(
                transaction_id=str(self.transaction.transaction.signatures[0]),
                event_name=event_name,
                event_data=event_data
            )
            self._processor(event)

    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> None:
        """
        Decodes events

        Args:
            transaction_with_meta (EncodedTransactionWithStatusMeta): The transaction data with metadata.
        """
        self.transaction = transaction_with_meta
        if self.transaction.meta.err:
            return
        logs = self.transaction.meta.log_messages
        # This 2 discriminators are associated with 'PerpUpdateFundingLog' and 'PerpUpdateFundingLogV2'
        # and this 2 events are not parsable with anchorpy library due to missing attributes.
        # likely relevant only for old events
        logs = [log for log in logs if not ('vx89Qqxin' in log or 'dZKDSrOa2' in log)]
        parser = EventParser(self.program.program_id, self.program.coder)
        parser.parse_logs(logs, lambda x: self.save_event(x))



if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = MangoTransactionParserV2(
        Path(MANGO_IDL_PATH),
        Pubkey.from_string(MANGO_ADDRESS)
    )
    rpc_url = os.getenv("RPC_URL")
    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet
    transaction = solana_client.get_transaction(
        Signature.from_string(
            # '3QBx7uhgy4PBGWY93qpKgxv9WDS2BS7aWXNgDwHq4tgUXmNvvd6sUQUGzpoJCqwVx5w9MzPL3rzqX2yiwW9R75kD'  # liq
            # '2EPKbJ9bBweZ2mu29qUPhjXc2wX37KLTEzvvAwkw7cmjtXETXFTT5CpdwA7LByZD1s3QpYkLkAeeoGmJdtebwWxF'
            '2H4DKRbRaEDLvnkEu5ZSXQ6Tuay1NE6YnBsr5auw21Cus4KoKFEq5bcprcWtTTUAkgGZUxZ8TQm6VoeSemb7C6iy'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
