from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class ClosePoolAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    farm: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    token_marco_account: Pubkey
    token_project_first_account: Pubkey
    token_project_second_account: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    buyback_x_account: Pubkey
    buyback_y_account: Pubkey
    admin: Pubkey
    program_authority: Pubkey


def close_pool(
    accounts: ClosePoolAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["farm"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["token_marco_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_project_first_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["token_project_second_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["buyback_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["buyback_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x8c\xbd\xd1\x17\xef>\xef\x0b"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
