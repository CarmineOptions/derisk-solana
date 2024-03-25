from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class WithdrawLpFeeAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    provider: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    owner_x_account: Pubkey
    owner_y_account: Pubkey
    pool_x_account: Pubkey
    pool_y_account: Pubkey
    owner: Pubkey
    program_authority: Pubkey


def withdraw_lp_fee(
    accounts: WithdrawLpFeeAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["provider"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["owner_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["owner_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_x_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["pool_y_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=True),
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
    identifier = b"\x95\xa1\x02\xd5\xc3\x93*A"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
