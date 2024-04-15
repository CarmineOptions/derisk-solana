from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class RefreshObligationFarmsForReserveArgs(typing.TypedDict):
    mode: int


layout = borsh.CStruct("mode" / borsh.U8)


class RefreshObligationFarmsForReserveAccounts(typing.TypedDict):
    crank: Pubkey
    obligation: Pubkey
    lending_market_authority: Pubkey
    reserve: Pubkey
    reserve_farm_state: Pubkey
    obligation_farm_user_state: Pubkey
    lending_market: Pubkey
    farms_program: Pubkey


def refresh_obligation_farms_for_reserve(
    args: RefreshObligationFarmsForReserveArgs,
    accounts: RefreshObligationFarmsForReserveAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["crank"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=accounts["obligation"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["lending_market_authority"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["reserve_farm_state"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["obligation_farm_user_state"],
            is_signer=False,
            is_writable=True,
        ),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["farms_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x8c\x90\xfd\x15\nJ\xf8\x03"
    encoded_args = layout.build(
        {
            "mode": args["mode"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
