from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class InitReferrerStateAndShortUrlArgs(typing.TypedDict):
    short_url: str


layout = borsh.CStruct("short_url" / borsh.String)


class InitReferrerStateAndShortUrlAccounts(typing.TypedDict):
    referrer: Pubkey
    referrer_state: Pubkey
    referrer_short_url: Pubkey
    referrer_user_metadata: Pubkey


def init_referrer_state_and_short_url(
    args: InitReferrerStateAndShortUrlArgs,
    accounts: InitReferrerStateAndShortUrlAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["referrer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["referrer_state"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["referrer_short_url"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["referrer_user_metadata"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xa5\x13\x19\x7fd7\x1fZ"
    encoded_args = layout.build(
        {
            "short_url": args["short_url"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
