from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class SetNewAccountAuthorityAccounts(typing.TypedDict):
    marginfi_account: Pubkey
    marginfi_group: Pubkey
    signer: Pubkey
    new_authority: Pubkey
    fee_payer: Pubkey


def set_new_account_authority(
    accounts: SetNewAccountAuthorityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["marginfi_group"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["new_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["fee_payer"], is_signer=True, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x99\xa22T\xb6\xc9J\xb3"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
