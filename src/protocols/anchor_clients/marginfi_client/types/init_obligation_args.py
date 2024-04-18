from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class InitObligationArgsJSON(typing.TypedDict):
    tag: int
    id: int


@dataclass
class InitObligationArgs:
    layout: typing.ClassVar = borsh.CStruct("tag" / borsh.U8, "id" / borsh.U8)
    tag: int
    id: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "InitObligationArgs":
        return cls(tag=obj.tag, id=obj.id)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"tag": self.tag, "id": self.id}

    def to_json(self) -> InitObligationArgsJSON:
        return {"tag": self.tag, "id": self.id}

    @classmethod
    def from_json(cls, obj: InitObligationArgsJSON) -> "InitObligationArgs":
        return cls(tag=obj["tag"], id=obj["id"])
