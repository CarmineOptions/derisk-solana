from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class RedeemFeesAccounts(typing.TypedDict):
    reserve: Pubkey
    reserve_liquidity_fee_receiver: Pubkey
    reserve_supply_liquidity: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey


def redeem_fees(
    accounts: RedeemFeesAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reserve_liquidity_fee_receiver"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_supply_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xd7'\xb4)\xad.\xf8\xdc"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
