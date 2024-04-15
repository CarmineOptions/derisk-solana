from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class UpdateLendingMarketOwnerAccounts(typing.TypedDict):
    lending_market_owner_cached: Pubkey
    lending_market: Pubkey


def update_lending_market_owner(
    accounts: UpdateLendingMarketOwnerAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(
            pubkey=accounts["lending_market_owner_cached"],
            is_signer=True,
            is_writable=False,
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=True
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"v\xe0\n>\xc4\xe6\xb8Y"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
