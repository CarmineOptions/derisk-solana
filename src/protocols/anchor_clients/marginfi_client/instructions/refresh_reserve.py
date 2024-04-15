from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class RefreshReserveAccounts(typing.TypedDict):
    reserve: Pubkey
    lending_market: Pubkey
    pyth_oracle: typing.Optional[Pubkey]
    switchboard_price_oracle: typing.Optional[Pubkey]
    switchboard_twap_oracle: typing.Optional[Pubkey]
    scope_prices: typing.Optional[Pubkey]


def refresh_reserve(
    accounts: RefreshReserveAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["pyth_oracle"], is_signer=False, is_writable=False)
        if accounts["pyth_oracle"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["switchboard_price_oracle"],
            is_signer=False,
            is_writable=False,
        )
        if accounts["switchboard_price_oracle"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["switchboard_twap_oracle"],
            is_signer=False,
            is_writable=False,
        )
        if accounts["switchboard_twap_oracle"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["scope_prices"], is_signer=False, is_writable=False)
        if accounts["scope_prices"]
        else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x02\xda\x8a\xebO\xc9\x19f"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
