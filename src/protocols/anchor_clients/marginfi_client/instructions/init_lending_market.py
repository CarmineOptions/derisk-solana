from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitLendingMarketArgs(typing.TypedDict):
    quote_currency: list[int]


layout = borsh.CStruct("quote_currency" / borsh.U8[32])


class InitLendingMarketAccounts(typing.TypedDict):
    lending_market_owner: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey


def init_lending_market(
    args: InitLendingMarketArgs,
    accounts: InitLendingMarketAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market_owner"], is_signer=True, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b'"\xa2t\x0ee\x89^\xef'
    encoded_args = layout.build(
        {
            "quote_currency": args["quote_currency"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
