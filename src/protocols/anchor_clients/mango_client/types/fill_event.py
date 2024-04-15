from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class FillEventJSON(typing.TypedDict):
    event_type: int
    taker_side: int
    maker_out: int
    maker_slot: int
    padding: list[int]
    timestamp: int
    seq_num: int
    maker: str
    padding2: list[int]
    maker_timestamp: int
    taker: str
    padding3: list[int]
    taker_client_order_id: int
    maker_order_id: int
    price: int
    quantity: int
    maker_client_order_id: int
    maker_fee: float
    taker_fee: float
    reserved: list[int]


@dataclass
class FillEvent:
    layout: typing.ClassVar = borsh.CStruct(
        "event_type" / borsh.U8,
        "taker_side" / borsh.U8,
        "maker_out" / borsh.U8,
        "maker_slot" / borsh.U8,
        "padding" / borsh.U8[4],
        "timestamp" / borsh.U64,
        "seq_num" / borsh.U64,
        "maker" / BorshPubkey,
        "padding2" / borsh.U8[32],
        "maker_timestamp" / borsh.U64,
        "taker" / BorshPubkey,
        "padding3" / borsh.U8[16],
        "taker_client_order_id" / borsh.U64,
        "maker_order_id" / borsh.U128,
        "price" / borsh.I64,
        "quantity" / borsh.I64,
        "maker_client_order_id" / borsh.U64,
        "maker_fee" / borsh.F32,
        "taker_fee" / borsh.F32,
        "reserved" / borsh.U8[8],
    )
    event_type: int
    taker_side: int
    maker_out: int
    maker_slot: int
    padding: list[int]
    timestamp: int
    seq_num: int
    maker: Pubkey
    padding2: list[int]
    maker_timestamp: int
    taker: Pubkey
    padding3: list[int]
    taker_client_order_id: int
    maker_order_id: int
    price: int
    quantity: int
    maker_client_order_id: int
    maker_fee: float
    taker_fee: float
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "FillEvent":
        return cls(
            event_type=obj.event_type,
            taker_side=obj.taker_side,
            maker_out=obj.maker_out,
            maker_slot=obj.maker_slot,
            padding=obj.padding,
            timestamp=obj.timestamp,
            seq_num=obj.seq_num,
            maker=obj.maker,
            padding2=obj.padding2,
            maker_timestamp=obj.maker_timestamp,
            taker=obj.taker,
            padding3=obj.padding3,
            taker_client_order_id=obj.taker_client_order_id,
            maker_order_id=obj.maker_order_id,
            price=obj.price,
            quantity=obj.quantity,
            maker_client_order_id=obj.maker_client_order_id,
            maker_fee=obj.maker_fee,
            taker_fee=obj.taker_fee,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "event_type": self.event_type,
            "taker_side": self.taker_side,
            "maker_out": self.maker_out,
            "maker_slot": self.maker_slot,
            "padding": self.padding,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "maker": self.maker,
            "padding2": self.padding2,
            "maker_timestamp": self.maker_timestamp,
            "taker": self.taker,
            "padding3": self.padding3,
            "taker_client_order_id": self.taker_client_order_id,
            "maker_order_id": self.maker_order_id,
            "price": self.price,
            "quantity": self.quantity,
            "maker_client_order_id": self.maker_client_order_id,
            "maker_fee": self.maker_fee,
            "taker_fee": self.taker_fee,
            "reserved": self.reserved,
        }

    def to_json(self) -> FillEventJSON:
        return {
            "event_type": self.event_type,
            "taker_side": self.taker_side,
            "maker_out": self.maker_out,
            "maker_slot": self.maker_slot,
            "padding": self.padding,
            "timestamp": self.timestamp,
            "seq_num": self.seq_num,
            "maker": str(self.maker),
            "padding2": self.padding2,
            "maker_timestamp": self.maker_timestamp,
            "taker": str(self.taker),
            "padding3": self.padding3,
            "taker_client_order_id": self.taker_client_order_id,
            "maker_order_id": self.maker_order_id,
            "price": self.price,
            "quantity": self.quantity,
            "maker_client_order_id": self.maker_client_order_id,
            "maker_fee": self.maker_fee,
            "taker_fee": self.taker_fee,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: FillEventJSON) -> "FillEvent":
        return cls(
            event_type=obj["event_type"],
            taker_side=obj["taker_side"],
            maker_out=obj["maker_out"],
            maker_slot=obj["maker_slot"],
            padding=obj["padding"],
            timestamp=obj["timestamp"],
            seq_num=obj["seq_num"],
            maker=Pubkey.from_string(obj["maker"]),
            padding2=obj["padding2"],
            maker_timestamp=obj["maker_timestamp"],
            taker=Pubkey.from_string(obj["taker"]),
            padding3=obj["padding3"],
            taker_client_order_id=obj["taker_client_order_id"],
            maker_order_id=obj["maker_order_id"],
            price=obj["price"],
            quantity=obj["quantity"],
            maker_client_order_id=obj["maker_client_order_id"],
            maker_fee=obj["maker_fee"],
            taker_fee=obj["taker_fee"],
            reserved=obj["reserved"],
        )
