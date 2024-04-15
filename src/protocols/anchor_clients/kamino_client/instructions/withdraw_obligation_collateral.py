from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class WithdrawObligationCollateralArgs(typing.TypedDict):
    collateral_amount: int


layout = borsh.CStruct("collateral_amount" / borsh.U64)


class WithdrawObligationCollateralAccounts(typing.TypedDict):
    owner: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    withdraw_reserve: Pubkey
    reserve_source_collateral: Pubkey
    user_destination_collateral: Pubkey
    instruction_sysvar_account: Pubkey


def withdraw_obligation_collateral(
    args: WithdrawObligationCollateralArgs,
    accounts: WithdrawObligationCollateralAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["reserve_source_collateral"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_destination_collateral"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["instruction_sysvar_account"],
            is_signer=False,
            is_writable=False,
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"%t\xcdg\xf3\xc0\\\xc6"
    encoded_args = layout.build(
        {
            "collateral_amount": args["collateral_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
