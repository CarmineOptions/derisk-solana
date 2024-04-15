from __future__ import annotations
from . import (
    big_fraction_bytes,
)
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class ObligationLiquidityJSON(typing.TypedDict):
    borrow_reserve: str
    cumulative_borrow_rate_bsf: big_fraction_bytes.BigFractionBytesJSON
    padding: int
    borrowed_amount_sf: int
    market_value_sf: int
    borrow_factor_adjusted_market_value_sf: int
    padding2: list[int]


@dataclass
class ObligationLiquidity:
    layout: typing.ClassVar = borsh.CStruct(
        "borrow_reserve" / BorshPubkey,
        "cumulative_borrow_rate_bsf" / big_fraction_bytes.BigFractionBytes.layout,
        "padding" / borsh.U64,
        "borrowed_amount_sf" / borsh.U128,
        "market_value_sf" / borsh.U128,
        "borrow_factor_adjusted_market_value_sf" / borsh.U128,
        "padding2" / borsh.U64[8],
    )
    borrow_reserve: Pubkey
    cumulative_borrow_rate_bsf: big_fraction_bytes.BigFractionBytes
    padding: int
    borrowed_amount_sf: int
    market_value_sf: int
    borrow_factor_adjusted_market_value_sf: int
    padding2: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ObligationLiquidity":
        return cls(
            borrow_reserve=obj.borrow_reserve,
            cumulative_borrow_rate_bsf=big_fraction_bytes.BigFractionBytes.from_decoded(
                obj.cumulative_borrow_rate_bsf
            ),
            padding=obj.padding,
            borrowed_amount_sf=obj.borrowed_amount_sf,
            market_value_sf=obj.market_value_sf,
            borrow_factor_adjusted_market_value_sf=obj.borrow_factor_adjusted_market_value_sf,
            padding2=obj.padding2,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "borrow_reserve": self.borrow_reserve,
            "cumulative_borrow_rate_bsf": self.cumulative_borrow_rate_bsf.to_encodable(),
            "padding": self.padding,
            "borrowed_amount_sf": self.borrowed_amount_sf,
            "market_value_sf": self.market_value_sf,
            "borrow_factor_adjusted_market_value_sf": self.borrow_factor_adjusted_market_value_sf,
            "padding2": self.padding2,
        }

    def to_json(self) -> ObligationLiquidityJSON:
        return {
            "borrow_reserve": str(self.borrow_reserve),
            "cumulative_borrow_rate_bsf": self.cumulative_borrow_rate_bsf.to_json(),
            "padding": self.padding,
            "borrowed_amount_sf": self.borrowed_amount_sf,
            "market_value_sf": self.market_value_sf,
            "borrow_factor_adjusted_market_value_sf": self.borrow_factor_adjusted_market_value_sf,
            "padding2": self.padding2,
        }

    @classmethod
    def from_json(cls, obj: ObligationLiquidityJSON) -> "ObligationLiquidity":
        return cls(
            borrow_reserve=Pubkey.from_string(obj["borrow_reserve"]),
            cumulative_borrow_rate_bsf=big_fraction_bytes.BigFractionBytes.from_json(
                obj["cumulative_borrow_rate_bsf"]
            ),
            padding=obj["padding"],
            borrowed_amount_sf=obj["borrowed_amount_sf"],
            market_value_sf=obj["market_value_sf"],
            borrow_factor_adjusted_market_value_sf=obj[
                "borrow_factor_adjusted_market_value_sf"
            ],
            padding2=obj["padding2"],
        )
