from __future__ import annotations
from . import (
    reserve_config,
    borrow_rate_curve,
)
import typing
from dataclasses import dataclass
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import EnumForCodegen, BorshPubkey
import borsh_construct as borsh

BoolJSONValue = tuple[bool]
U8JSONValue = tuple[int]
U8TupleJSONValue = tuple[int, int]
U16JSONValue = tuple[int]
U64JSONValue = tuple[int]
PubkeyJSONValue = tuple[str]
ScopeChainJSONValue = tuple[list[int]]
NameJSONValue = tuple[list[int]]
BorrowRateCurveJSONValue = tuple[borrow_rate_curve.BorrowRateCurveJSON]
FullJSONValue = tuple[reserve_config.ReserveConfigJSON]
WithdrawalCapJSONValue = tuple[int, int]
ElevationGroupsJSONValue = tuple[list[int]]
BoolValue = tuple[bool]
U8Value = tuple[int]
U8TupleValue = tuple[int, int]
U16Value = tuple[int]
U64Value = tuple[int]
PubkeyValue = tuple[Pubkey]
ScopeChainValue = tuple[list[int]]
NameValue = tuple[list[int]]
BorrowRateCurveValue = tuple[borrow_rate_curve.BorrowRateCurve]
FullValue = tuple[reserve_config.ReserveConfig]
WithdrawalCapValue = tuple[int, int]
ElevationGroupsValue = tuple[list[int]]


class BoolJSON(typing.TypedDict):
    value: BoolJSONValue
    kind: typing.Literal["Bool"]


class U8JSON(typing.TypedDict):
    value: U8JSONValue
    kind: typing.Literal["U8"]


class U8TupleJSON(typing.TypedDict):
    value: U8TupleJSONValue
    kind: typing.Literal["U8Tuple"]


class U16JSON(typing.TypedDict):
    value: U16JSONValue
    kind: typing.Literal["U16"]


class U64JSON(typing.TypedDict):
    value: U64JSONValue
    kind: typing.Literal["U64"]


class PubkeyJSON(typing.TypedDict):
    value: PubkeyJSONValue
    kind: typing.Literal["Pubkey"]


class ScopeChainJSON(typing.TypedDict):
    value: ScopeChainJSONValue
    kind: typing.Literal["ScopeChain"]


class NameJSON(typing.TypedDict):
    value: NameJSONValue
    kind: typing.Literal["Name"]


class BorrowRateCurveJSON(typing.TypedDict):
    value: BorrowRateCurveJSONValue
    kind: typing.Literal["BorrowRateCurve"]


class FullJSON(typing.TypedDict):
    value: FullJSONValue
    kind: typing.Literal["Full"]


class WithdrawalCapJSON(typing.TypedDict):
    value: WithdrawalCapJSONValue
    kind: typing.Literal["WithdrawalCap"]


