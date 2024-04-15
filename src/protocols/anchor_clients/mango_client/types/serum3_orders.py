from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class Serum3OrdersJSON(typing.TypedDict):
    open_orders: str
    base_borrows_without_fee: int
    quote_borrows_without_fee: int
    market_index: int
    base_token_index: int
    quote_token_index: int
    padding: list[int]
    highest_placed_bid_inv: float
    lowest_placed_ask: float
    potential_base_tokens: int
    potential_quote_tokens: int
    lowest_placed_bid_inv: float
    highest_placed_ask: float
    reserved: list[int]


@dataclass
class Serum3Orders:
    layout: typing.ClassVar = borsh.CStruct(
        "open_orders" / BorshPubkey,
        "base_borrows_without_fee" / borsh.U64,
        "quote_borrows_without_fee" / borsh.U64,
        "market_index" / borsh.U16,
        "base_token_index" / borsh.U16,
        "quote_token_index" / borsh.U16,
        "padding" / borsh.U8[2],
        "highest_placed_bid_inv" / borsh.F64,
        "lowest_placed_ask" / borsh.F64,
        "potential_base_tokens" / borsh.U64,
        "potential_quote_tokens" / borsh.U64,
        "lowest_placed_bid_inv" / borsh.F64,
        "highest_placed_ask" / borsh.F64,
        "reserved" / borsh.U8[16],
    )
    open_orders: Pubkey
    base_borrows_without_fee: int
    quote_borrows_without_fee: int
    market_index: int
    base_token_index: int
    quote_token_index: int
    padding: list[int]
    highest_placed_bid_inv: float
    lowest_placed_ask: float
    potential_base_tokens: int
    potential_quote_tokens: int
    lowest_placed_bid_inv: float
    highest_placed_ask: float
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "Serum3Orders":
        return cls(
            open_orders=obj.open_orders,
            base_borrows_without_fee=obj.base_borrows_without_fee,
            quote_borrows_without_fee=obj.quote_borrows_without_fee,
            market_index=obj.market_index,
            base_token_index=obj.base_token_index,
            quote_token_index=obj.quote_token_index,
            padding=obj.padding,
            highest_placed_bid_inv=obj.highest_placed_bid_inv,
            lowest_placed_ask=obj.lowest_placed_ask,
            potential_base_tokens=obj.potential_base_tokens,
            potential_quote_tokens=obj.potential_quote_tokens,
            lowest_placed_bid_inv=obj.lowest_placed_bid_inv,
            highest_placed_ask=obj.highest_placed_ask,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "open_orders": self.open_orders,
            "base_borrows_without_fee": self.base_borrows_without_fee,
            "quote_borrows_without_fee": self.quote_borrows_without_fee,
            "market_index": self.market_index,
            "base_token_index": self.base_token_index,
            "quote_token_index": self.quote_token_index,
            "padding": self.padding,
            "highest_placed_bid_inv": self.highest_placed_bid_inv,
            "lowest_placed_ask": self.lowest_placed_ask,
            "potential_base_tokens": self.potential_base_tokens,
            "potential_quote_tokens": self.potential_quote_tokens,
            "lowest_placed_bid_inv": self.lowest_placed_bid_inv,
            "highest_placed_ask": self.highest_placed_ask,
            "reserved": self.reserved,
        }

    def to_json(self) -> Serum3OrdersJSON:
        return {
            "open_orders": str(self.open_orders),
            "base_borrows_without_fee": self.base_borrows_without_fee,
            "quote_borrows_without_fee": self.quote_borrows_without_fee,
            "market_index": self.market_index,
            "base_token_index": self.base_token_index,
            "quote_token_index": self.quote_token_index,
            "padding": self.padding,
            "highest_placed_bid_inv": self.highest_placed_bid_inv,
            "lowest_placed_ask": self.lowest_placed_ask,
            "potential_base_tokens": self.potential_base_tokens,
            "potential_quote_tokens": self.potential_quote_tokens,
            "lowest_placed_bid_inv": self.lowest_placed_bid_inv,
            "highest_placed_ask": self.highest_placed_ask,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: Serum3OrdersJSON) -> "Serum3Orders":
        return cls(
            open_orders=Pubkey.from_string(obj["open_orders"]),
            base_borrows_without_fee=obj["base_borrows_without_fee"],
            quote_borrows_without_fee=obj["quote_borrows_without_fee"],
            market_index=obj["market_index"],
            base_token_index=obj["base_token_index"],
            quote_token_index=obj["quote_token_index"],
            padding=obj["padding"],
            highest_placed_bid_inv=obj["highest_placed_bid_inv"],
            lowest_placed_ask=obj["lowest_placed_ask"],
            potential_base_tokens=obj["potential_base_tokens"],
            potential_quote_tokens=obj["potential_quote_tokens"],
            lowest_placed_bid_inv=obj["lowest_placed_bid_inv"],
            highest_placed_ask=obj["highest_placed_ask"],
            reserved=obj["reserved"],
        )
