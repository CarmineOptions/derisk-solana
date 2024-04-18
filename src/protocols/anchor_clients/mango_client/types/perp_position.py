from __future__ import annotations
from . import (
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PerpPositionJSON(typing.TypedDict):
    market_index: int
    padding: list[int]
    settle_pnl_limit_window: int
    settle_pnl_limit_settled_in_current_window_native: int
    base_position_lots: int
    quote_position_native: i80f48.I80F48JSON
    quote_running_native: int
    long_settled_funding: i80f48.I80F48JSON
    short_settled_funding: i80f48.I80F48JSON
    bids_base_lots: int
    asks_base_lots: int
    taker_base_lots: int
    taker_quote_lots: int
    cumulative_long_funding: float
    cumulative_short_funding: float
    maker_volume: int
    taker_volume: int
    perp_spot_transfers: int
    avg_entry_price_per_base_lot: float
    deprecated_realized_trade_pnl_native: i80f48.I80F48JSON
    oneshot_settle_pnl_allowance: i80f48.I80F48JSON
    recurring_settle_pnl_allowance: int
    realized_pnl_for_position_native: i80f48.I80F48JSON
    reserved: list[int]


@dataclass
class PerpPosition:
    layout: typing.ClassVar = borsh.CStruct(
        "market_index" / borsh.U16,
        "padding" / borsh.U8[2],
        "settle_pnl_limit_window" / borsh.U32,
        "settle_pnl_limit_settled_in_current_window_native" / borsh.I64,
        "base_position_lots" / borsh.I64,
        "quote_position_native" / i80f48.I80F48.layout,
        "quote_running_native" / borsh.I64,
        "long_settled_funding" / i80f48.I80F48.layout,
        "short_settled_funding" / i80f48.I80F48.layout,
        "bids_base_lots" / borsh.I64,
        "asks_base_lots" / borsh.I64,
        "taker_base_lots" / borsh.I64,
        "taker_quote_lots" / borsh.I64,
        "cumulative_long_funding" / borsh.F64,
        "cumulative_short_funding" / borsh.F64,
        "maker_volume" / borsh.U64,
        "taker_volume" / borsh.U64,
        "perp_spot_transfers" / borsh.I64,
        "avg_entry_price_per_base_lot" / borsh.F64,
        "deprecated_realized_trade_pnl_native" / i80f48.I80F48.layout,
        "oneshot_settle_pnl_allowance" / i80f48.I80F48.layout,
        "recurring_settle_pnl_allowance" / borsh.I64,
        "realized_pnl_for_position_native" / i80f48.I80F48.layout,
        "reserved" / borsh.U8[88],
    )
    market_index: int
    padding: list[int]
    settle_pnl_limit_window: int
    settle_pnl_limit_settled_in_current_window_native: int
    base_position_lots: int
    quote_position_native: i80f48.I80F48
    quote_running_native: int
    long_settled_funding: i80f48.I80F48
    short_settled_funding: i80f48.I80F48
    bids_base_lots: int
    asks_base_lots: int
    taker_base_lots: int
    taker_quote_lots: int
    cumulative_long_funding: float
    cumulative_short_funding: float
    maker_volume: int
    taker_volume: int
    perp_spot_transfers: int
    avg_entry_price_per_base_lot: float
    deprecated_realized_trade_pnl_native: i80f48.I80F48
    oneshot_settle_pnl_allowance: i80f48.I80F48
    recurring_settle_pnl_allowance: int
    realized_pnl_for_position_native: i80f48.I80F48
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "PerpPosition":
        return cls(
            market_index=obj.market_index,
            padding=obj.padding,
            settle_pnl_limit_window=obj.settle_pnl_limit_window,
            settle_pnl_limit_settled_in_current_window_native=obj.settle_pnl_limit_settled_in_current_window_native,
            base_position_lots=obj.base_position_lots,
            quote_position_native=i80f48.I80F48.from_decoded(obj.quote_position_native),
            quote_running_native=obj.quote_running_native,
            long_settled_funding=i80f48.I80F48.from_decoded(obj.long_settled_funding),
            short_settled_funding=i80f48.I80F48.from_decoded(obj.short_settled_funding),
            bids_base_lots=obj.bids_base_lots,
            asks_base_lots=obj.asks_base_lots,
            taker_base_lots=obj.taker_base_lots,
            taker_quote_lots=obj.taker_quote_lots,
            cumulative_long_funding=obj.cumulative_long_funding,
            cumulative_short_funding=obj.cumulative_short_funding,
            maker_volume=obj.maker_volume,
            taker_volume=obj.taker_volume,
            perp_spot_transfers=obj.perp_spot_transfers,
            avg_entry_price_per_base_lot=obj.avg_entry_price_per_base_lot,
            deprecated_realized_trade_pnl_native=i80f48.I80F48.from_decoded(
                obj.deprecated_realized_trade_pnl_native
            ),
            oneshot_settle_pnl_allowance=i80f48.I80F48.from_decoded(
                obj.oneshot_settle_pnl_allowance
            ),
            recurring_settle_pnl_allowance=obj.recurring_settle_pnl_allowance,
            realized_pnl_for_position_native=i80f48.I80F48.from_decoded(
                obj.realized_pnl_for_position_native
            ),
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "market_index": self.market_index,
            "padding": self.padding,
            "settle_pnl_limit_window": self.settle_pnl_limit_window,
            "settle_pnl_limit_settled_in_current_window_native": self.settle_pnl_limit_settled_in_current_window_native,
            "base_position_lots": self.base_position_lots,
            "quote_position_native": self.quote_position_native.to_encodable(),
            "quote_running_native": self.quote_running_native,
            "long_settled_funding": self.long_settled_funding.to_encodable(),
            "short_settled_funding": self.short_settled_funding.to_encodable(),
            "bids_base_lots": self.bids_base_lots,
            "asks_base_lots": self.asks_base_lots,
            "taker_base_lots": self.taker_base_lots,
            "taker_quote_lots": self.taker_quote_lots,
            "cumulative_long_funding": self.cumulative_long_funding,
            "cumulative_short_funding": self.cumulative_short_funding,
            "maker_volume": self.maker_volume,
            "taker_volume": self.taker_volume,
            "perp_spot_transfers": self.perp_spot_transfers,
            "avg_entry_price_per_base_lot": self.avg_entry_price_per_base_lot,
            "deprecated_realized_trade_pnl_native": self.deprecated_realized_trade_pnl_native.to_encodable(),
            "oneshot_settle_pnl_allowance": self.oneshot_settle_pnl_allowance.to_encodable(),
            "recurring_settle_pnl_allowance": self.recurring_settle_pnl_allowance,
            "realized_pnl_for_position_native": self.realized_pnl_for_position_native.to_encodable(),
            "reserved": self.reserved,
        }

    def to_json(self) -> PerpPositionJSON:
        return {
            "market_index": self.market_index,
            "padding": self.padding,
            "settle_pnl_limit_window": self.settle_pnl_limit_window,
            "settle_pnl_limit_settled_in_current_window_native": self.settle_pnl_limit_settled_in_current_window_native,
            "base_position_lots": self.base_position_lots,
            "quote_position_native": self.quote_position_native.to_json(),
            "quote_running_native": self.quote_running_native,
            "long_settled_funding": self.long_settled_funding.to_json(),
            "short_settled_funding": self.short_settled_funding.to_json(),
            "bids_base_lots": self.bids_base_lots,
            "asks_base_lots": self.asks_base_lots,
            "taker_base_lots": self.taker_base_lots,
            "taker_quote_lots": self.taker_quote_lots,
            "cumulative_long_funding": self.cumulative_long_funding,
            "cumulative_short_funding": self.cumulative_short_funding,
            "maker_volume": self.maker_volume,
            "taker_volume": self.taker_volume,
            "perp_spot_transfers": self.perp_spot_transfers,
            "avg_entry_price_per_base_lot": self.avg_entry_price_per_base_lot,
            "deprecated_realized_trade_pnl_native": self.deprecated_realized_trade_pnl_native.to_json(),
            "oneshot_settle_pnl_allowance": self.oneshot_settle_pnl_allowance.to_json(),
            "recurring_settle_pnl_allowance": self.recurring_settle_pnl_allowance,
            "realized_pnl_for_position_native": self.realized_pnl_for_position_native.to_json(),
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: PerpPositionJSON) -> "PerpPosition":
        return cls(
            market_index=obj["market_index"],
            padding=obj["padding"],
            settle_pnl_limit_window=obj["settle_pnl_limit_window"],
            settle_pnl_limit_settled_in_current_window_native=obj[
                "settle_pnl_limit_settled_in_current_window_native"
            ],
            base_position_lots=obj["base_position_lots"],
            quote_position_native=i80f48.I80F48.from_json(obj["quote_position_native"]),
            quote_running_native=obj["quote_running_native"],
            long_settled_funding=i80f48.I80F48.from_json(obj["long_settled_funding"]),
            short_settled_funding=i80f48.I80F48.from_json(obj["short_settled_funding"]),
            bids_base_lots=obj["bids_base_lots"],
            asks_base_lots=obj["asks_base_lots"],
            taker_base_lots=obj["taker_base_lots"],
            taker_quote_lots=obj["taker_quote_lots"],
            cumulative_long_funding=obj["cumulative_long_funding"],
            cumulative_short_funding=obj["cumulative_short_funding"],
            maker_volume=obj["maker_volume"],
            taker_volume=obj["taker_volume"],
            perp_spot_transfers=obj["perp_spot_transfers"],
            avg_entry_price_per_base_lot=obj["avg_entry_price_per_base_lot"],
            deprecated_realized_trade_pnl_native=i80f48.I80F48.from_json(
                obj["deprecated_realized_trade_pnl_native"]
            ),
            oneshot_settle_pnl_allowance=i80f48.I80F48.from_json(
                obj["oneshot_settle_pnl_allowance"]
            ),
            recurring_settle_pnl_allowance=obj["recurring_settle_pnl_allowance"],
            realized_pnl_for_position_native=i80f48.I80F48.from_json(
                obj["realized_pnl_for_position_native"]
            ),
            reserved=obj["reserved"],
        )
