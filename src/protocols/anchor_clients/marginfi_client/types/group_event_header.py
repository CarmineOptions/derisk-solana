from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class GroupEventHeaderJSON(typing.TypedDict):
    signer: typing.Optional[str]
    marginfi_group: str


@dataclass
class GroupEventHeader:
    layout: typing.ClassVar = borsh.CStruct(
        "signer" / borsh.Option(BorshPubkey), "marginfi_group" / BorshPubkey
    )
    signer: typing.Optional[Pubkey]
    marginfi_group: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "GroupEventHeader":
        return cls(signer=obj.signer, marginfi_group=obj.marginfi_group)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"signer": self.signer, "marginfi_group": self.marginfi_group}

    def to_json(self) -> GroupEventHeaderJSON:
        return {
            "signer": (None if self.signer is None else str(self.signer)),
            "marginfi_group": str(self.marginfi_group),
        }

    @classmethod
    def from_json(cls, obj: GroupEventHeaderJSON) -> "GroupEventHeader":
        return cls(
            signer=(
                None if obj["signer"] is None else Pubkey.from_string(obj["signer"])
            ),
            marginfi_group=Pubkey.from_string(obj["marginfi_group"]),
        )
