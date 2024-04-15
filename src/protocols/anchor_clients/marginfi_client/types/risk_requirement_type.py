from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class InitialJSON(typing.TypedDict):
    kind: typing.Literal["Initial"]


class MaintenanceJSON(typing.TypedDict):
    kind: typing.Literal["Maintenance"]


class EquityJSON(typing.TypedDict):
    kind: typing.Literal["Equity"]


@dataclass
class Initial:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Initial"

    @classmethod
    def to_json(cls) -> InitialJSON:
        return InitialJSON(
            kind="Initial",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Initial": {},
        }


@dataclass
class Maintenance:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Maintenance"

    @classmethod
    def to_json(cls) -> MaintenanceJSON:
        return MaintenanceJSON(
            kind="Maintenance",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Maintenance": {},
        }


@dataclass
class Equity:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Equity"

    @classmethod
    def to_json(cls) -> EquityJSON:
        return EquityJSON(
            kind="Equity",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Equity": {},
        }


RiskRequirementTypeKind = typing.Union[Initial, Maintenance, Equity]
RiskRequirementTypeJSON = typing.Union[InitialJSON, MaintenanceJSON, EquityJSON]


def from_decoded(obj: dict) -> RiskRequirementTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Initial" in obj:
        return Initial()
    if "Maintenance" in obj:
        return Maintenance()
    if "Equity" in obj:
        return Equity()
    raise ValueError("Invalid enum object")


def from_json(obj: RiskRequirementTypeJSON) -> RiskRequirementTypeKind:
    if obj["kind"] == "Initial":
        return Initial()
    if obj["kind"] == "Maintenance":
        return Maintenance()
    if obj["kind"] == "Equity":
        return Equity()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Initial" / borsh.CStruct(),
    "Maintenance" / borsh.CStruct(),
    "Equity" / borsh.CStruct(),
)
