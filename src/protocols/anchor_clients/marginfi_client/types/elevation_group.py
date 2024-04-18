from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class ElevationGroupJSON(typing.TypedDict):
    max_liquidation_bonus_bps: int
    id: int
    ltv_pct: int
    liquidation_threshold_pct: int
    allow_new_loans: int
    reserved: list[int]
    padding: list[int]


@dataclass
class ElevationGroup:
    layout: typing.ClassVar = borsh.CStruct(
        "max_liquidation_bonus_bps" / borsh.U16,
        "id" / borsh.U8,
        "ltv_pct" / borsh.U8,
        "liquidation_threshold_pct" / borsh.U8,
        "allow_new_loans" / borsh.U8,
        "reserved" / borsh.U8[2],
        "padding" / borsh.U64[8],
    )
    max_liquidation_bonus_bps: int
    id: int
    ltv_pct: int
    liquidation_threshold_pct: int
    allow_new_loans: int
    reserved: list[int]
    padding: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ElevationGroup":
        return cls(
            max_liquidation_bonus_bps=obj.max_liquidation_bonus_bps,
            id=obj.id,
            ltv_pct=obj.ltv_pct,
            liquidation_threshold_pct=obj.liquidation_threshold_pct,
            allow_new_loans=obj.allow_new_loans,
            reserved=obj.reserved,
            padding=obj.padding,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "max_liquidation_bonus_bps": self.max_liquidation_bonus_bps,
            "id": self.id,
            "ltv_pct": self.ltv_pct,
            "liquidation_threshold_pct": self.liquidation_threshold_pct,
            "allow_new_loans": self.allow_new_loans,
            "reserved": self.reserved,
            "padding": self.padding,
        }

    def to_json(self) -> ElevationGroupJSON:
        return {
            "max_liquidation_bonus_bps": self.max_liquidation_bonus_bps,
            "id": self.id,
            "ltv_pct": self.ltv_pct,
            "liquidation_threshold_pct": self.liquidation_threshold_pct,
            "allow_new_loans": self.allow_new_loans,
            "reserved": self.reserved,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: ElevationGroupJSON) -> "ElevationGroup":
        return cls(
            max_liquidation_bonus_bps=obj["max_liquidation_bonus_bps"],
            id=obj["id"],
            ltv_pct=obj["ltv_pct"],
            liquidation_threshold_pct=obj["liquidation_threshold_pct"],
            allow_new_loans=obj["allow_new_loans"],
            reserved=obj["reserved"],
            padding=obj["padding"],
        )
