from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class BorrowObligationLiquidityArgs(typing.TypedDict):
    liquidity_amount: int


layout = borsh.CStruct("liquidity_amount" / borsh.U64)


class BorrowObligationLiquidityAccounts(typing.TypedDict):
    owner: Pubkey
    obligation: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    borrow_reserve: Pubkey
    reserve_source_liquidity: Pubkey
    borrow_reserve_liquidity_fee_receiver: Pubkey
    user_destination_liquidity: Pubkey
    referrer_token_state: typing.Optional[Pubkey]
    instruction_sysvar_account: Pubkey


def borrow_obligation_liquidity(
    args: BorrowObligationLiquidityArgs,
    accounts: BorrowObligationLiquidityAccounts,
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
            pubkey=accounts["borrow_reserve"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["reserve_source_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["borrow_reserve_liquidity_fee_receiver"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["user_destination_liquidity"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["referrer_token_state"], is_signer=False, is_writable=True
        )
        if accounts["referrer_token_state"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["instruction_sysvar_account"],
            is_signer=False,
            is_writable=False,
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"y\x7f\x12\xccI\xf5\xe1A"
    encoded_args = layout.build(
        {
            "liquidity_amount": args["liquidity_amount"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
