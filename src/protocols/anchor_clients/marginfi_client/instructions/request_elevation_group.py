from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class RequestElevationGroupArgs(typing.TypedDict):
    elevation_group: int


layout = borsh.CStruct("elevation_group" / borsh.U8)


class RequestElevationGroupAccounts(typing.TypedDict):
    owner: Pubkey
    obligation: Pubkey
    lending_market: Pubkey


def request_elevation_group(
    args: RequestElevationGroupArgs,
    accounts: RequestElevationGroupAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b'$w\xfb\x81"\xf0\x07\x93'
    encoded_args = layout.build(
        {
            "elevation_group": args["elevation_group"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
