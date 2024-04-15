from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LendingAccountStartFlashloanArgs(typing.TypedDict):
    end_index: int


layout = borsh.CStruct("end_index" / borsh.U64)


class LendingAccountStartFlashloanAccounts(typing.TypedDict):
    marginfi_account: Pubkey
    signer: Pubkey
    ixs_sysvar: Pubkey


def lending_account_start_flashloan(
    args: LendingAccountStartFlashloanArgs,
    accounts: LendingAccountStartFlashloanAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["ixs_sysvar"], is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x0e\x83!\xdcQ\xba\xb4k"
    encoded_args = layout.build(
        {
            "end_index": args["end_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