class ElevationGroupsJSON(typing.TypedDict):
    value: ElevationGroupsJSONValue
    kind: typing.Literal["ElevationGroups"]


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
class U8Tuple:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "U8Tuple"
    value: U8TupleValue

    def to_json(self) -> U8TupleJSON:
        return U8TupleJSON(
            kind="U8Tuple",
            value=(
                self.value[0],
                self.value[1],
            ),
        )

    def to_encodable(self) -> dict:
        return {
            "U8Tuple": {
                "item_0": self.value[0],
                "item_1": self.value[1],
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
class ScopeChain:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "ScopeChain"
    value: ScopeChainValue

    def to_json(self) -> ScopeChainJSON:
        return ScopeChainJSON(
            kind="ScopeChain",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "ScopeChain": {
                "item_0": self.value[0],
            },
        }


@dataclass
class Name:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "Name"
    value: NameValue

    def to_json(self) -> NameJSON:
        return NameJSON(
            kind="Name",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "Name": {
                "item_0": self.value[0],
            },
        }


@dataclass
class BorrowRateCurve:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "BorrowRateCurve"
    value: BorrowRateCurveValue

    def to_json(self) -> BorrowRateCurveJSON:
        return BorrowRateCurveJSON(
            kind="BorrowRateCurve",
            value=(self.value[0].to_json(),),
        )

    def to_encodable(self) -> dict:
        return {
            "BorrowRateCurve": {
                "item_0": self.value[0].to_encodable(),
            },
        }


@dataclass
class Full:
    discriminator: typing.ClassVar = 9
    kind: typing.ClassVar = "Full"
    value: FullValue

    def to_json(self) -> FullJSON:
        return FullJSON(
            kind="Full",
            value=(self.value[0].to_json(),),
        )

    def to_encodable(self) -> dict:
        return {
            "Full": {
                "item_0": self.value[0].to_encodable(),
            },
        }


@dataclass
class WithdrawalCap:
    discriminator: typing.ClassVar = 10
    kind: typing.ClassVar = "WithdrawalCap"
    value: WithdrawalCapValue

    def to_json(self) -> WithdrawalCapJSON:
        return WithdrawalCapJSON(
            kind="WithdrawalCap",
            value=(
                self.value[0],
                self.value[1],
            ),
        )

    def to_encodable(self) -> dict:
        return {
            "WithdrawalCap": {
                "item_0": self.value[0],
                "item_1": self.value[1],
            },
        }


@dataclass
class ElevationGroups:
    discriminator: typing.ClassVar = 11
    kind: typing.ClassVar = "ElevationGroups"
    value: ElevationGroupsValue

    def to_json(self) -> ElevationGroupsJSON:
        return ElevationGroupsJSON(
            kind="ElevationGroups",
            value=(self.value[0],),
        )

    def to_encodable(self) -> dict:
        return {
            "ElevationGroups": {
                "item_0": self.value[0],
            },
        }


UpdateReserveConfigValueKind = typing.Union[
    Bool,
    U8,
    U8Tuple,
    U16,
    U64,
    Pubkey,
    ScopeChain,
    Name,
    BorrowRateCurve,
    Full,
    WithdrawalCap,
    ElevationGroups,
]
UpdateReserveConfigValueJSON = typing.Union[
    BoolJSON,
    U8JSON,
    U8TupleJSON,
    U16JSON,
    U64JSON,
    PubkeyJSON,
    ScopeChainJSON,
    NameJSON,
    BorrowRateCurveJSON,
    FullJSON,
    WithdrawalCapJSON,
    ElevationGroupsJSON,
]


def from_decoded(obj: dict) -> UpdateReserveConfigValueKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Bool" in obj:
        val = obj["Bool"]
        return Bool((val["item_0"],))
    if "U8" in obj:
        val = obj["U8"]
        return U8((val["item_0"],))
    if "U8Tuple" in obj:
        val = obj["U8Tuple"]
        return U8Tuple(
            (
                val["item_0"],
                val["item_1"],
            )
        )
    if "U16" in obj:
        val = obj["U16"]
        return U16((val["item_0"],))
    if "U64" in obj:
        val = obj["U64"]
        return U64((val["item_0"],))
    if "Pubkey" in obj:
        val = obj["Pubkey"]
        return Pubkey((val["item_0"],))
    if "ScopeChain" in obj:
        val = obj["ScopeChain"]
        return ScopeChain((val["item_0"],))
    if "Name" in obj:
        val = obj["Name"]
        return Name((val["item_0"],))
    if "BorrowRateCurve" in obj:
        val = obj["BorrowRateCurve"]
        return BorrowRateCurve(
            (borrow_rate_curve.BorrowRateCurve.from_decoded(val["item_0"]),)
        )
    if "Full" in obj:
        val = obj["Full"]
        return Full((reserve_config.ReserveConfig.from_decoded(val["item_0"]),))
    if "WithdrawalCap" in obj:
        val = obj["WithdrawalCap"]
        return WithdrawalCap(
            (
                val["item_0"],
                val["item_1"],
            )
        )
    if "ElevationGroups" in obj:
        val = obj["ElevationGroups"]
        return ElevationGroups((val["item_0"],))
    raise ValueError("Invalid enum object")


def from_json(obj: UpdateReserveConfigValueJSON) -> UpdateReserveConfigValueKind:
    if obj["kind"] == "Bool":
        bool_json_value = typing.cast(BoolJSONValue, obj["value"])
        return Bool((bool_json_value[0],))
    if obj["kind"] == "U8":
        u8json_value = typing.cast(U8JSONValue, obj["value"])
        return U8((u8json_value[0],))
    if obj["kind"] == "U8Tuple":
        u8_tuple_json_value = typing.cast(U8TupleJSONValue, obj["value"])
        return U8Tuple(
            (
                u8_tuple_json_value[0],
                u8_tuple_json_value[1],
            )
        )
    if obj["kind"] == "U16":
        u16json_value = typing.cast(U16JSONValue, obj["value"])
        return U16((u16json_value[0],))
    if obj["kind"] == "U64":
        u64json_value = typing.cast(U64JSONValue, obj["value"])
        return U64((u64json_value[0],))
    if obj["kind"] == "Pubkey":
        pubkey_json_value = typing.cast(PubkeyJSONValue, obj["value"])
        return Pubkey((Pubkey.from_string(pubkey_json_value[0]),))
    if obj["kind"] == "ScopeChain":
        scope_chain_json_value = typing.cast(ScopeChainJSONValue, obj["value"])
        return ScopeChain((scope_chain_json_value[0],))
    if obj["kind"] == "Name":
        name_json_value = typing.cast(NameJSONValue, obj["value"])
        return Name((name_json_value[0],))
    if obj["kind"] == "BorrowRateCurve":
        borrow_rate_curve_json_value = typing.cast(
            BorrowRateCurveJSONValue, obj["value"]
        )
        return BorrowRateCurve(
            (
                borrow_rate_curve.BorrowRateCurve.from_json(
                    borrow_rate_curve_json_value[0]
                ),
            )
        )
    if obj["kind"] == "Full":
        full_json_value = typing.cast(FullJSONValue, obj["value"])
        return Full((reserve_config.ReserveConfig.from_json(full_json_value[0]),))
    if obj["kind"] == "WithdrawalCap":
        withdrawal_cap_json_value = typing.cast(WithdrawalCapJSONValue, obj["value"])
        return WithdrawalCap(
            (
                withdrawal_cap_json_value[0],
                withdrawal_cap_json_value[1],
            )
        )
    if obj["kind"] == "ElevationGroups":
        elevation_groups_json_value = typing.cast(
            ElevationGroupsJSONValue, obj["value"]
        )
        return ElevationGroups((elevation_groups_json_value[0],))
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Bool" / borsh.CStruct("item_0" / borsh.Bool),
    "U8" / borsh.CStruct("item_0" / borsh.U8),
    "U8Tuple" / borsh.CStruct("item_0" / borsh.U8, "item_1" / borsh.U8),
    "U16" / borsh.CStruct("item_0" / borsh.U16),
    "U64" / borsh.CStruct("item_0" / borsh.U64),
    "Pubkey" / borsh.CStruct("item_0" / BorshPubkey),
    "ScopeChain" / borsh.CStruct("item_0" / borsh.U16[4]),
    "Name" / borsh.CStruct("item_0" / borsh.U8[32]),
    "BorrowRateCurve"
    / borsh.CStruct("item_0" / borrow_rate_curve.BorrowRateCurve.layout),
    "Full" / borsh.CStruct("item_0" / reserve_config.ReserveConfig.layout),
    "WithdrawalCap" / borsh.CStruct("item_0" / borsh.U64, "item_1" / borsh.U64),
    "ElevationGroups" / borsh.CStruct("item_0" / borsh.U8[20]),
)
