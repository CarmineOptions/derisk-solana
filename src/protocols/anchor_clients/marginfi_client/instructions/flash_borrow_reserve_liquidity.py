from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class FlashBorrowReserveLiquidityArgs(typing.TypedDict):
    liquidity_amount: int


layout = borsh.CStruct("liquidity_amount" / borsh.U64)


class FlashBorrowReserveLiquidityAccounts(typing.TypedDict):
    user_transfer_authority: Pubkey
    lending_market_authority: Pubkey
    lending_market: Pubkey
    reserve: Pubkey
    reserve_source_liquidity: Pubkey
    user_destination_liquidity: Pubkey
    reserve_liquidity_fee_receiver: Pubkey
    referrer_token_state: typing.Optional[Pubkey]
    referrer_account: typing.Optional[Pubkey]
    sysvar_info: Pubkey


def flash_borrow_reserve_liquidity(
    args: FlashBorrowReserveLiquidityArgs,
    accounts: FlashBorrowReserveLiquidityAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["user_transfer_authority"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["reserve_source_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_destination_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["reserve_liquidity_fee_receiver"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["referrer_token_state"], is_signer=False, is_writable=True
        )
        if accounts["referrer_token_state"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["referrer_account"], is_signer=False, is_writable=True
        )
        if accounts["referrer_account"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["sysvar_info"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x87\xe74\xa7\x074\xd4\xc1"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
