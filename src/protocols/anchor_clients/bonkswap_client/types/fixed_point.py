from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class FixedPointJSON(typing.TypedDict):
    v: int


@dataclass
class FixedPoint:
    layout: typing.ClassVar = borsh.CStruct("v" / borsh.U128)
    v: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "FixedPoint":
        return cls(v=obj.v)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"v": self.v}

    def to_json(self) -> FixedPointJSON:
        return {"v": self.v}

    @classmethod
    def from_json(cls, obj: FixedPointJSON) -> "FixedPoint":
        return cls(v=obj["v"])
