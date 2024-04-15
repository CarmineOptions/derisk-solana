from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class AccountEventHeaderJSON(typing.TypedDict):
    signer: typing.Optional[str]
    marginfi_account: str
    marginfi_account_authority: str
    marginfi_group: str


@dataclass
class AccountEventHeader:
    layout: typing.ClassVar = borsh.CStruct(
        "signer" / borsh.Option(BorshPubkey),
        "marginfi_account" / BorshPubkey,
        "marginfi_account_authority" / BorshPubkey,
        "marginfi_group" / BorshPubkey,
    )
    signer: typing.Optional[Pubkey]
    marginfi_account: Pubkey
    marginfi_account_authority: Pubkey
    marginfi_group: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "AccountEventHeader":
        return cls(
            signer=obj.signer,
            marginfi_account=obj.marginfi_account,
            marginfi_account_authority=obj.marginfi_account_authority,
            marginfi_group=obj.marginfi_group,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "signer": self.signer,
            "marginfi_account": self.marginfi_account,
            "marginfi_account_authority": self.marginfi_account_authority,
            "marginfi_group": self.marginfi_group,
        }

    def to_json(self) -> AccountEventHeaderJSON:
        return {
            "signer": (None if self.signer is None else str(self.signer)),
            "marginfi_account": str(self.marginfi_account),
            "marginfi_account_authority": str(self.marginfi_account_authority),
            "marginfi_group": str(self.marginfi_group),
        }

    @classmethod
    def from_json(cls, obj: AccountEventHeaderJSON) -> "AccountEventHeader":
        return cls(
            signer=(
                None if obj["signer"] is None else Pubkey.from_string(obj["signer"])
            ),
            marginfi_account=Pubkey.from_string(obj["marginfi_account"]),
            marginfi_account_authority=Pubkey.from_string(
                obj["marginfi_account_authority"]
            ),
            marginfi_group=Pubkey.from_string(obj["marginfi_group"]),
        )
