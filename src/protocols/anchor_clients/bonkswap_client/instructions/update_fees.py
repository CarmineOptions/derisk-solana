from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class UpdateFeesArgs(typing.TypedDict):
    new_buyback_fee: types.fixed_point.FixedPoint
    new_project_fee: types.fixed_point.FixedPoint
    new_provider_fee: types.fixed_point.FixedPoint
    new_mercanti_fee: types.fixed_point.FixedPoint


layout = borsh.CStruct(
    "new_buyback_fee" / types.fixed_point.FixedPoint.layout,
    "new_project_fee" / types.fixed_point.FixedPoint.layout,
    "new_provider_fee" / types.fixed_point.FixedPoint.layout,
    "new_mercanti_fee" / types.fixed_point.FixedPoint.layout,
)


class UpdateFeesAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    admin: Pubkey
    program_authority: Pubkey


def update_fees(
    args: UpdateFeesArgs,
    accounts: UpdateFeesAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xe1\x1b\r\x06ET\xac\xbf"
    encoded_args = layout.build(
        {
            "new_buyback_fee": args["new_buyback_fee"].to_encodable(),
            "new_project_fee": args["new_project_fee"].to_encodable(),
            "new_provider_fee": args["new_provider_fee"].to_encodable(),
            "new_mercanti_fee": args["new_mercanti_fee"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
