from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class CollateralJSON(typing.TypedDict):
    kind: typing.Literal["Collateral"]


class DebtJSON(typing.TypedDict):
    kind: typing.Literal["Debt"]


@dataclass
class Collateral:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Collateral"

    @classmethod
    def to_json(cls) -> CollateralJSON:
        return CollateralJSON(
            kind="Collateral",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Collateral": {},
        }


@dataclass
class Debt:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Debt"

    @classmethod
    def to_json(cls) -> DebtJSON:
        return DebtJSON(
            kind="Debt",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Debt": {},
        }


ReserveFarmKindKind = typing.Union[Collateral, Debt]
ReserveFarmKindJSON = typing.Union[CollateralJSON, DebtJSON]


def from_decoded(obj: dict) -> ReserveFarmKindKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Collateral" in obj:
        return Collateral()
    if "Debt" in obj:
        return Debt()
    raise ValueError("Invalid enum object")


def from_json(obj: ReserveFarmKindJSON) -> ReserveFarmKindKind:
    if obj["kind"] == "Collateral":
        return Collateral()
    if obj["kind"] == "Debt":
        return Debt()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Collateral" / borsh.CStruct(), "Debt" / borsh.CStruct())
