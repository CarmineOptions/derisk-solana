from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class FixedJSON(typing.TypedDict):
    kind: typing.Literal["Fixed"]


class OraclePeggedJSON(typing.TypedDict):
    kind: typing.Literal["OraclePegged"]


@dataclass
class Fixed:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Fixed"

    @classmethod
    def to_json(cls) -> FixedJSON:
        return FixedJSON(
            kind="Fixed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Fixed": {},
        }


@dataclass
class OraclePegged:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "OraclePegged"

    @classmethod
    def to_json(cls) -> OraclePeggedJSON:
        return OraclePeggedJSON(
            kind="OraclePegged",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OraclePegged": {},
        }


BookSideOrderTreeKind = typing.Union[Fixed, OraclePegged]
BookSideOrderTreeJSON = typing.Union[FixedJSON, OraclePeggedJSON]


def from_decoded(obj: dict) -> BookSideOrderTreeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Fixed" in obj:
        return Fixed()
    if "OraclePegged" in obj:
        return OraclePegged()
    raise ValueError("Invalid enum object")


def from_json(obj: BookSideOrderTreeJSON) -> BookSideOrderTreeKind:
    if obj["kind"] == "Fixed":
        return Fixed()
    if obj["kind"] == "OraclePegged":
        return OraclePegged()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Fixed" / borsh.CStruct(), "OraclePegged" / borsh.CStruct())
