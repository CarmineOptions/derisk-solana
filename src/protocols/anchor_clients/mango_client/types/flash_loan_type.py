from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class UnknownJSON(typing.TypedDict):
    kind: typing.Literal["Unknown"]


class SwapJSON(typing.TypedDict):
    kind: typing.Literal["Swap"]


class SwapWithoutFeeJSON(typing.TypedDict):
    kind: typing.Literal["SwapWithoutFee"]


@dataclass
class Unknown:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Unknown"

    @classmethod
    def to_json(cls) -> UnknownJSON:
        return UnknownJSON(
            kind="Unknown",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Unknown": {},
        }


@dataclass
class Swap:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Swap"

    @classmethod
    def to_json(cls) -> SwapJSON:
        return SwapJSON(
            kind="Swap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Swap": {},
        }


@dataclass
class SwapWithoutFee:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "SwapWithoutFee"

    @classmethod
    def to_json(cls) -> SwapWithoutFeeJSON:
        return SwapWithoutFeeJSON(
            kind="SwapWithoutFee",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SwapWithoutFee": {},
        }


FlashLoanTypeKind = typing.Union[Unknown, Swap, SwapWithoutFee]
FlashLoanTypeJSON = typing.Union[UnknownJSON, SwapJSON, SwapWithoutFeeJSON]


def from_decoded(obj: dict) -> FlashLoanTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Unknown" in obj:
        return Unknown()
    if "Swap" in obj:
        return Swap()
    if "SwapWithoutFee" in obj:
        return SwapWithoutFee()
    raise ValueError("Invalid enum object")


def from_json(obj: FlashLoanTypeJSON) -> FlashLoanTypeKind:
    if obj["kind"] == "Unknown":
        return Unknown()
    if obj["kind"] == "Swap":
        return Swap()
    if obj["kind"] == "SwapWithoutFee":
        return SwapWithoutFee()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Unknown" / borsh.CStruct(),
    "Swap" / borsh.CStruct(),
    "SwapWithoutFee" / borsh.CStruct(),
)
