from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class RefreshReserveJSON(typing.TypedDict):
    kind: typing.Literal["RefreshReserve"]


class RefreshFarmsForObligationForReserveJSON(typing.TypedDict):
    kind: typing.Literal["RefreshFarmsForObligationForReserve"]


class RefreshObligationJSON(typing.TypedDict):
    kind: typing.Literal["RefreshObligation"]


@dataclass
class RefreshReserve:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "RefreshReserve"

    @classmethod
    def to_json(cls) -> RefreshReserveJSON:
        return RefreshReserveJSON(
            kind="RefreshReserve",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "RefreshReserve": {},
        }


@dataclass
class RefreshFarmsForObligationForReserve:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "RefreshFarmsForObligationForReserve"

    @classmethod
    def to_json(cls) -> RefreshFarmsForObligationForReserveJSON:
        return RefreshFarmsForObligationForReserveJSON(
            kind="RefreshFarmsForObligationForReserve",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "RefreshFarmsForObligationForReserve": {},
        }


@dataclass
class RefreshObligation:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "RefreshObligation"

    @classmethod
    def to_json(cls) -> RefreshObligationJSON:
        return RefreshObligationJSON(
            kind="RefreshObligation",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "RefreshObligation": {},
        }


RequiredIxTypeKind = typing.Union[
    RefreshReserve, RefreshFarmsForObligationForReserve, RefreshObligation
]
RequiredIxTypeJSON = typing.Union[
    RefreshReserveJSON, RefreshFarmsForObligationForReserveJSON, RefreshObligationJSON
]


def from_decoded(obj: dict) -> RequiredIxTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "RefreshReserve" in obj:
        return RefreshReserve()
    if "RefreshFarmsForObligationForReserve" in obj:
        return RefreshFarmsForObligationForReserve()
    if "RefreshObligation" in obj:
        return RefreshObligation()
    raise ValueError("Invalid enum object")


def from_json(obj: RequiredIxTypeJSON) -> RequiredIxTypeKind:
    if obj["kind"] == "RefreshReserve":
        return RefreshReserve()
    if obj["kind"] == "RefreshFarmsForObligationForReserve":
        return RefreshFarmsForObligationForReserve()
    if obj["kind"] == "RefreshObligation":
        return RefreshObligation()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "RefreshReserve" / borsh.CStruct(),
    "RefreshFarmsForObligationForReserve" / borsh.CStruct(),
    "RefreshObligation" / borsh.CStruct(),
)
