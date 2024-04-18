from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class BigFractionBytesJSON(typing.TypedDict):
    value: list[int]
    padding: list[int]


@dataclass
class BigFractionBytes:
    layout: typing.ClassVar = borsh.CStruct(
        "value" / borsh.U64[4], "padding" / borsh.U64[2]
    )
    value: list[int]
    padding: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "BigFractionBytes":
        return cls(value=obj.value, padding=obj.padding)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"value": self.value, "padding": self.padding}

    def to_json(self) -> BigFractionBytesJSON:
        return {"value": self.value, "padding": self.padding}

    @classmethod
    def from_json(cls, obj: BigFractionBytesJSON) -> "BigFractionBytes":
        return cls(value=obj["value"], padding=obj["padding"])
