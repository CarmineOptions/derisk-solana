from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class DepositReserveLiquidityAndObligationCollateralArgs(typing.TypedDict):
    liquidity_amount: int


layout = borsh.CStruct("liquidity_amount" / borsh.U64)


class DepositReserveLiquidityAndObligationCollateralAccounts(typing.TypedDict):
    owner: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    reserve: Pubkey
    reserve_liquidity_supply: Pubkey
    reserve_collateral_mint: Pubkey
    reserve_destination_deposit_collateral: Pubkey
    user_source_liquidity: Pubkey
    user_destination_collateral: Pubkey
    instruction_sysvar_account: Pubkey


def deposit_reserve_liquidity_and_obligation_collateral(
    args: DepositReserveLiquidityAndObligationCollateralArgs,
    accounts: DepositReserveLiquidityAndObligationCollateralAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reserve_liquidity_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_collateral_mint"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_destination_deposit_collateral"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_source_liquidity"], is_signer=False, is_writable=True
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
    identifier = b"\x81\xc7\x04\x02\xde'\x1a."
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
