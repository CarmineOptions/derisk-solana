from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitFarmsForReserveArgs(typing.TypedDict):
    mode: int


layout = borsh.CStruct("mode" / borsh.U8)


class InitFarmsForReserveAccounts(typing.TypedDict):
    lending_market_owner: Pubkey
    lending_market: Pubkey
    lending_market_authority: Pubkey
    reserve: Pubkey
    farms_program: Pubkey
    farms_global_config: Pubkey
    farm_state: Pubkey
    farms_vault_authority: Pubkey


def init_farms_for_reserve(
    args: InitFarmsForReserveArgs,
    accounts: InitFarmsForReserveAccounts,
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
            is_writable=True,
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["farms_program"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["farms_global_config"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["farm_state"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["farms_vault_authority"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xda\x06>\xe9\x01!\xe8R"
    encoded_args = layout.build(
        {
            "mode": args["mode"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
