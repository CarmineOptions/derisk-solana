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


class ReserveLiquidityJSON(typing.TypedDict):
    mint_pubkey: str
    supply_vault: str
    fee_vault: str
    available_amount: int
    borrowed_amount_sf: int
    market_price_sf: int
    market_price_last_updated_ts: int
    mint_decimals: int
    deposit_limit_crossed_slot: int
    borrow_limit_crossed_slot: int
    cumulative_borrow_rate_bsf: big_fraction_bytes.BigFractionBytesJSON
    accumulated_protocol_fees_sf: int
    accumulated_referrer_fees_sf: int
    pending_referrer_fees_sf: int
    absolute_referral_rate_sf: int
    padding2: list[int]
    padding3: list[int]


@dataclass
class ReserveLiquidity:
    layout: typing.ClassVar = borsh.CStruct(
        "mint_pubkey" / BorshPubkey,
        "supply_vault" / BorshPubkey,
        "fee_vault" / BorshPubkey,
        "available_amount" / borsh.U64,
        "borrowed_amount_sf" / borsh.U128,
        "market_price_sf" / borsh.U128,
        "market_price_last_updated_ts" / borsh.U64,
        "mint_decimals" / borsh.U64,
        "deposit_limit_crossed_slot" / borsh.U64,
        "borrow_limit_crossed_slot" / borsh.U64,
        "cumulative_borrow_rate_bsf" / big_fraction_bytes.BigFractionBytes.layout,
        "accumulated_protocol_fees_sf" / borsh.U128,
        "accumulated_referrer_fees_sf" / borsh.U128,
        "pending_referrer_fees_sf" / borsh.U128,
        "absolute_referral_rate_sf" / borsh.U128,
        "padding2" / borsh.U64[55],
        "padding3" / borsh.U128[32],
    )
    mint_pubkey: Pubkey
    supply_vault: Pubkey
    fee_vault: Pubkey
    available_amount: int
    borrowed_amount_sf: int
    market_price_sf: int
    market_price_last_updated_ts: int
    mint_decimals: int
    deposit_limit_crossed_slot: int
    borrow_limit_crossed_slot: int
    cumulative_borrow_rate_bsf: big_fraction_bytes.BigFractionBytes
    accumulated_protocol_fees_sf: int
    accumulated_referrer_fees_sf: int
    pending_referrer_fees_sf: int
    absolute_referral_rate_sf: int
    padding2: list[int]
    padding3: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ReserveLiquidity":
        return cls(
            mint_pubkey=obj.mint_pubkey,
            supply_vault=obj.supply_vault,
            fee_vault=obj.fee_vault,
            available_amount=obj.available_amount,
            borrowed_amount_sf=obj.borrowed_amount_sf,
            market_price_sf=obj.market_price_sf,
            market_price_last_updated_ts=obj.market_price_last_updated_ts,
            mint_decimals=obj.mint_decimals,
            deposit_limit_crossed_slot=obj.deposit_limit_crossed_slot,
            borrow_limit_crossed_slot=obj.borrow_limit_crossed_slot,
            cumulative_borrow_rate_bsf=big_fraction_bytes.BigFractionBytes.from_decoded(
                obj.cumulative_borrow_rate_bsf
            ),
            accumulated_protocol_fees_sf=obj.accumulated_protocol_fees_sf,
            accumulated_referrer_fees_sf=obj.accumulated_referrer_fees_sf,
            pending_referrer_fees_sf=obj.pending_referrer_fees_sf,
            absolute_referral_rate_sf=obj.absolute_referral_rate_sf,
            padding2=obj.padding2,
            padding3=obj.padding3,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "mint_pubkey": self.mint_pubkey,
            "supply_vault": self.supply_vault,
            "fee_vault": self.fee_vault,
            "available_amount": self.available_amount,
            "borrowed_amount_sf": self.borrowed_amount_sf,
            "market_price_sf": self.market_price_sf,
            "market_price_last_updated_ts": self.market_price_last_updated_ts,
            "mint_decimals": self.mint_decimals,
            "deposit_limit_crossed_slot": self.deposit_limit_crossed_slot,
            "borrow_limit_crossed_slot": self.borrow_limit_crossed_slot,
            "cumulative_borrow_rate_bsf": self.cumulative_borrow_rate_bsf.to_encodable(),
            "accumulated_protocol_fees_sf": self.accumulated_protocol_fees_sf,
            "accumulated_referrer_fees_sf": self.accumulated_referrer_fees_sf,
            "pending_referrer_fees_sf": self.pending_referrer_fees_sf,
            "absolute_referral_rate_sf": self.absolute_referral_rate_sf,
            "padding2": self.padding2,
            "padding3": self.padding3,
        }

    def to_json(self) -> ReserveLiquidityJSON:
        return {
            "mint_pubkey": str(self.mint_pubkey),
            "supply_vault": str(self.supply_vault),
            "fee_vault": str(self.fee_vault),
            "available_amount": self.available_amount,
            "borrowed_amount_sf": self.borrowed_amount_sf,
            "market_price_sf": self.market_price_sf,
            "market_price_last_updated_ts": self.market_price_last_updated_ts,
            "mint_decimals": self.mint_decimals,
            "deposit_limit_crossed_slot": self.deposit_limit_crossed_slot,
            "borrow_limit_crossed_slot": self.borrow_limit_crossed_slot,
            "cumulative_borrow_rate_bsf": self.cumulative_borrow_rate_bsf.to_json(),
            "accumulated_protocol_fees_sf": self.accumulated_protocol_fees_sf,
            "accumulated_referrer_fees_sf": self.accumulated_referrer_fees_sf,
            "pending_referrer_fees_sf": self.pending_referrer_fees_sf,
            "absolute_referral_rate_sf": self.absolute_referral_rate_sf,
            "padding2": self.padding2,
            "padding3": self.padding3,
        }

    @classmethod
    def from_json(cls, obj: ReserveLiquidityJSON) -> "ReserveLiquidity":
        return cls(
            mint_pubkey=Pubkey.from_string(obj["mint_pubkey"]),
            supply_vault=Pubkey.from_string(obj["supply_vault"]),
            fee_vault=Pubkey.from_string(obj["fee_vault"]),
            available_amount=obj["available_amount"],
            borrowed_amount_sf=obj["borrowed_amount_sf"],
            market_price_sf=obj["market_price_sf"],
            market_price_last_updated_ts=obj["market_price_last_updated_ts"],
            mint_decimals=obj["mint_decimals"],
            deposit_limit_crossed_slot=obj["deposit_limit_crossed_slot"],
            borrow_limit_crossed_slot=obj["borrow_limit_crossed_slot"],
            cumulative_borrow_rate_bsf=big_fraction_bytes.BigFractionBytes.from_json(
                obj["cumulative_borrow_rate_bsf"]
            ),
            accumulated_protocol_fees_sf=obj["accumulated_protocol_fees_sf"],
            accumulated_referrer_fees_sf=obj["accumulated_referrer_fees_sf"],
            pending_referrer_fees_sf=obj["pending_referrer_fees_sf"],
            absolute_referral_rate_sf=obj["absolute_referral_rate_sf"],
            padding2=obj["padding2"],
            padding3=obj["padding3"],
        )
