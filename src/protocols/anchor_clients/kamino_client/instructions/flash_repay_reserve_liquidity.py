from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class FlashRepayReserveLiquidityArgs(typing.TypedDict):
    liquidity_amount: int
    borrow_instruction_index: int


layout = borsh.CStruct(
    "liquidity_amount" / borsh.U64, "borrow_instruction_index" / borsh.U8
)


class FlashRepayReserveLiquidityAccounts(typing.TypedDict):
    user_transfer_authority: Pubkey
    lending_market_authority: Pubkey
    lending_market: Pubkey
    reserve: Pubkey
    reserve_destination_liquidity: Pubkey
    user_source_liquidity: Pubkey
    reserve_liquidity_fee_receiver: Pubkey
    referrer_token_state: typing.Optional[Pubkey]
    referrer_account: typing.Optional[Pubkey]
    sysvar_info: Pubkey


def flash_repay_reserve_liquidity(
    args: FlashRepayReserveLiquidityArgs,
    accounts: FlashRepayReserveLiquidityAccounts,
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
            pubkey=accounts["reserve_destination_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_source_liquidity"], is_signer=False, is_writable=True
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
    identifier = b"\xb9u\x00\xcb`\xf5\xb4\xba"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
            "borrow_instruction_index": args["borrow_instruction_index"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
