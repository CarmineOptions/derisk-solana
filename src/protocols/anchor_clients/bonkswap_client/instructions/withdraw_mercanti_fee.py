from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class WithdrawMercantiFeeAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    mercanti_x_account: Pubkey
    mercanti_y_account: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    admin: Pubkey
    program_authority: Pubkey


def withdraw_mercanti_fee(
    accounts: WithdrawMercantiFeeAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["mercanti_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["mercanti_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["program_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xfd\xe5\x81%/H\x0b\xf0"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
