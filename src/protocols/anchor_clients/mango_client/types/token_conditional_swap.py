from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TokenConditionalSwapJSON(typing.TypedDict):
    id: int
    max_buy: int
    max_sell: int
    bought: int
    sold: int
    expiry_timestamp: int
    price_lower_limit: float
    price_upper_limit: float
    price_premium_rate: float
    taker_fee_rate: float
    maker_fee_rate: float
    buy_token_index: int
    sell_token_index: int
    is_configured: int
    allow_creating_deposits: int
    allow_creating_borrows: int
    display_price_style: int
    intention: int
    tcs_type: int
    padding: list[int]
    start_timestamp: int
    duration_seconds: int
    reserved: list[int]


@dataclass
class TokenConditionalSwap:
    layout: typing.ClassVar = borsh.CStruct(
        "id" / borsh.U64,
        "max_buy" / borsh.U64,
        "max_sell" / borsh.U64,
        "bought" / borsh.U64,
        "sold" / borsh.U64,
        "expiry_timestamp" / borsh.U64,
        "price_lower_limit" / borsh.F64,
        "price_upper_limit" / borsh.F64,
        "price_premium_rate" / borsh.F64,
        "taker_fee_rate" / borsh.F32,
        "maker_fee_rate" / borsh.F32,
        "buy_token_index" / borsh.U16,
        "sell_token_index" / borsh.U16,
        "is_configured" / borsh.U8,
        "allow_creating_deposits" / borsh.U8,
        "allow_creating_borrows" / borsh.U8,
        "display_price_style" / borsh.U8,
        "intention" / borsh.U8,
        "tcs_type" / borsh.U8,
        "padding" / borsh.U8[6],
        "start_timestamp" / borsh.U64,
        "duration_seconds" / borsh.U64,
        "reserved" / borsh.U8[88],
    )
    id: int
    max_buy: int
    max_sell: int
    bought: int
    sold: int
    expiry_timestamp: int
    price_lower_limit: float
    price_upper_limit: float
    price_premium_rate: float
    taker_fee_rate: float
    maker_fee_rate: float
    buy_token_index: int
    sell_token_index: int
    is_configured: int
    allow_creating_deposits: int
    allow_creating_borrows: int
    display_price_style: int
    intention: int
    tcs_type: int
    padding: list[int]
    start_timestamp: int
    duration_seconds: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "TokenConditionalSwap":
        return cls(
            id=obj.id,
            max_buy=obj.max_buy,
            max_sell=obj.max_sell,
            bought=obj.bought,
            sold=obj.sold,
            expiry_timestamp=obj.expiry_timestamp,
            price_lower_limit=obj.price_lower_limit,
            price_upper_limit=obj.price_upper_limit,
            price_premium_rate=obj.price_premium_rate,
            taker_fee_rate=obj.taker_fee_rate,
            maker_fee_rate=obj.maker_fee_rate,
            buy_token_index=obj.buy_token_index,
            sell_token_index=obj.sell_token_index,
            is_configured=obj.is_configured,
            allow_creating_deposits=obj.allow_creating_deposits,
            allow_creating_borrows=obj.allow_creating_borrows,
            display_price_style=obj.display_price_style,
            intention=obj.intention,
            tcs_type=obj.tcs_type,
            padding=obj.padding,
            start_timestamp=obj.start_timestamp,
            duration_seconds=obj.duration_seconds,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "id": self.id,
            "max_buy": self.max_buy,
            "max_sell": self.max_sell,
            "bought": self.bought,
            "sold": self.sold,
            "expiry_timestamp": self.expiry_timestamp,
            "price_lower_limit": self.price_lower_limit,
            "price_upper_limit": self.price_upper_limit,
            "price_premium_rate": self.price_premium_rate,
            "taker_fee_rate": self.taker_fee_rate,
            "maker_fee_rate": self.maker_fee_rate,
            "buy_token_index": self.buy_token_index,
            "sell_token_index": self.sell_token_index,
            "is_configured": self.is_configured,
            "allow_creating_deposits": self.allow_creating_deposits,
            "allow_creating_borrows": self.allow_creating_borrows,
            "display_price_style": self.display_price_style,
            "intention": self.intention,
            "tcs_type": self.tcs_type,
            "padding": self.padding,
            "start_timestamp": self.start_timestamp,
            "duration_seconds": self.duration_seconds,
            "reserved": self.reserved,
        }

    def to_json(self) -> TokenConditionalSwapJSON:
        return {
            "id": self.id,
            "max_buy": self.max_buy,
            "max_sell": self.max_sell,
            "bought": self.bought,
            "sold": self.sold,
            "expiry_timestamp": self.expiry_timestamp,
            "price_lower_limit": self.price_lower_limit,
            "price_upper_limit": self.price_upper_limit,
            "price_premium_rate": self.price_premium_rate,
            "taker_fee_rate": self.taker_fee_rate,
            "maker_fee_rate": self.maker_fee_rate,
            "buy_token_index": self.buy_token_index,
            "sell_token_index": self.sell_token_index,
            "is_configured": self.is_configured,
            "allow_creating_deposits": self.allow_creating_deposits,
            "allow_creating_borrows": self.allow_creating_borrows,
            "display_price_style": self.display_price_style,
            "intention": self.intention,
            "tcs_type": self.tcs_type,
            "padding": self.padding,
            "start_timestamp": self.start_timestamp,
            "duration_seconds": self.duration_seconds,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: TokenConditionalSwapJSON) -> "TokenConditionalSwap":
        return cls(
            id=obj["id"],
            max_buy=obj["max_buy"],
            max_sell=obj["max_sell"],
            bought=obj["bought"],
            sold=obj["sold"],
            expiry_timestamp=obj["expiry_timestamp"],
            price_lower_limit=obj["price_lower_limit"],
            price_upper_limit=obj["price_upper_limit"],
            price_premium_rate=obj["price_premium_rate"],
            taker_fee_rate=obj["taker_fee_rate"],
            maker_fee_rate=obj["maker_fee_rate"],
            buy_token_index=obj["buy_token_index"],
            sell_token_index=obj["sell_token_index"],
            is_configured=obj["is_configured"],
            allow_creating_deposits=obj["allow_creating_deposits"],
            allow_creating_borrows=obj["allow_creating_borrows"],
            display_price_style=obj["display_price_style"],
            intention=obj["intention"],
            tcs_type=obj["tcs_type"],
            padding=obj["padding"],
            start_timestamp=obj["start_timestamp"],
            duration_seconds=obj["duration_seconds"],
            reserved=obj["reserved"],
        )
