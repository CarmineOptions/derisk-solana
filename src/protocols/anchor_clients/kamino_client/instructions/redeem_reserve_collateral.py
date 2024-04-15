from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class RedeemReserveCollateralArgs(typing.TypedDict):
    collateral_amount: int


layout = borsh.CStruct("collateral_amount" / borsh.U64)


class RedeemReserveCollateralAccounts(typing.TypedDict):
    owner: Pubkey
    lending_market: Pubkey
    reserve: Pubkey
    lending_market_authority: Pubkey
    reserve_collateral_mint: Pubkey
    reserve_liquidity_supply: Pubkey
    user_source_collateral: Pubkey
    user_destination_liquidity: Pubkey


def redeem_reserve_collateral(
    args: RedeemReserveCollateralArgs,
    accounts: RedeemReserveCollateralAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["owner"], is_signer=True, is_writable=False),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["reserve_collateral_mint"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_liquidity_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_source_collateral"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["user_destination_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xeau\xb5}\xb9\x8e\xdc\x1d"
    encoded_args = layout.build(
        {
            "collateral_amount": args["collateral_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
