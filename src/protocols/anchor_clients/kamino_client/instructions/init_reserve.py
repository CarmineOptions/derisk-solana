from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class InitReserveAccounts(typing.TypedDict):
    lending_market_owner: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    reserve: Pubkey
    reserve_liquidity_mint: Pubkey
    reserve_liquidity_supply: Pubkey
    fee_receiver: Pubkey
    reserve_collateral_mint: Pubkey
    reserve_collateral_supply: Pubkey


def init_reserve(
    accounts: InitReserveAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market_owner"], is_signer=True, is_writable=True
        ),
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
            pubkey=accounts["reserve_liquidity_mint"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["reserve_liquidity_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["fee_receiver"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reserve_collateral_mint"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_collateral_supply"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x8a\xf5G\xe1\x99\x04\x03+"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
