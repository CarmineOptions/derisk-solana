from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class TimeWeightedJSON(typing.TypedDict):
    kind: typing.Literal["TimeWeighted"]


class RealTimeJSON(typing.TypedDict):
    kind: typing.Literal["RealTime"]


@dataclass
class TimeWeighted:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "TimeWeighted"

    @classmethod
    def to_json(cls) -> TimeWeightedJSON:
        return TimeWeightedJSON(
            kind="TimeWeighted",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TimeWeighted": {},
        }


@dataclass
class RealTime:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "RealTime"

    @classmethod
    def to_json(cls) -> RealTimeJSON:
        return RealTimeJSON(
            kind="RealTime",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "RealTime": {},
        }


OraclePriceTypeKind = typing.Union[TimeWeighted, RealTime]
OraclePriceTypeJSON = typing.Union[TimeWeightedJSON, RealTimeJSON]


def from_decoded(obj: dict) -> OraclePriceTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "TimeWeighted" in obj:
        return TimeWeighted()
    if "RealTime" in obj:
        return RealTime()
    raise ValueError("Invalid enum object")


def from_json(obj: OraclePriceTypeJSON) -> OraclePriceTypeKind:
    if obj["kind"] == "TimeWeighted":
        return TimeWeighted()
    if obj["kind"] == "RealTime":
        return RealTime()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("TimeWeighted" / borsh.CStruct(), "RealTime" / borsh.CStruct())
