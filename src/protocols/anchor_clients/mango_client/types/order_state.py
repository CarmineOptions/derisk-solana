from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class ValidJSON(typing.TypedDict):
    kind: typing.Literal["Valid"]


class InvalidJSON(typing.TypedDict):
    kind: typing.Literal["Invalid"]


class SkippedJSON(typing.TypedDict):
    kind: typing.Literal["Skipped"]


@dataclass
class Valid:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Valid"

    @classmethod
    def to_json(cls) -> ValidJSON:
        return ValidJSON(
            kind="Valid",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Valid": {},
        }


@dataclass
class Invalid:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Invalid"

    @classmethod
    def to_json(cls) -> InvalidJSON:
        return InvalidJSON(
            kind="Invalid",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Invalid": {},
        }


@dataclass
class Skipped:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Skipped"

    @classmethod
    def to_json(cls) -> SkippedJSON:
        return SkippedJSON(
            kind="Skipped",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Skipped": {},
        }


OrderStateKind = typing.Union[Valid, Invalid, Skipped]
OrderStateJSON = typing.Union[ValidJSON, InvalidJSON, SkippedJSON]


def from_decoded(obj: dict) -> OrderStateKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Valid" in obj:
        return Valid()
    if "Invalid" in obj:
        return Invalid()
    if "Skipped" in obj:
        return Skipped()
    raise ValueError("Invalid enum object")


def from_json(obj: OrderStateJSON) -> OrderStateKind:
    if obj["kind"] == "Valid":
        return Valid()
    if obj["kind"] == "Invalid":
        return Invalid()
    if obj["kind"] == "Skipped":
        return Skipped()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Valid" / borsh.CStruct(), "Invalid" / borsh.CStruct(), "Skipped" / borsh.CStruct()
)
