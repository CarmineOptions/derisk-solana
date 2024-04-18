from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class NotLiquidatableJSON(typing.TypedDict):
    kind: typing.Literal["NotLiquidatable"]


class LiquidatableJSON(typing.TypedDict):
    kind: typing.Literal["Liquidatable"]


class BecameNotLiquidatableJSON(typing.TypedDict):
    kind: typing.Literal["BecameNotLiquidatable"]


@dataclass
class NotLiquidatable:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "NotLiquidatable"

    @classmethod
    def to_json(cls) -> NotLiquidatableJSON:
        return NotLiquidatableJSON(
            kind="NotLiquidatable",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "NotLiquidatable": {},
        }


@dataclass
class Liquidatable:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Liquidatable"

    @classmethod
    def to_json(cls) -> LiquidatableJSON:
        return LiquidatableJSON(
            kind="Liquidatable",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Liquidatable": {},
        }


@dataclass
class BecameNotLiquidatable:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "BecameNotLiquidatable"

    @classmethod
    def to_json(cls) -> BecameNotLiquidatableJSON:
        return BecameNotLiquidatableJSON(
            kind="BecameNotLiquidatable",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BecameNotLiquidatable": {},
        }


CheckLiquidatableKind = typing.Union[
    NotLiquidatable, Liquidatable, BecameNotLiquidatable
]
CheckLiquidatableJSON = typing.Union[
    NotLiquidatableJSON, LiquidatableJSON, BecameNotLiquidatableJSON
]


def from_decoded(obj: dict) -> CheckLiquidatableKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "NotLiquidatable" in obj:
        return NotLiquidatable()
    if "Liquidatable" in obj:
        return Liquidatable()
    if "BecameNotLiquidatable" in obj:
        return BecameNotLiquidatable()
    raise ValueError("Invalid enum object")


def from_json(obj: CheckLiquidatableJSON) -> CheckLiquidatableKind:
    if obj["kind"] == "NotLiquidatable":
        return NotLiquidatable()
    if obj["kind"] == "Liquidatable":
        return Liquidatable()
    if obj["kind"] == "BecameNotLiquidatable":
        return BecameNotLiquidatable()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "NotLiquidatable" / borsh.CStruct(),
    "Liquidatable" / borsh.CStruct(),
    "BecameNotLiquidatable" / borsh.CStruct(),
)
