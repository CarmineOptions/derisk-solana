from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class OutEventJSON(typing.TypedDict):
    event_type: int
    side: int
    owner_slot: int
    padding0: list[int]
    timestamp: int
    seq_num: int
    owner: str
    quantity: int
    order_id: int
    padding1: list[int]


@dataclass
class OutEvent:
    layout: typing.ClassVar = borsh.CStruct(
        "event_type" / borsh.U8,
        "side" / borsh.U8,
        "owner_slot" / borsh.U8,
        "padding0" / borsh.U8[5],
        "timestamp" / borsh.U64,
        "seq_num" / borsh.U64,
        "owner" / BorshPubkey,
        "quantity" / borsh.I64,
        "order_id" / borsh.U128,
        "padding1" / borsh.U8[128],
    )
    event_type: int
    side: int
    owner_slot: int
    padding0: list[int]
    timestamp: int
    seq_num: int
    owner: Pubkey
    quantity: int
    order_id: int
    padding1: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "OutEvent":
        return cls(
            event_type=obj.event_type,
            side=obj.side,
            owner_slot=obj.owner_slot,
            padding0=obj.padding0,
            timestamp=obj.timestamp,
            seq_num=obj.seq_num,
            owner=obj.owner,
            quantity=obj.quantity,
            order_id=obj.order_id,
            padding1=obj.padding1,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "event_type": self.event_type,
            "side": self.side,
            "owner_slot": self.owner_slot,
            "padding0": self.padding0,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "owner": self.owner,
            "quantity": self.quantity,
            "order_id": self.order_id,
            "padding1": self.padding1,
        }

    def to_json(self) -> OutEventJSON:
        return {
            "event_type": self.event_type,
            "side": self.side,
            "owner_slot": self.owner_slot,
            "padding0": self.padding0,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "owner": str(self.owner),
            "quantity": self.quantity,
            "order_id": self.order_id,
            "padding1": self.padding1,
        }

    @classmethod
    def from_json(cls, obj: OutEventJSON) -> "OutEvent":
        return cls(
            event_type=obj["event_type"],
            side=obj["side"],
            owner_slot=obj["owner_slot"],
            padding0=obj["padding0"],
            timestamp=obj["timestamp"],
            seq_num=obj["seq_num"],
            owner=Pubkey.from_string(obj["owner"]),
            quantity=obj["quantity"],
            order_id=obj["order_id"],
            padding1=obj["padding1"],
        )
