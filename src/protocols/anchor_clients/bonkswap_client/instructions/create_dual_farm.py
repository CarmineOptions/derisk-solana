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


class CreateDualFarmArgs(typing.TypedDict):
    supply_marco: types.token.Token
    supply_project_first: types.token.Token
    duration: int
    bump: int


layout = borsh.CStruct(
    "supply_marco" / types.token.Token.layout,
    "supply_project_first" / types.token.Token.layout,
    "duration" / borsh.U64,
    "bump" / borsh.U8,
)


class CreateDualFarmAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    farm: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    token_marco: Pubkey
    token_project_first: Pubkey
    token_marco_account: Pubkey
    token_project_first_account: Pubkey
    admin_marco_account: Pubkey
    admin_project_first_account: Pubkey
    admin: Pubkey
    program_authority: Pubkey


def create_dual_farm(
    args: CreateDualFarmArgs,
    accounts: CreateDualFarmAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["farm"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_marco"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_project_first"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_marco_account"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_project_first_account"],
            is_signer=True,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["admin_marco_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["admin_project_first_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"*\xb4g\x8a\xce+\xd0b"
    encoded_args = layout.build(
        {
            "supply_marco": args["supply_marco"].to_encodable(),
            "supply_project_first": args["supply_project_first"].to_encodable(),
            "duration": args["duration"],
            "bump": args["bump"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
