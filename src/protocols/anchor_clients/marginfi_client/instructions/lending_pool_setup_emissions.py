from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LendingPoolSetupEmissionsArgs(typing.TypedDict):
    flags: int
    rate: int
    total_emissions: int


layout = borsh.CStruct(
    "flags" / borsh.U64, "rate" / borsh.U64, "total_emissions" / borsh.U64
)


class LendingPoolSetupEmissionsAccounts(typing.TypedDict):
    marginfi_group: Pubkey
    admin: Pubkey
    bank: Pubkey
    emissions_mint: Pubkey
    emissions_auth: Pubkey
    emissions_token_account: Pubkey
    emissions_funding_account: Pubkey


def lending_pool_setup_emissions(
    args: LendingPoolSetupEmissionsArgs,
    accounts: LendingPoolSetupEmissionsAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["marginfi_group"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["admin"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["bank"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["emissions_mint"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["emissions_auth"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["emissions_token_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["emissions_funding_account"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xceax\xacq\xcc\xa9F"
    encoded_args = layout.build(
        {
            "flags": args["flags"],
            "rate": args["rate"],
            "total_emissions": args["total_emissions"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
