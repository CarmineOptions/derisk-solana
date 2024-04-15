from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from solders.instruction import Instruction, AccountMeta
from ..program_id import PROGRAM_ID


class DeleteReferrerStateAndShortUrlAccounts(typing.TypedDict):
    referrer: Pubkey
    referrer_state: Pubkey
    short_url: Pubkey


def delete_referrer_state_and_short_url(
    accounts: DeleteReferrerStateAndShortUrlAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["referrer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["referrer_state"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["short_url"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\x99\xb9c\x1c\xe4\xb3\xbb\x96"
    encoded_args = b""
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
