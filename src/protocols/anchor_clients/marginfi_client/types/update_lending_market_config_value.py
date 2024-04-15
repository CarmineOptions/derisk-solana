from __future__ import annotations
from . import (
    elevation_group,
)
import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import EnumForCodegen, BorshPubkey
import borsh_construct as borsh

BoolJSONValue = tuple[bool]
U8JSONValue = tuple[int]
U8ArrayJSONValue = tuple[list[int]]
U16JSONValue = tuple[int]
U64JSONValue = tuple[int]
PubkeyJSONValue = tuple[str]
ElevationGroupJSONValue = tuple[elevation_group.ElevationGroupJSON]
BoolValue = tuple[bool]
U8Value = tuple[int]
U8ArrayValue = tuple[list[int]]
U16Value = tuple[int]
U64Value = tuple[int]
PubkeyValue = tuple[Pubkey]
ElevationGroupValue = tuple[elevation_group.ElevationGroup]


class BoolJSON(typing.TypedDict):
    value: BoolJSONValue
    kind: typing.Literal["Bool"]


class U8JSON(typing.TypedDict):
    value: U8JSONValue
    kind: typing.Literal["U8"]


class U8ArrayJSON(typing.TypedDict):
    value: U8ArrayJSONValue
    kind: typing.Literal["U8Array"]


class U16JSON(typing.TypedDict):
    value: U16JSONValue
    kind: typing.Literal["U16"]


class U64JSON(typing.TypedDict):
    value: U64JSONValue
    kind: typing.Literal["U64"]


class PubkeyJSON(typing.TypedDict):
    value: PubkeyJSONValue
    kind: typing.Literal["Pubkey"]


class ElevationGroupJSON(typing.TypedDict):
    value: ElevationGroupJSONValue
    kind: typing.Literal["ElevationGroup"]


@dataclass
class Bool:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Bool"
    value: BoolValue

    def to_json(self) -> BoolJSON:
        return BoolJSON(
            kind="Bool",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "Bool": {
                "item_0": self.value[0],
            },
        }


@dataclass
class U8:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "U8"
    value: U8Value

    def to_json(self) -> U8JSON:
        return U8JSON(
            kind="U8",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "U8": {
                "item_0": self.value[0],
            },
        }


@dataclass
class U8Array:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "U8Array"
    value: U8ArrayValue

    def to_json(self) -> U8ArrayJSON:
        return U8ArrayJSON(
            kind="U8Array",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "U8Array": {
                "item_0": self.value[0],
            },
        }


@dataclass
class U16:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "U16"
    value: U16Value

    def to_json(self) -> U16JSON:
        return U16JSON(
            kind="U16",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "U16": {
                "item_0": self.value[0],
            },
        }


@dataclass
class U64:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "U64"
    value: U64Value

    def to_json(self) -> U64JSON:
        return U64JSON(
            kind="U64",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "U64": {
                "item_0": self.value[0],
            },
        }


@dataclass
class Pubkey:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "Pubkey"
    value: PubkeyValue

    def to_json(self) -> PubkeyJSON:
        return PubkeyJSON(
            kind="Pubkey",
            value=(str(self.value[0]),),
        )

    def to_encodable(self) -> dict:
        return {
            "Pubkey": {
                "item_0": self.value[0],
            },
        }


@dataclass
class ElevationGroup:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "ElevationGroup"
    value: ElevationGroupValue

    def to_json(self) -> ElevationGroupJSON:
        return ElevationGroupJSON(
            kind="ElevationGroup",
            value=(self.value[0].to_json(),),
        )

    def to_encodable(self) -> dict:
        return {
            "ElevationGroup": {
                "item_0": self.value[0].to_encodable(),
            },
        }


UpdateLendingMarketConfigValueKind = typing.Union[
    Bool, U8, U8Array, U16, U64, Pubkey, ElevationGroup
]
UpdateLendingMarketConfigValueJSON = typing.Union[
    BoolJSON, U8JSON, U8ArrayJSON, U16JSON, U64JSON, PubkeyJSON, ElevationGroupJSON
]


def from_decoded(obj: dict) -> UpdateLendingMarketConfigValueKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Bool" in obj:
        val = obj["Bool"]
        return Bool((val["item_0"],))
    if "U8" in obj:
        val = obj["U8"]
        return U8((val["item_0"],))
    if "U8Array" in obj:
        val = obj["U8Array"]
        return U8Array((val["item_0"],))
    if "U16" in obj:
        val = obj["U16"]
        return U16((val["item_0"],))
    if "U64" in obj:
        val = obj["U64"]
        return U64((val["item_0"],))
    if "Pubkey" in obj:
        val = obj["Pubkey"]
        return Pubkey((val["item_0"],))
    if "ElevationGroup" in obj:
        val = obj["ElevationGroup"]
        return ElevationGroup(
            (elevation_group.ElevationGroup.from_decoded(val["item_0"]),)
        )
    raise ValueError("Invalid enum object")


def from_json(
    obj: UpdateLendingMarketConfigValueJSON,
) -> UpdateLendingMarketConfigValueKind:
    if obj["kind"] == "Bool":
        bool_json_value = typing.cast(BoolJSONValue, obj["value"])
        return Bool((bool_json_value[0],))
    if obj["kind"] == "U8":
        u8json_value = typing.cast(U8JSONValue, obj["value"])
        return U8((u8json_value[0],))
    if obj["kind"] == "U8Array":
        u8_array_json_value = typing.cast(U8ArrayJSONValue, obj["value"])
        return U8Array((u8_array_json_value[0],))
    if obj["kind"] == "U16":
        u16json_value = typing.cast(U16JSONValue, obj["value"])
        return U16((u16json_value[0],))
    if obj["kind"] == "U64":
        u64json_value = typing.cast(U64JSONValue, obj["value"])
        return U64((u64json_value[0],))
    if obj["kind"] == "Pubkey":
        pubkey_json_value = typing.cast(PubkeyJSONValue, obj["value"])
        return Pubkey((Pubkey.from_string(pubkey_json_value[0]),))
    if obj["kind"] == "ElevationGroup":
        elevation_group_json_value = typing.cast(ElevationGroupJSONValue, obj["value"])
        return ElevationGroup(
            (elevation_group.ElevationGroup.from_json(elevation_group_json_value[0]),)
        )
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Bool" / borsh.CStruct("item_0" / borsh.Bool),
    "U8" / borsh.CStruct("item_0" / borsh.U8),
    "U8Array" / borsh.CStruct("item_0" / borsh.U8[8]),
    "U16" / borsh.CStruct("item_0" / borsh.U16),
    "U64" / borsh.CStruct("item_0" / borsh.U64),
    "Pubkey" / borsh.CStruct("item_0" / BorshPubkey),
    "ElevationGroup" / borsh.CStruct("item_0" / elevation_group.ElevationGroup.layout),
)
