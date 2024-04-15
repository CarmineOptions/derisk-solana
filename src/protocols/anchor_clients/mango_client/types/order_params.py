from __future__ import annotations
from . import (
    post_order_type,
)
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class ImmediateOrCancelJSONValue(typing.TypedDict):
    price_lots: int


class FixedJSONValue(typing.TypedDict):
    price_lots: int
    order_type: post_order_type.PostOrderTypeJSON


class OraclePeggedJSONValue(typing.TypedDict):
    price_offset_lots: int
    order_type: post_order_type.PostOrderTypeJSON
    peg_limit: int
    max_oracle_staleness_slots: int


class ImmediateOrCancelValue(typing.TypedDict):
    price_lots: int


class FixedValue(typing.TypedDict):
    price_lots: int
    order_type: post_order_type.PostOrderTypeKind


class OraclePeggedValue(typing.TypedDict):
    price_offset_lots: int
    order_type: post_order_type.PostOrderTypeKind
    peg_limit: int
    max_oracle_staleness_slots: int


class MarketJSON(typing.TypedDict):
    kind: typing.Literal["Market"]


class ImmediateOrCancelJSON(typing.TypedDict):
    value: ImmediateOrCancelJSONValue
    kind: typing.Literal["ImmediateOrCancel"]


class FixedJSON(typing.TypedDict):
    value: FixedJSONValue
    kind: typing.Literal["Fixed"]


class OraclePeggedJSON(typing.TypedDict):
    value: OraclePeggedJSONValue
    kind: typing.Literal["OraclePegged"]


@dataclass
class Market:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Market"

    @classmethod
    def to_json(cls) -> MarketJSON:
        return MarketJSON(
            kind="Market",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Market": {},
        }


@dataclass
class ImmediateOrCancel:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "ImmediateOrCancel"
    value: ImmediateOrCancelValue

    def to_json(self) -> ImmediateOrCancelJSON:
        return ImmediateOrCancelJSON(
            kind="ImmediateOrCancel",
            value={
                "price_lots": self.value["price_lots"],
            },
        )

    def to_encodable(self) -> dict:
        return {
            "ImmediateOrCancel": {
                "price_lots": self.value["price_lots"],
            },
        }


@dataclass
class Fixed:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Fixed"
    value: FixedValue

    def to_json(self) -> FixedJSON:
        return FixedJSON(
            kind="Fixed",
            value={
                "price_lots": self.value["price_lots"],
                "order_type": self.value["order_type"].to_json(),
            },
        )

    def to_encodable(self) -> dict:
        return {
            "Fixed": {
                "price_lots": self.value["price_lots"],
                "order_type": self.value["order_type"].to_encodable(),
            },
        }


@dataclass
class OraclePegged:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "OraclePegged"
    value: OraclePeggedValue

    def to_json(self) -> OraclePeggedJSON:
        return OraclePeggedJSON(
            kind="OraclePegged",
            value={
                "price_offset_lots": self.value["price_offset_lots"],
                "order_type": self.value["order_type"].to_json(),
                "peg_limit": self.value["peg_limit"],
                "max_oracle_staleness_slots": self.value["max_oracle_staleness_slots"],
            },
        )

    def to_encodable(self) -> dict:
        return {
            "OraclePegged": {
                "price_offset_lots": self.value["price_offset_lots"],
                "order_type": self.value["order_type"].to_encodable(),
                "peg_limit": self.value["peg_limit"],
                "max_oracle_staleness_slots": self.value["max_oracle_staleness_slots"],
            },
        }


OrderParamsKind = typing.Union[Market, ImmediateOrCancel, Fixed, OraclePegged]
OrderParamsJSON = typing.Union[
    MarketJSON, ImmediateOrCancelJSON, FixedJSON, OraclePeggedJSON
]


def from_decoded(obj: dict) -> OrderParamsKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Market" in obj:
        return Market()
    if "ImmediateOrCancel" in obj:
        val = obj["ImmediateOrCancel"]
        return ImmediateOrCancel(
            ImmediateOrCancelValue(
                price_lots=val["price_lots"],
            )
        )
    if "Fixed" in obj:
        val = obj["Fixed"]
        return Fixed(
            FixedValue(
                price_lots=val["price_lots"],
                order_type=post_order_type.from_decoded(val["order_type"]),
            )
        )
    if "OraclePegged" in obj:
        val = obj["OraclePegged"]
        return OraclePegged(
            OraclePeggedValue(
                price_offset_lots=val["price_offset_lots"],
                order_type=post_order_type.from_decoded(val["order_type"]),
                peg_limit=val["peg_limit"],
                max_oracle_staleness_slots=val["max_oracle_staleness_slots"],
            )
        )
    raise ValueError("Invalid enum object")


def from_json(obj: OrderParamsJSON) -> OrderParamsKind:
    if obj["kind"] == "Market":
        return Market()
    if obj["kind"] == "ImmediateOrCancel":
        immediate_or_cancel_json_value = typing.cast(
            ImmediateOrCancelJSONValue, obj["value"]
        )
        return ImmediateOrCancel(
            ImmediateOrCancelValue(
                price_lots=immediate_or_cancel_json_value["price_lots"],
            )
        )
    if obj["kind"] == "Fixed":
        fixed_json_value = typing.cast(FixedJSONValue, obj["value"])
        return Fixed(
            FixedValue(
                price_lots=fixed_json_value["price_lots"],
                order_type=post_order_type.from_json(fixed_json_value["order_type"]),
            )
        )
    if obj["kind"] == "OraclePegged":
        oracle_pegged_json_value = typing.cast(OraclePeggedJSONValue, obj["value"])
        return OraclePegged(
            OraclePeggedValue(
                price_offset_lots=oracle_pegged_json_value["price_offset_lots"],
                order_type=post_order_type.from_json(
                    oracle_pegged_json_value["order_type"]
                ),
                peg_limit=oracle_pegged_json_value["peg_limit"],
                max_oracle_staleness_slots=oracle_pegged_json_value[
                    "max_oracle_staleness_slots"
                ],
            )
        )
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Market" / borsh.CStruct(),
    "ImmediateOrCancel" / borsh.CStruct("price_lots" / borsh.I64),
    "Fixed"
    / borsh.CStruct("price_lots" / borsh.I64, "order_type" / post_order_type.layout),
    "OraclePegged"
    / borsh.CStruct(
        "price_offset_lots" / borsh.I64,
        "order_type" / post_order_type.layout,
        "peg_limit" / borsh.I64,
        "max_oracle_staleness_slots" / borsh.I32,
    ),
)
