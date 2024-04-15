from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitReferrerTokenStateArgs(typing.TypedDict):
    referrer: Pubkey


layout = borsh.CStruct("referrer" / BorshPubkey)


class InitReferrerTokenStateAccounts(typing.TypedDict):
    payer: Pubkey
    lending_market: Pubkey
    reserve: Pubkey
    referrer_token_state: Pubkey


def init_referrer_token_state(
    args: InitReferrerTokenStateArgs,
    accounts: InitReferrerTokenStateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["lending_market"], is_signer=False, is_writable=False
        ),
        AccountMeta(pubkey=accounts["reserve"], is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["referrer_token_state"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"t-B\x94:\r\xdas"
    encoded_args = layout.build(
        {
            "referrer": args["referrer"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
