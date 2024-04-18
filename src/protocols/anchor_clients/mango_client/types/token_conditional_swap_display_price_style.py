from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class SellTokenPerBuyTokenJSON(typing.TypedDict):
    kind: typing.Literal["SellTokenPerBuyToken"]


class BuyTokenPerSellTokenJSON(typing.TypedDict):
    kind: typing.Literal["BuyTokenPerSellToken"]


@dataclass
class SellTokenPerBuyToken:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "SellTokenPerBuyToken"

    @classmethod
    def to_json(cls) -> SellTokenPerBuyTokenJSON:
        return SellTokenPerBuyTokenJSON(
            kind="SellTokenPerBuyToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "SellTokenPerBuyToken": {},
        }


@dataclass
class BuyTokenPerSellToken:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "BuyTokenPerSellToken"

    @classmethod
    def to_json(cls) -> BuyTokenPerSellTokenJSON:
        return BuyTokenPerSellTokenJSON(
            kind="BuyTokenPerSellToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "BuyTokenPerSellToken": {},
        }


TokenConditionalSwapDisplayPriceStyleKind = typing.Union[
    SellTokenPerBuyToken, BuyTokenPerSellToken
]
TokenConditionalSwapDisplayPriceStyleJSON = typing.Union[
    SellTokenPerBuyTokenJSON, BuyTokenPerSellTokenJSON
]


def from_decoded(obj: dict) -> TokenConditionalSwapDisplayPriceStyleKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "SellTokenPerBuyToken" in obj:
        return SellTokenPerBuyToken()
    if "BuyTokenPerSellToken" in obj:
        return BuyTokenPerSellToken()
    raise ValueError("Invalid enum object")


def from_json(
    obj: TokenConditionalSwapDisplayPriceStyleJSON,
) -> TokenConditionalSwapDisplayPriceStyleKind:
    if obj["kind"] == "SellTokenPerBuyToken":
        return SellTokenPerBuyToken()
    if obj["kind"] == "BuyTokenPerSellToken":
        return BuyTokenPerSellToken()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "SellTokenPerBuyToken" / borsh.CStruct(), "BuyTokenPerSellToken" / borsh.CStruct()
)
