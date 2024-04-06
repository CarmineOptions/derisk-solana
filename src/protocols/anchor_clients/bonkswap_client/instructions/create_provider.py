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


class CreateProviderArgs(typing.TypedDict):
    token_x_amount: types.token.Token
    token_y_amount: types.token.Token
    bump: int


layout = borsh.CStruct(
    "token_x_amount" / types.token.Token.layout,
    "token_y_amount" / types.token.Token.layout,
    "bump" / borsh.U8,
)


class CreateProviderAccounts(typing.TypedDict):
    pool: Pubkey
    farm: Pubkey
    provider: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    owner_x_account: Pubkey
    owner_y_account: Pubkey
    owner: Pubkey


def create_provider(
    args: CreateProviderArgs,
    accounts: CreateProviderAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["farm"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["provider"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["owner_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["owner_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"J5\xd3\xae&\xa8\xe3\xb1"
    encoded_args = layout.build(
        {
            "token_x_amount": args["token_x_amount"].to_encodable(),
            "token_y_amount": args["token_y_amount"].to_encodable(),
            "bump": args["bump"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
