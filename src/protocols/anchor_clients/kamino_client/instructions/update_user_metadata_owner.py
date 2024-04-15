from __future__ import annotations
import typing
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh
from ..program_id import PROGRAM_ID


class UpdateUserMetadataOwnerArgs(typing.TypedDict):
    owner: Pubkey


layout = borsh.CStruct("owner" / BorshPubkey)


class UpdateUserMetadataOwnerAccounts(typing.TypedDict):
    user_metadata: Pubkey


def update_user_metadata_owner(
    args: UpdateUserMetadataOwnerArgs,
    accounts: UpdateUserMetadataOwnerAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["user_metadata"], is_signer=False, is_writable=True)
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"So\x15:\xe6\x83\x05\xec"
    encoded_args = layout.build(
        {
            "owner": args["owner"],
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
