from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class LowJSON(typing.TypedDict):
    kind: typing.Literal["Low"]


class HighJSON(typing.TypedDict):
    kind: typing.Literal["High"]


@dataclass
class Low:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Low"

    @classmethod
    def to_json(cls) -> LowJSON:
        return LowJSON(
            kind="Low",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Low": {},
        }


@dataclass
class High:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "High"

    @classmethod
    def to_json(cls) -> HighJSON:
        return HighJSON(
            kind="High",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "High": {},
        }


PriceBiasKind = typing.Union[Low, High]
PriceBiasJSON = typing.Union[LowJSON, HighJSON]


def from_decoded(obj: dict) -> PriceBiasKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Low" in obj:
        return Low()
    if "High" in obj:
        return High()
    raise ValueError("Invalid enum object")


def from_json(obj: PriceBiasJSON) -> PriceBiasKind:
    if obj["kind"] == "Low":
        return Low()
    if obj["kind"] == "High":
        return High()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Low" / borsh.CStruct(), "High" / borsh.CStruct())
