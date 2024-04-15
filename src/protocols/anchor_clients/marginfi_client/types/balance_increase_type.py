from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class AnyJSON(typing.TypedDict):
    kind: typing.Literal["Any"]


class RepayOnlyJSON(typing.TypedDict):
    kind: typing.Literal["RepayOnly"]


class DepositOnlyJSON(typing.TypedDict):
    kind: typing.Literal["DepositOnly"]


class BypassDepositLimitJSON(typing.TypedDict):
    kind: typing.Literal["BypassDepositLimit"]


@dataclass
class Any:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Any"

    @classmethod
    def to_json(cls) -> AnyJSON:
        return AnyJSON(
            kind="Any",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Any": {},
        }


@dataclass
class RepayOnly:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "RepayOnly"

    @classmethod
    def to_json(cls) -> RepayOnlyJSON:
        return RepayOnlyJSON(
            kind="RepayOnly",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "RepayOnly": {},
        }


@dataclass
class DepositOnly:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "DepositOnly"

    @classmethod
    def to_json(cls) -> DepositOnlyJSON:
        return DepositOnlyJSON(
            kind="DepositOnly",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "DepositOnly": {},
        }


@dataclass
class BypassDepositLimit:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "BypassDepositLimit"

    @classmethod
    def to_json(cls) -> BypassDepositLimitJSON:
        return BypassDepositLimitJSON(
            kind="BypassDepositLimit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BypassDepositLimit": {},
        }


BalanceIncreaseTypeKind = typing.Union[Any, RepayOnly, DepositOnly, BypassDepositLimit]
BalanceIncreaseTypeJSON = typing.Union[
    AnyJSON, RepayOnlyJSON, DepositOnlyJSON, BypassDepositLimitJSON
]


def from_decoded(obj: dict) -> BalanceIncreaseTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Any" in obj:
        return Any()
    if "RepayOnly" in obj:
        return RepayOnly()
    if "DepositOnly" in obj:
        return DepositOnly()
    if "BypassDepositLimit" in obj:
        return BypassDepositLimit()
    raise ValueError("Invalid enum object")


def from_json(obj: BalanceIncreaseTypeJSON) -> BalanceIncreaseTypeKind:
    if obj["kind"] == "Any":
        return Any()
    if obj["kind"] == "RepayOnly":
        return RepayOnly()
    if obj["kind"] == "DepositOnly":
        return DepositOnly()
    if obj["kind"] == "BypassDepositLimit":
        return BypassDepositLimit()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Any" / borsh.CStruct(),
    "RepayOnly" / borsh.CStruct(),
    "DepositOnly" / borsh.CStruct(),
    "BypassDepositLimit" / borsh.CStruct(),
)
