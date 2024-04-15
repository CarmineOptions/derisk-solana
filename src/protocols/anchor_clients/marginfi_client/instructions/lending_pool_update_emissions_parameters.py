from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LendingPoolUpdateEmissionsParametersArgs(typing.TypedDict):
    emissions_flags: typing.Optional[int]
    emissions_rate: typing.Optional[int]
    additional_emissions: typing.Optional[int]


layout = borsh.CStruct(
    "emissions_flags" / borsh.Option(borsh.U64),
    "emissions_rate" / borsh.Option(borsh.U64),
    "additional_emissions" / borsh.Option(borsh.U64),
)


class LendingPoolUpdateEmissionsParametersAccounts(typing.TypedDict):
    marginfi_group: Pubkey
    admin: Pubkey
    bank: Pubkey
    emissions_mint: Pubkey
    emissions_token_account: Pubkey
    emissions_funding_account: Pubkey


def lending_pool_update_emissions_parameters(
    args: LendingPoolUpdateEmissionsParametersArgs,
    accounts: LendingPoolUpdateEmissionsParametersAccounts,
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
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"7\xd5\xe0\xa8\x995\xc5("
    encoded_args = layout.build(
        {
            "emissions_flags": args["emissions_flags"],
            "emissions_rate": args["emissions_rate"],
            "additional_emissions": args["additional_emissions"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
