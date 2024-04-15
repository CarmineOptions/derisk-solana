from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class RegularJSON(typing.TypedDict):
    kind: typing.Literal["Regular"]


class IsolatedCollateralJSON(typing.TypedDict):
    kind: typing.Literal["IsolatedCollateral"]


class IsolatedDebtJSON(typing.TypedDict):
    kind: typing.Literal["IsolatedDebt"]


@dataclass
class Regular:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "Regular"

    @classmethod
    def to_json(cls) -> RegularJSON:
        return RegularJSON(
            kind="Regular",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Regular": {},
        }


@dataclass
class IsolatedCollateral:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "IsolatedCollateral"

    @classmethod
    def to_json(cls) -> IsolatedCollateralJSON:
        return IsolatedCollateralJSON(
            kind="IsolatedCollateral",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "IsolatedCollateral": {},
        }


@dataclass
class IsolatedDebt:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "IsolatedDebt"

    @classmethod
    def to_json(cls) -> IsolatedDebtJSON:
        return IsolatedDebtJSON(
            kind="IsolatedDebt",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "IsolatedDebt": {},
        }


AssetTierKind = typing.Union[Regular, IsolatedCollateral, IsolatedDebt]
AssetTierJSON = typing.Union[RegularJSON, IsolatedCollateralJSON, IsolatedDebtJSON]


def from_decoded(obj: dict) -> AssetTierKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "Regular" in obj:
        return Regular()
    if "IsolatedCollateral" in obj:
        return IsolatedCollateral()
    if "IsolatedDebt" in obj:
        return IsolatedDebt()
    raise ValueError("Invalid enum object")


def from_json(obj: AssetTierJSON) -> AssetTierKind:
    if obj["kind"] == "Regular":
        return Regular()
    if obj["kind"] == "IsolatedCollateral":
        return IsolatedCollateral()
    if obj["kind"] == "IsolatedDebt":
        return IsolatedDebt()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "Regular" / borsh.CStruct(),
    "IsolatedCollateral" / borsh.CStruct(),
    "IsolatedDebt" / borsh.CStruct(),
)
