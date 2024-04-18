from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class KeepAccumulatorJSON(typing.TypedDict):
    kind: typing.Literal["KeepAccumulator"]


class ResetAccumulatorJSON(typing.TypedDict):
    kind: typing.Literal["ResetAccumulator"]


@dataclass
class KeepAccumulator:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "KeepAccumulator"

    @classmethod
    def to_json(cls) -> KeepAccumulatorJSON:
        return KeepAccumulatorJSON(
            kind="KeepAccumulator",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "KeepAccumulator": {},
        }


@dataclass
class ResetAccumulator:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "ResetAccumulator"

    @classmethod
    def to_json(cls) -> ResetAccumulatorJSON:
        return ResetAccumulatorJSON(
            kind="ResetAccumulator",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "ResetAccumulator": {},
        }


WithdrawalCapAccumulatorActionKind = typing.Union[KeepAccumulator, ResetAccumulator]
WithdrawalCapAccumulatorActionJSON = typing.Union[
    KeepAccumulatorJSON, ResetAccumulatorJSON
]


def from_decoded(obj: dict) -> WithdrawalCapAccumulatorActionKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "KeepAccumulator" in obj:
        return KeepAccumulator()
    if "ResetAccumulator" in obj:
        return ResetAccumulator()
    raise ValueError("Invalid enum object")


def from_json(
    obj: WithdrawalCapAccumulatorActionJSON,
) -> WithdrawalCapAccumulatorActionKind:
    if obj["kind"] == "KeepAccumulator":
        return KeepAccumulator()
    if obj["kind"] == "ResetAccumulator":
        return ResetAccumulator()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "KeepAccumulator" / borsh.CStruct(), "ResetAccumulator" / borsh.CStruct()
)
