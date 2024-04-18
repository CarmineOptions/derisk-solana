from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class InitJSON(typing.TypedDict):
    kind: typing.Literal["Init"]


class MaintJSON(typing.TypedDict):
    kind: typing.Literal["Maint"]


class LiquidationEndJSON(typing.TypedDict):
    kind: typing.Literal["LiquidationEnd"]


@dataclass
class Init:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Init"

    @classmethod
    def to_json(cls) -> InitJSON:
        return InitJSON(
            kind="Init",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Init": {},
        }


@dataclass
class Maint:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Maint"

    @classmethod
    def to_json(cls) -> MaintJSON:
        return MaintJSON(
            kind="Maint",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Maint": {},
        }


@dataclass
class LiquidationEnd:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "LiquidationEnd"

    @classmethod
    def to_json(cls) -> LiquidationEndJSON:
        return LiquidationEndJSON(
            kind="LiquidationEnd",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "LiquidationEnd": {},
        }


HealthTypeKind = typing.Union[Init, Maint, LiquidationEnd]
HealthTypeJSON = typing.Union[InitJSON, MaintJSON, LiquidationEndJSON]


def from_decoded(obj: dict) -> HealthTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Init" in obj:
        return Init()
    if "Maint" in obj:
        return Maint()
    if "LiquidationEnd" in obj:
        return LiquidationEnd()
    raise ValueError("Invalid enum object")


def from_json(obj: HealthTypeJSON) -> HealthTypeKind:
    if obj["kind"] == "Init":
        return Init()
    if obj["kind"] == "Maint":
        return Maint()
    if obj["kind"] == "LiquidationEnd":
        return LiquidationEnd()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Init" / borsh.CStruct(),
    "Maint" / borsh.CStruct(),
    "LiquidationEnd" / borsh.CStruct(),
)
