from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class FixedPremiumJSON(typing.TypedDict):
    kind: typing.Literal["FixedPremium"]


class PremiumAuctionJSON(typing.TypedDict):
    kind: typing.Literal["PremiumAuction"]


class LinearAuctionJSON(typing.TypedDict):
    kind: typing.Literal["LinearAuction"]


@dataclass
class FixedPremium:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "FixedPremium"

    @classmethod
    def to_json(cls) -> FixedPremiumJSON:
        return FixedPremiumJSON(
            kind="FixedPremium",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "FixedPremium": {},
        }


@dataclass
class PremiumAuction:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "PremiumAuction"

    @classmethod
    def to_json(cls) -> PremiumAuctionJSON:
        return PremiumAuctionJSON(
            kind="PremiumAuction",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PremiumAuction": {},
        }


@dataclass
class LinearAuction:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "LinearAuction"

    @classmethod
    def to_json(cls) -> LinearAuctionJSON:
        return LinearAuctionJSON(
            kind="LinearAuction",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "LinearAuction": {},
        }


TokenConditionalSwapTypeKind = typing.Union[FixedPremium, PremiumAuction, LinearAuction]
TokenConditionalSwapTypeJSON = typing.Union[
    FixedPremiumJSON, PremiumAuctionJSON, LinearAuctionJSON
]


def from_decoded(obj: dict) -> TokenConditionalSwapTypeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "FixedPremium" in obj:
        return FixedPremium()
    if "PremiumAuction" in obj:
        return PremiumAuction()
    if "LinearAuction" in obj:
        return LinearAuction()
    raise ValueError("Invalid enum object")


def from_json(obj: TokenConditionalSwapTypeJSON) -> TokenConditionalSwapTypeKind:
    if obj["kind"] == "FixedPremium":
        return FixedPremium()
    if obj["kind"] == "PremiumAuction":
        return PremiumAuction()
    if obj["kind"] == "LinearAuction":
        return LinearAuction()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "FixedPremium" / borsh.CStruct(),
    "PremiumAuction" / borsh.CStruct(),
    "LinearAuction" / borsh.CStruct(),
)
