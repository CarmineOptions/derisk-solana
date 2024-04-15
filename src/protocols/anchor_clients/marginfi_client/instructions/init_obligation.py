from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class InitObligationArgs(typing.TypedDict):
    args: types.init_obligation_args.InitObligationArgs


layout = borsh.CStruct("args" / types.init_obligation_args.InitObligationArgs.layout)


class InitObligationAccounts(typing.TypedDict):
    obligation_owner: Pubkey
    fee_payer: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    seed1_account: Pubkey
    seed2_account: Pubkey
    owner_user_metadata: Pubkey


def init_obligation(
    args: InitObligationArgs,
    accounts: InitObligationAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["obligation_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["fee_payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["seed1_account"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["seed2_account"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["owner_user_metadata"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xfb\n\xe7L\x1b\x0b\x9f`"
    encoded_args = layout.build(
        {
            "args": args["args"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
