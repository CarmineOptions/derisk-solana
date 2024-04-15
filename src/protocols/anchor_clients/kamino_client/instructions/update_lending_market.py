from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class UpdateLendingMarketArgs(typing.TypedDict):
    mode: int
    value: list[int]


layout = borsh.CStruct("mode" / borsh.U64, "value" / borsh.U8[72])


class UpdateLendingMarketAccounts(typing.TypedDict):
    lending_market_owner: Pubkey
    lending_market: Pubkey


def update_lending_market(
    args: UpdateLendingMarketArgs,
    accounts: UpdateLendingMarketAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=True
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd1\x9d5\xd2a\xb4\x1f-"
    encoded_args = layout.build(
        {
            "mode": args["mode"],
            "value": args["value"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
