from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class SingleJSON(typing.TypedDict):
    kind: typing.Literal["Single"]


class DualJSON(typing.TypedDict):
    kind: typing.Literal["Dual"]


class TripleJSON(typing.TypedDict):
    kind: typing.Literal["Triple"]


@dataclass
class Single:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Single"

    @classmethod
    def to_json(cls) -> SingleJSON:
        return SingleJSON(
            kind="Single",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Single": {},
        }


@dataclass
class Dual:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Dual"

    @classmethod
    def to_json(cls) -> DualJSON:
        return DualJSON(
            kind="Dual",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Dual": {},
        }


@dataclass
class Triple:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Triple"

    @classmethod
    def to_json(cls) -> TripleJSON:
        return TripleJSON(
            kind="Triple",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Triple": {},
        }


FarmTypeKind = typing.Union[Single, Dual, Triple]
FarmTypeJSON = typing.Union[SingleJSON, DualJSON, TripleJSON]


def from_decoded(obj: dict) -> FarmTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Single" in obj:
        return Single()
    if "Dual" in obj:
        return Dual()
    if "Triple" in obj:
        return Triple()
    raise ValueError("Invalid enum object")


def from_json(obj: FarmTypeJSON) -> FarmTypeKind:
    if obj["kind"] == "Single":
        return Single()
    if obj["kind"] == "Dual":
        return Dual()
    if obj["kind"] == "Triple":
        return Triple()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Single" / borsh.CStruct(), "Dual" / borsh.CStruct(), "Triple" / borsh.CStruct()
)
