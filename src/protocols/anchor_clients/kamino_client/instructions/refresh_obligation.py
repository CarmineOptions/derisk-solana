from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class RefreshObligationAccounts(typing.TypedDict):
    lending_market: Pubkey
    obligation: Pubkey


def refresh_obligation(
    accounts: RefreshObligationAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"!\x84\x93\xe4\x97\xc0HY"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
