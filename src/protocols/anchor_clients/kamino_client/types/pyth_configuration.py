from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class PythConfigurationJSON(typing.TypedDict):
    price: str


@dataclass
class PythConfiguration:
    layout: typing.ClassVar = borsh.CStruct("price" / BorshPubkey)
    price: Pubkey

    @classmethod
    def from_decoded(cls, obj: Container) -> "PythConfiguration":
        return cls(price=obj.price)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"price": self.price}

    def to_json(self) -> PythConfigurationJSON:
        return {"price": str(self.price)}

    @classmethod
    def from_json(cls, obj: PythConfigurationJSON) -> "PythConfiguration":
        return cls(price=Pubkey.from_string(obj["price"]))
