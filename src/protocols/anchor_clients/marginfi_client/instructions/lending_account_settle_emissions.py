from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class LendingAccountSettleEmissionsAccounts(typing.TypedDict):
    marginfi_account: Pubkey
    bank: Pubkey


def lending_account_settle_emissions(
    accounts: LendingAccountSettleEmissionsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["bank"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa1:\x88\xae\xf2\xdf\x9c\xb0"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
