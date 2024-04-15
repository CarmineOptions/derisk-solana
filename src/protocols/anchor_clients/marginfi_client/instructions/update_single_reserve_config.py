from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class UpdateSingleReserveConfigArgs(typing.TypedDict):
    mode: int
    value: list[int]


layout = borsh.CStruct("mode" / borsh.U64, "value" / borsh.U8[32])


class UpdateSingleReserveConfigAccounts(typing.TypedDict):
    lending_market_owner: Pubkey
    lending_market: Pubkey
    reserve: Pubkey


def update_single_reserve_config(
    args: UpdateSingleReserveConfigArgs,
    accounts: UpdateSingleReserveConfigAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf8\xc3\xc0Z\xcc*\xa2\xe9"
    encoded_args = layout.build(
        {
            "mode": args["mode"],
            "value": args["value"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
