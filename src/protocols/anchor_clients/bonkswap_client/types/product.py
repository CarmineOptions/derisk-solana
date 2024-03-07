from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class ProductJSON(typing.TypedDict):
    v: int


@dataclass
class Product:
    layout: typing.ClassVar = borsh.CStruct("v" / borsh.U128)
    v: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "Product":
        return cls(v=obj.v)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"v": self.v}

    def to_json(self) -> ProductJSON:
        return {"v": self.v}

    @classmethod
    def from_json(cls, obj: ProductJSON) -> "Product":
        return cls(v=obj["v"])
