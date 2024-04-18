from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class SolJSON(typing.TypedDict):
    kind: typing.Literal["Sol"]


class UsdhJSON(typing.TypedDict):
    kind: typing.Literal["Usdh"]


@dataclass
class Sol:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Sol"

    @classmethod
    def to_json(cls) -> SolJSON:
        return SolJSON(
            kind="Sol",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Sol": {},
        }


@dataclass
class Usdh:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Usdh"

    @classmethod
    def to_json(cls) -> UsdhJSON:
        return UsdhJSON(
            kind="Usdh",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Usdh": {},
        }


LiquidationTokenTestKind = typing.Union[Sol, Usdh]
LiquidationTokenTestJSON = typing.Union[SolJSON, UsdhJSON]


def from_decoded(obj: dict) -> LiquidationTokenTestKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Sol" in obj:
        return Sol()
    if "Usdh" in obj:
        return Usdh()
    raise ValueError("Invalid enum object")


def from_json(obj: LiquidationTokenTestJSON) -> LiquidationTokenTestKind:
    if obj["kind"] == "Sol":
        return Sol()
    if obj["kind"] == "Usdh":
        return Usdh()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Sol" / borsh.CStruct(), "Usdh" / borsh.CStruct())
