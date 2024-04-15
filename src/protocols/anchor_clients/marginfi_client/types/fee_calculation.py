from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class ExclusiveJSON(typing.TypedDict):
    kind: typing.Literal["Exclusive"]


class InclusiveJSON(typing.TypedDict):
    kind: typing.Literal["Inclusive"]


@dataclass
class Exclusive:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Exclusive"

    @classmethod
    def to_json(cls) -> ExclusiveJSON:
        return ExclusiveJSON(
            kind="Exclusive",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Exclusive": {},
        }


@dataclass
class Inclusive:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Inclusive"

    @classmethod
    def to_json(cls) -> InclusiveJSON:
        return InclusiveJSON(
            kind="Inclusive",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Inclusive": {},
        }


FeeCalculationKind = typing.Union[Exclusive, Inclusive]
FeeCalculationJSON = typing.Union[ExclusiveJSON, InclusiveJSON]


def from_decoded(obj: dict) -> FeeCalculationKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Exclusive" in obj:
        return Exclusive()
    if "Inclusive" in obj:
        return Inclusive()
    raise ValueError("Invalid enum object")


def from_json(obj: FeeCalculationJSON) -> FeeCalculationKind:
    if obj["kind"] == "Exclusive":
        return Exclusive()
    if obj["kind"] == "Inclusive":
        return Inclusive()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Exclusive" / borsh.CStruct(), "Inclusive" / borsh.CStruct())
