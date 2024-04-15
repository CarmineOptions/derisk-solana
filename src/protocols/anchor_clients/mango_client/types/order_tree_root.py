from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class OrderTreeRootJSON(typing.TypedDict):
    maybe_node: int
    leaf_count: int


@dataclass
class OrderTreeRoot:
    layout: typing.ClassVar = borsh.CStruct(
        "maybe_node" / borsh.U32, "leaf_count" / borsh.U32
    )
    maybe_node: int
    leaf_count: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "OrderTreeRoot":
        return cls(maybe_node=obj.maybe_node, leaf_count=obj.leaf_count)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"maybe_node": self.maybe_node, "leaf_count": self.leaf_count}

    def to_json(self) -> OrderTreeRootJSON:
        return {"maybe_node": self.maybe_node, "leaf_count": self.leaf_count}

    @classmethod
    def from_json(cls, obj: OrderTreeRootJSON) -> "OrderTreeRoot":
        return cls(maybe_node=obj["maybe_node"], leaf_count=obj["leaf_count"])
