from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class LeafNodeJSON(typing.TypedDict):
    tag: int
    owner_slot: int
    order_type: int
    padding: list[int]
    time_in_force: int
    padding2: list[int]
    key: int
    owner: str
    quantity: int
    timestamp: int
    peg_limit: int
    client_order_id: int
    reserved: list[int]


@dataclass
class LeafNode:
    layout: typing.ClassVar = borsh.CStruct(
        "tag" / borsh.U8,
        "owner_slot" / borsh.U8,
        "order_type" / borsh.U8,
        "padding" / borsh.U8[1],
        "time_in_force" / borsh.U16,
        "padding2" / borsh.U8[2],
        "key" / borsh.U128,
        "owner" / BorshPubkey,
        "quantity" / borsh.I64,
        "timestamp" / borsh.U64,
        "peg_limit" / borsh.I64,
        "client_order_id" / borsh.U64,
        "reserved" / borsh.U8[32],
    )
    tag: int
    owner_slot: int
    order_type: int
    padding: list[int]
    time_in_force: int
    padding2: list[int]
    key: int
    owner: Pubkey
    quantity: int
    timestamp: int
    peg_limit: int
    client_order_id: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "LeafNode":
        return cls(
            tag=obj.tag,
            owner_slot=obj.owner_slot,
            order_type=obj.order_type,
            padding=obj.padding,
            time_in_force=obj.time_in_force,
            padding2=obj.padding2,
            key=obj.key,
            owner=obj.owner,
            quantity=obj.quantity,
            timestamp=obj.timestamp,
            peg_limit=obj.peg_limit,
            client_order_id=obj.client_order_id,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "tag": self.tag,
            "owner_slot": self.owner_slot,
            "order_type": self.order_type,
            "padding": self.padding,
            "time_in_force": self.time_in_force,
            "padding2": self.padding2,
            "key": self.key,
            "owner": self.owner,
            "quantity": self.quantity,
            "timestamp": self.timestamp,
            "peg_limit": self.peg_limit,
            "client_order_id": self.client_order_id,
            "reserved": self.reserved,
        }

    def to_json(self) -> LeafNodeJSON:
        return {
            "tag": self.tag,
            "owner_slot": self.owner_slot,
            "order_type": self.order_type,
            "padding": self.padding,
            "time_in_force": self.time_in_force,
            "padding2": self.padding2,
            "key": self.key,
            "owner": str(self.owner),
            "quantity": self.quantity,
            "timestamp": self.timestamp,
            "peg_limit": self.peg_limit,
            "client_order_id": self.client_order_id,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: LeafNodeJSON) -> "LeafNode":
        return cls(
            tag=obj["tag"],
            owner_slot=obj["owner_slot"],
            order_type=obj["order_type"],
            padding=obj["padding"],
            time_in_force=obj["time_in_force"],
            padding2=obj["padding2"],
            key=obj["key"],
            owner=Pubkey.from_string(obj["owner"]),
            quantity=obj["quantity"],
            timestamp=obj["timestamp"],
            peg_limit=obj["peg_limit"],
            client_order_id=obj["client_order_id"],
            reserved=obj["reserved"],
        )
