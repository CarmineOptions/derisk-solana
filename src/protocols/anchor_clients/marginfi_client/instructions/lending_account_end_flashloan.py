from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class LendingAccountEndFlashloanAccounts(typing.TypedDict):
    marginfi_account: Pubkey
    signer: Pubkey


def lending_account_end_flashloan(
    accounts: LendingAccountEndFlashloanAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"i|\xc9j\x99\x02\x08\x9c"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
