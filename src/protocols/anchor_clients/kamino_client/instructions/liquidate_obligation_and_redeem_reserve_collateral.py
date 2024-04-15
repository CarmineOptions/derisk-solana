from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class LiquidateObligationAndRedeemReserveCollateralArgs(typing.TypedDict):
    liquidity_amount: int
    min_acceptable_received_collateral_amount: int
    max_allowed_ltv_override_percent: int


layout = borsh.CStruct(
    "liquidity_amount" / borsh.U64,
    "min_acceptable_received_collateral_amount" / borsh.U64,
    "max_allowed_ltv_override_percent" / borsh.U64,
)


class LiquidateObligationAndRedeemReserveCollateralAccounts(typing.TypedDict):
    liquidator: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    repay_reserve: Pubkey
    repay_reserve_liquidity_supply: Pubkey
    withdraw_reserve: Pubkey
    withdraw_reserve_collateral_mint: Pubkey
    withdraw_reserve_collateral_supply: Pubkey
    withdraw_reserve_liquidity_supply: Pubkey
    withdraw_reserve_liquidity_fee_receiver: Pubkey
    user_source_liquidity: Pubkey
    user_destination_collateral: Pubkey
    user_destination_liquidity: Pubkey
    instruction_sysvar_account: Pubkey


def liquidate_obligation_and_redeem_reserve_collateral(
    args: LiquidateObligationAndRedeemReserveCollateralArgs,
    accounts: LiquidateObligationAndRedeemReserveCollateralAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["liquidator"], is_signer=True, is_writable=False),
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
            pubkey=accounts["repay_reserve"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["repay_reserve_liquidity_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve_collateral_mint"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve_collateral_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve_liquidity_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["withdraw_reserve_liquidity_fee_receiver"],
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
        AccountMeta(
            pubkey=accounts["user_destination_liquidity"],
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
    identifier = b"\xb1G\x9a\xbc\xe2\x85J7"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
            "min_acceptable_received_collateral_amount": args[
                "min_acceptable_received_collateral_amount"
            ],
            "max_allowed_ltv_override_percent": args[
                "max_allowed_ltv_override_percent"
            ],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
