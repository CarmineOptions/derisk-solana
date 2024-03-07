from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class WithdrawRewardsAccounts(typing.TypedDict):
    state: Pubkey
    pool: Pubkey
    farm: Pubkey
    provider: Pubkey
    token_x: Pubkey
    token_y: Pubkey
    token_marco: Pubkey
    token_project_first: Pubkey
    token_project_second: Pubkey
    token_marco_account: Pubkey
    token_project_first_account: Pubkey
    token_project_second_account: Pubkey
    owner_marco_account: Pubkey
    owner_project_first_account: Pubkey
    owner_project_second_account: Pubkey
    owner: Pubkey
    program_authority: Pubkey


def withdraw_rewards(
    accounts: WithdrawRewardsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["state"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["pool"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["farm"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["provider"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["token_x"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_y"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["token_marco"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_project_first"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["token_project_second"], is_signer=False, is_writable=True
        ),
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
            pubkey=accounts["owner_marco_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["owner_project_first_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["owner_project_second_account"],
            is_signer=False,
            is_writable=True,
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
    identifier = b"\n\xd6\xdb\x8b\xcd\x16\xfb\x15"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
