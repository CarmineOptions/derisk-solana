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


class LendingPoolAddBankWithSeedArgs(typing.TypedDict):
    bank_config: types.bank_config_compact.BankConfigCompact
    bank_seed: int


layout = borsh.CStruct(
    "bank_config" / types.bank_config_compact.BankConfigCompact.layout,
    "bank_seed" / borsh.U64,
)


class LendingPoolAddBankWithSeedAccounts(typing.TypedDict):
    marginfi_group: Pubkey
    admin: Pubkey
    fee_payer: Pubkey
    bank_mint: Pubkey
    bank: Pubkey
    liquidity_vault_authority: Pubkey
    liquidity_vault: Pubkey
    insurance_vault_authority: Pubkey
    insurance_vault: Pubkey
    fee_vault_authority: Pubkey
    fee_vault: Pubkey


def lending_pool_add_bank_with_seed(
    args: LendingPoolAddBankWithSeedArgs,
    accounts: LendingPoolAddBankWithSeedAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_group"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["fee_payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["bank_mint"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["bank"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["liquidity_vault_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["liquidity_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["insurance_vault_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["insurance_vault"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["fee_vault_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["fee_vault"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"L\xd3\xd5\xabuN\x9eL"
    encoded_args = layout.build(
        {
            "bank_config": args["bank_config"].to_encodable(),
            "bank_seed": args["bank_seed"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
