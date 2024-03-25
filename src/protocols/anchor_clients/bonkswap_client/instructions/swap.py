from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from .. import types
from ..program_id import PROGRAM_ID


class SwapArgs(typing.TypedDict):
    delta_in: types.token.Token
    price_limit: types.fixed_point.FixedPoint
    x_to_y: bool


layout = borsh.CStruct(
    "delta_in" / types.token.Token.layout,
    "price_limit" / types.fixed_point.FixedPoint.layout,
    "x_to_y" / borsh.Bool,
)


class SwapAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    swapper_x_account: Pubkey
    swapper_y_account: Pubkey
    swapper: Pubkey
    referrer_x_account: Pubkey
    referrer_y_account: Pubkey
    referrer: Pubkey
    program_authority: Pubkey


def swap(
    args: SwapArgs,
    accounts: SwapAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["swapper_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["swapper_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["swapper"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["referrer_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["referrer_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["referrer"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xf8\xc6\x9e\x91\xe1u\x87\xc8"
    encoded_args = layout.build(
        {
            "delta_in": args["delta_in"].to_encodable(),
            "price_limit": args["price_limit"].to_encodable(),
            "x_to_y": args["x_to_y"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
