from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class LendingAccountWithdrawEmissionsAccounts(typing.TypedDict):
    marginfi_group: Pubkey
    marginfi_account: Pubkey
    signer: Pubkey
    bank: Pubkey
    emissions_mint: Pubkey
    emissions_auth: Pubkey
    emissions_vault: Pubkey
    destination_account: Pubkey


def lending_account_withdraw_emissions(
    accounts: LendingAccountWithdrawEmissionsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_group"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["marginfi_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["signer"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["bank"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["emissions_mint"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["emissions_auth"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["emissions_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["destination_account"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xea\x16T\xd6v\xb0\x8c\xaa"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
