from __future__ import annotations
from . import (
    withdrawal_caps,
    reserve_fees,
    token_info,
    borrow_rate_curve,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class ReserveConfigJSON(typing.TypedDict):
    status: int
    asset_tier: int
    reserved0: list[int]
    multiplier_side_boost: list[int]
    multiplier_tag_boost: list[int]
    protocol_take_rate_pct: int
    protocol_liquidation_fee_pct: int
    loan_to_value_pct: int
    liquidation_threshold_pct: int
    min_liquidation_bonus_bps: int
    max_liquidation_bonus_bps: int
    bad_debt_liquidation_bonus_bps: int
    deleveraging_margin_call_period_secs: int
    deleveraging_threshold_slots_per_bps: int
    fees: reserve_fees.ReserveFeesJSON
    borrow_rate_curve: borrow_rate_curve.BorrowRateCurveJSON
    borrow_factor_pct: int
    deposit_limit: int
    borrow_limit: int
    token_info: token_info.TokenInfoJSON
    deposit_withdrawal_cap: withdrawal_caps.WithdrawalCapsJSON
    debt_withdrawal_cap: withdrawal_caps.WithdrawalCapsJSON
    elevation_groups: list[int]
    reserved1: list[int]


@dataclass
class ReserveConfig:
    layout: typing.ClassVar = borsh.CStruct(
        "status" / borsh.U8,
        "asset_tier" / borsh.U8,
        "reserved0" / borsh.U8[2],
        "multiplier_side_boost" / borsh.U8[2],
        "multiplier_tag_boost" / borsh.U8[8],
        "protocol_take_rate_pct" / borsh.U8,
        "protocol_liquidation_fee_pct" / borsh.U8,
        "loan_to_value_pct" / borsh.U8,
        "liquidation_threshold_pct" / borsh.U8,
        "min_liquidation_bonus_bps" / borsh.U16,
        "max_liquidation_bonus_bps" / borsh.U16,
        "bad_debt_liquidation_bonus_bps" / borsh.U16,
        "deleveraging_margin_call_period_secs" / borsh.U64,
        "deleveraging_threshold_slots_per_bps" / borsh.U64,
        "fees" / reserve_fees.ReserveFees.layout,
        "borrow_rate_curve" / borrow_rate_curve.BorrowRateCurve.layout,
        "borrow_factor_pct" / borsh.U64,
        "deposit_limit" / borsh.U64,
        "borrow_limit" / borsh.U64,
        "token_info" / token_info.TokenInfo.layout,
        "deposit_withdrawal_cap" / withdrawal_caps.WithdrawalCaps.layout,
        "debt_withdrawal_cap" / withdrawal_caps.WithdrawalCaps.layout,
        "elevation_groups" / borsh.U8[20],
        "reserved1" / borsh.U8[4],
    )
    status: int
    asset_tier: int
    reserved0: list[int]
    multiplier_side_boost: list[int]
    multiplier_tag_boost: list[int]
    protocol_take_rate_pct: int
    protocol_liquidation_fee_pct: int
    loan_to_value_pct: int
    liquidation_threshold_pct: int
    min_liquidation_bonus_bps: int
    max_liquidation_bonus_bps: int
    bad_debt_liquidation_bonus_bps: int
    deleveraging_margin_call_period_secs: int
    deleveraging_threshold_slots_per_bps: int
    fees: reserve_fees.ReserveFees
    borrow_rate_curve: borrow_rate_curve.BorrowRateCurve
    borrow_factor_pct: int
    deposit_limit: int
    borrow_limit: int
    token_info: token_info.TokenInfo
    deposit_withdrawal_cap: withdrawal_caps.WithdrawalCaps
    debt_withdrawal_cap: withdrawal_caps.WithdrawalCaps
    elevation_groups: list[int]
    reserved1: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ReserveConfig":
        return cls(
            status=obj.status,
            asset_tier=obj.asset_tier,
            reserved0=obj.reserved0,
            multiplier_side_boost=obj.multiplier_side_boost,
            multiplier_tag_boost=obj.multiplier_tag_boost,
            protocol_take_rate_pct=obj.protocol_take_rate_pct,
            protocol_liquidation_fee_pct=obj.protocol_liquidation_fee_pct,
            loan_to_value_pct=obj.loan_to_value_pct,
            liquidation_threshold_pct=obj.liquidation_threshold_pct,
            min_liquidation_bonus_bps=obj.min_liquidation_bonus_bps,
            max_liquidation_bonus_bps=obj.max_liquidation_bonus_bps,
            bad_debt_liquidation_bonus_bps=obj.bad_debt_liquidation_bonus_bps,
            deleveraging_margin_call_period_secs=obj.deleveraging_margin_call_period_secs,
            deleveraging_threshold_slots_per_bps=obj.deleveraging_threshold_slots_per_bps,
            fees=reserve_fees.ReserveFees.from_decoded(obj.fees),
            borrow_rate_curve=borrow_rate_curve.BorrowRateCurve.from_decoded(
                obj.borrow_rate_curve
            ),
            borrow_factor_pct=obj.borrow_factor_pct,
            deposit_limit=obj.deposit_limit,
            borrow_limit=obj.borrow_limit,
            token_info=token_info.TokenInfo.from_decoded(obj.token_info),
            deposit_withdrawal_cap=withdrawal_caps.WithdrawalCaps.from_decoded(
                obj.deposit_withdrawal_cap
            ),
            debt_withdrawal_cap=withdrawal_caps.WithdrawalCaps.from_decoded(
                obj.debt_withdrawal_cap
            ),
            elevation_groups=obj.elevation_groups,
            reserved1=obj.reserved1,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "status": self.status,
            "asset_tier": self.asset_tier,
            "reserved0": self.reserved0,
            "multiplier_side_boost": self.multiplier_side_boost,
            "multiplier_tag_boost": self.multiplier_tag_boost,
            "protocol_take_rate_pct": self.protocol_take_rate_pct,
            "protocol_liquidation_fee_pct": self.protocol_liquidation_fee_pct,
            "loan_to_value_pct": self.loan_to_value_pct,
            "liquidation_threshold_pct": self.liquidation_threshold_pct,
            "min_liquidation_bonus_bps": self.min_liquidation_bonus_bps,
            "max_liquidation_bonus_bps": self.max_liquidation_bonus_bps,
            "bad_debt_liquidation_bonus_bps": self.bad_debt_liquidation_bonus_bps,
            "deleveraging_margin_call_period_secs": self.deleveraging_margin_call_period_secs,
            "deleveraging_threshold_slots_per_bps": self.deleveraging_threshold_slots_per_bps,
            "fees": self.fees.to_encodable(),
            "borrow_rate_curve": self.borrow_rate_curve.to_encodable(),
            "borrow_factor_pct": self.borrow_factor_pct,
            "deposit_limit": self.deposit_limit,
            "borrow_limit": self.borrow_limit,
            "token_info": self.token_info.to_encodable(),
            "deposit_withdrawal_cap": self.deposit_withdrawal_cap.to_encodable(),
            "debt_withdrawal_cap": self.debt_withdrawal_cap.to_encodable(),
            "elevation_groups": self.elevation_groups,
            "reserved1": self.reserved1,
        }

    def to_json(self) -> ReserveConfigJSON:
        return {
            "status": self.status,
            "asset_tier": self.asset_tier,
            "reserved0": self.reserved0,
            "multiplier_side_boost": self.multiplier_side_boost,
            "multiplier_tag_boost": self.multiplier_tag_boost,
            "protocol_take_rate_pct": self.protocol_take_rate_pct,
            "protocol_liquidation_fee_pct": self.protocol_liquidation_fee_pct,
            "loan_to_value_pct": self.loan_to_value_pct,
            "liquidation_threshold_pct": self.liquidation_threshold_pct,
            "min_liquidation_bonus_bps": self.min_liquidation_bonus_bps,
            "max_liquidation_bonus_bps": self.max_liquidation_bonus_bps,
            "bad_debt_liquidation_bonus_bps": self.bad_debt_liquidation_bonus_bps,
            "deleveraging_margin_call_period_secs": self.deleveraging_margin_call_period_secs,
            "deleveraging_threshold_slots_per_bps": self.deleveraging_threshold_slots_per_bps,
            "fees": self.fees.to_json(),
            "borrow_rate_curve": self.borrow_rate_curve.to_json(),
            "borrow_factor_pct": self.borrow_factor_pct,
            "deposit_limit": self.deposit_limit,
            "borrow_limit": self.borrow_limit,
            "token_info": self.token_info.to_json(),
            "deposit_withdrawal_cap": self.deposit_withdrawal_cap.to_json(),
            "debt_withdrawal_cap": self.debt_withdrawal_cap.to_json(),
            "elevation_groups": self.elevation_groups,
            "reserved1": self.reserved1,
        }

    @classmethod
    def from_json(cls, obj: ReserveConfigJSON) -> "ReserveConfig":
        return cls(
            status=obj["status"],
            asset_tier=obj["asset_tier"],
            reserved0=obj["reserved0"],
            multiplier_side_boost=obj["multiplier_side_boost"],
            multiplier_tag_boost=obj["multiplier_tag_boost"],
            protocol_take_rate_pct=obj["protocol_take_rate_pct"],
            protocol_liquidation_fee_pct=obj["protocol_liquidation_fee_pct"],
            loan_to_value_pct=obj["loan_to_value_pct"],
            liquidation_threshold_pct=obj["liquidation_threshold_pct"],
            min_liquidation_bonus_bps=obj["min_liquidation_bonus_bps"],
            max_liquidation_bonus_bps=obj["max_liquidation_bonus_bps"],
            bad_debt_liquidation_bonus_bps=obj["bad_debt_liquidation_bonus_bps"],
            deleveraging_margin_call_period_secs=obj[
                "deleveraging_margin_call_period_secs"
            ],
            deleveraging_threshold_slots_per_bps=obj[
                "deleveraging_threshold_slots_per_bps"
            ],
            fees=reserve_fees.ReserveFees.from_json(obj["fees"]),
            borrow_rate_curve=borrow_rate_curve.BorrowRateCurve.from_json(
                obj["borrow_rate_curve"]
            ),
            borrow_factor_pct=obj["borrow_factor_pct"],
            deposit_limit=obj["deposit_limit"],
            borrow_limit=obj["borrow_limit"],
            token_info=token_info.TokenInfo.from_json(obj["token_info"]),
            deposit_withdrawal_cap=withdrawal_caps.WithdrawalCaps.from_json(
                obj["deposit_withdrawal_cap"]
            ),
            debt_withdrawal_cap=withdrawal_caps.WithdrawalCaps.from_json(
                obj["debt_withdrawal_cap"]
            ),
            elevation_groups=obj["elevation_groups"],
            reserved1=obj["reserved1"],
        )
