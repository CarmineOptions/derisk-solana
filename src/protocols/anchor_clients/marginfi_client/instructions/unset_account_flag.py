from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class UnsetAccountFlagArgs(typing.TypedDict):
    flag: int


layout = borsh.CStruct("flag" / borsh.U64)


class UnsetAccountFlagAccounts(typing.TypedDict):
    marginfi_group: Pubkey
    marginfi_account: Pubkey
    admin: Pubkey


def unset_account_flag(
    args: UnsetAccountFlagArgs,
    accounts: UnsetAccountFlagAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_group"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"8Q8U\\1\xffF"
    encoded_args = layout.build(
        {
            "flag": args["flag"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
