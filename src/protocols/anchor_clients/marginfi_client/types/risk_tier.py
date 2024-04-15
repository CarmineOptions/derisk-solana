from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class CollateralJSON(typing.TypedDict):
    kind: typing.Literal["Collateral"]


class IsolatedJSON(typing.TypedDict):
    kind: typing.Literal["Isolated"]


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
class Isolated:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Isolated"

    @classmethod
    def to_json(cls) -> IsolatedJSON:
        return IsolatedJSON(
            kind="Isolated",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Isolated": {},
        }


RiskTierKind = typing.Union[Collateral, Isolated]
RiskTierJSON = typing.Union[CollateralJSON, IsolatedJSON]


def from_decoded(obj: dict) -> RiskTierKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Collateral" in obj:
        return Collateral()
    if "Isolated" in obj:
        return Isolated()
    raise ValueError("Invalid enum object")


def from_json(obj: RiskTierJSON) -> RiskTierKind:
    if obj["kind"] == "Collateral":
        return Collateral()
    if obj["kind"] == "Isolated":
        return Isolated()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen("Collateral" / borsh.CStruct(), "Isolated" / borsh.CStruct())
