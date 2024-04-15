from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class SocializeLossArgs(typing.TypedDict):
    liquidity_amount: int


layout = borsh.CStruct("liquidity_amount" / borsh.U64)


class SocializeLossAccounts(typing.TypedDict):
    risk_council: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    reserve: Pubkey
    instruction_sysvar_account: Pubkey


def socialize_loss(
    args: SocializeLossArgs,
    accounts: SocializeLossAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["risk_council"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["instruction_sysvar_account"],
            is_signer=False,
            is_writable=False,
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf5K[\x00\xeca\x13\x03"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
