from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class UnknownJSON(typing.TypedDict):
    kind: typing.Literal["Unknown"]


class StopLossJSON(typing.TypedDict):
    kind: typing.Literal["StopLoss"]


class TakeProfitJSON(typing.TypedDict):
    kind: typing.Literal["TakeProfit"]


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
class StopLoss:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "StopLoss"

    @classmethod
    def to_json(cls) -> StopLossJSON:
        return StopLossJSON(
            kind="StopLoss",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "StopLoss": {},
        }


@dataclass
class TakeProfit:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "TakeProfit"

    @classmethod
    def to_json(cls) -> TakeProfitJSON:
        return TakeProfitJSON(
            kind="TakeProfit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TakeProfit": {},
        }


TokenConditionalSwapIntentionKind = typing.Union[Unknown, StopLoss, TakeProfit]
TokenConditionalSwapIntentionJSON = typing.Union[
    UnknownJSON, StopLossJSON, TakeProfitJSON
]


def from_decoded(obj: dict) -> TokenConditionalSwapIntentionKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Unknown" in obj:
        return Unknown()
    if "StopLoss" in obj:
        return StopLoss()
    if "TakeProfit" in obj:
        return TakeProfit()
    raise ValueError("Invalid enum object")


def from_json(
    obj: TokenConditionalSwapIntentionJSON,
) -> TokenConditionalSwapIntentionKind:
    if obj["kind"] == "Unknown":
        return Unknown()
    if obj["kind"] == "StopLoss":
        return StopLoss()
    if obj["kind"] == "TakeProfit":
        return TakeProfit()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Unknown" / borsh.CStruct(),
    "StopLoss" / borsh.CStruct(),
    "TakeProfit" / borsh.CStruct(),
)
