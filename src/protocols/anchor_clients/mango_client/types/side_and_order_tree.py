from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class BidFixedJSON(typing.TypedDict):
    kind: typing.Literal["BidFixed"]


class AskFixedJSON(typing.TypedDict):
    kind: typing.Literal["AskFixed"]


class BidOraclePeggedJSON(typing.TypedDict):
    kind: typing.Literal["BidOraclePegged"]


class AskOraclePeggedJSON(typing.TypedDict):
    kind: typing.Literal["AskOraclePegged"]


@dataclass
class BidFixed:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "BidFixed"

    @classmethod
    def to_json(cls) -> BidFixedJSON:
        return BidFixedJSON(
            kind="BidFixed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BidFixed": {},
        }


@dataclass
class AskFixed:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "AskFixed"

    @classmethod
    def to_json(cls) -> AskFixedJSON:
        return AskFixedJSON(
            kind="AskFixed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AskFixed": {},
        }


@dataclass
class BidOraclePegged:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "BidOraclePegged"

    @classmethod
    def to_json(cls) -> BidOraclePeggedJSON:
        return BidOraclePeggedJSON(
            kind="BidOraclePegged",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BidOraclePegged": {},
        }


@dataclass
class AskOraclePegged:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "AskOraclePegged"

    @classmethod
    def to_json(cls) -> AskOraclePeggedJSON:
        return AskOraclePeggedJSON(
            kind="AskOraclePegged",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AskOraclePegged": {},
        }


SideAndOrderTreeKind = typing.Union[
    BidFixed, AskFixed, BidOraclePegged, AskOraclePegged
]
SideAndOrderTreeJSON = typing.Union[
    BidFixedJSON, AskFixedJSON, BidOraclePeggedJSON, AskOraclePeggedJSON
]


def from_decoded(obj: dict) -> SideAndOrderTreeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "BidFixed" in obj:
        return BidFixed()
    if "AskFixed" in obj:
        return AskFixed()
    if "BidOraclePegged" in obj:
        return BidOraclePegged()
    if "AskOraclePegged" in obj:
        return AskOraclePegged()
    raise ValueError("Invalid enum object")


def from_json(obj: SideAndOrderTreeJSON) -> SideAndOrderTreeKind:
    if obj["kind"] == "BidFixed":
        return BidFixed()
    if obj["kind"] == "AskFixed":
        return AskFixed()
    if obj["kind"] == "BidOraclePegged":
        return BidOraclePegged()
    if obj["kind"] == "AskOraclePegged":
        return AskOraclePegged()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "BidFixed" / borsh.CStruct(),
    "AskFixed" / borsh.CStruct(),
    "BidOraclePegged" / borsh.CStruct(),
    "AskOraclePegged" / borsh.CStruct(),
)
