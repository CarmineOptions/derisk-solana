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


class CreatePoolArgs(typing.TypedDict):
    lp_fee: types.fixed_point.FixedPoint
    buyback_fee: types.fixed_point.FixedPoint
    project_fee: types.fixed_point.FixedPoint
    mercanti_fee: types.fixed_point.FixedPoint
    initial_token_x: types.token.Token
    initial_token_y: types.token.Token
    bump: int


layout = borsh.CStruct(
    "lp_fee" / types.fixed_point.FixedPoint.layout,
    "buyback_fee" / types.fixed_point.FixedPoint.layout,
    "project_fee" / types.fixed_point.FixedPoint.layout,
    "mercanti_fee" / types.fixed_point.FixedPoint.layout,
    "initial_token_x" / types.token.Token.layout,
    "initial_token_y" / types.token.Token.layout,
    "bump" / borsh.U8,
)


class CreatePoolAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    admin_x_account: Pubkey
    admin_y_account: Pubkey
    admin: Pubkey
    project_owner: Pubkey
    program_authority: Pubkey


def create_pool(
    args: CreatePoolArgs,
    accounts: CreatePoolAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["admin_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["admin_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["project_owner"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xe9\x92\xd1\x8e\xcfh@\xbc"
    encoded_args = layout.build(
        {
            "lp_fee": args["lp_fee"].to_encodable(),
            "buyback_fee": args["buyback_fee"].to_encodable(),
            "project_fee": args["project_fee"].to_encodable(),
            "mercanti_fee": args["mercanti_fee"].to_encodable(),
            "initial_token_x": args["initial_token_x"].to_encodable(),
            "initial_token_y": args["initial_token_y"].to_encodable(),
            "bump": args["bump"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
