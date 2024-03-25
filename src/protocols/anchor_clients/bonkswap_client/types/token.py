from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TokenJSON(typing.TypedDict):
    v: int


@dataclass
class Token:
    layout: typing.ClassVar = borsh.CStruct("v" / borsh.U64)
    v: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "Token":
        return cls(v=obj.v)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"v": self.v}

    def to_json(self) -> TokenJSON:
        return {"v": self.v}

    @classmethod
    def from_json(cls, obj: TokenJSON) -> "Token":
        return cls(v=obj["v"])
