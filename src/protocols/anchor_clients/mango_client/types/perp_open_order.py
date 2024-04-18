from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PerpOpenOrderJSON(typing.TypedDict):
    side_and_tree: int
    padding1: list[int]
    market: int
    padding2: list[int]
    client_id: int
    id: int
    quantity: int
    reserved: list[int]


@dataclass
class PerpOpenOrder:
    layout: typing.ClassVar = borsh.CStruct(
        "side_and_tree" / borsh.U8,
        "padding1" / borsh.U8[1],
        "market" / borsh.U16,
        "padding2" / borsh.U8[4],
        "client_id" / borsh.U64,
        "id" / borsh.U128,
        "quantity" / borsh.I64,
        "reserved" / borsh.U8[56],
    )
    side_and_tree: int
    padding1: list[int]
    market: int
    padding2: list[int]
    client_id: int
    id: int
    quantity: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "PerpOpenOrder":
        return cls(
            side_and_tree=obj.side_and_tree,
            padding1=obj.padding1,
            market=obj.market,
            padding2=obj.padding2,
            client_id=obj.client_id,
            id=obj.id,
            quantity=obj.quantity,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "side_and_tree": self.side_and_tree,
            "padding1": self.padding1,
            "market": self.market,
            "padding2": self.padding2,
            "client_id": self.client_id,
            "id": self.id,
            "quantity": self.quantity,
            "reserved": self.reserved,
        }

    def to_json(self) -> PerpOpenOrderJSON:
        return {
            "side_and_tree": self.side_and_tree,
            "padding1": self.padding1,
            "market": self.market,
            "padding2": self.padding2,
            "client_id": self.client_id,
            "id": self.id,
            "quantity": self.quantity,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: PerpOpenOrderJSON) -> "PerpOpenOrder":
        return cls(
            side_and_tree=obj["side_and_tree"],
            padding1=obj["padding1"],
            market=obj["market"],
            padding2=obj["padding2"],
            client_id=obj["client_id"],
            id=obj["id"],
            quantity=obj["quantity"],
            reserved=obj["reserved"],
        )
