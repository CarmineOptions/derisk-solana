from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class StablePriceModelJSON(typing.TypedDict):
    stable_price: float
    last_update_timestamp: int
    delay_prices: list[float]
    delay_accumulator_price: float
    delay_accumulator_time: int
    delay_interval_seconds: int
    delay_growth_limit: float
    stable_growth_limit: float
    last_delay_interval_index: int
    reset_on_nonzero_price: int
    padding: list[int]
    reserved: list[int]


@dataclass
class StablePriceModel:
    layout: typing.ClassVar = borsh.CStruct(
        "stable_price" / borsh.F64,
        "last_update_timestamp" / borsh.U64,
        "delay_prices" / borsh.F64[24],
        "delay_accumulator_price" / borsh.F64,
        "delay_accumulator_time" / borsh.U32,
        "delay_interval_seconds" / borsh.U32,
        "delay_growth_limit" / borsh.F32,
        "stable_growth_limit" / borsh.F32,
        "last_delay_interval_index" / borsh.U8,
        "reset_on_nonzero_price" / borsh.U8,
        "padding" / borsh.U8[6],
        "reserved" / borsh.U8[48],
    )
    stable_price: float
    last_update_timestamp: int
    delay_prices: list[float]
    delay_accumulator_price: float
    delay_accumulator_time: int
    delay_interval_seconds: int
    delay_growth_limit: float
    stable_growth_limit: float
    last_delay_interval_index: int
    reset_on_nonzero_price: int
    padding: list[int]
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "StablePriceModel":
        return cls(
            stable_price=obj.stable_price,
            last_update_timestamp=obj.last_update_timestamp,
            delay_prices=obj.delay_prices,
            delay_accumulator_price=obj.delay_accumulator_price,
            delay_accumulator_time=obj.delay_accumulator_time,
            delay_interval_seconds=obj.delay_interval_seconds,
            delay_growth_limit=obj.delay_growth_limit,
            stable_growth_limit=obj.stable_growth_limit,
            last_delay_interval_index=obj.last_delay_interval_index,
            reset_on_nonzero_price=obj.reset_on_nonzero_price,
            padding=obj.padding,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "stable_price": self.stable_price,
            "last_update_timestamp": self.last_update_timestamp,
            "delay_prices": self.delay_prices,
            "delay_accumulator_price": self.delay_accumulator_price,
            "delay_accumulator_time": self.delay_accumulator_time,
            "delay_interval_seconds": self.delay_interval_seconds,
            "delay_growth_limit": self.delay_growth_limit,
            "stable_growth_limit": self.stable_growth_limit,
            "last_delay_interval_index": self.last_delay_interval_index,
            "reset_on_nonzero_price": self.reset_on_nonzero_price,
            "padding": self.padding,
            "reserved": self.reserved,
        }

    def to_json(self) -> StablePriceModelJSON:
        return {
            "stable_price": self.stable_price,
            "last_update_timestamp": self.last_update_timestamp,
            "delay_prices": self.delay_prices,
            "delay_accumulator_price": self.delay_accumulator_price,
            "delay_accumulator_time": self.delay_accumulator_time,
            "delay_interval_seconds": self.delay_interval_seconds,
            "delay_growth_limit": self.delay_growth_limit,
            "stable_growth_limit": self.stable_growth_limit,
            "last_delay_interval_index": self.last_delay_interval_index,
            "reset_on_nonzero_price": self.reset_on_nonzero_price,
            "padding": self.padding,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: StablePriceModelJSON) -> "StablePriceModel":
        return cls(
            stable_price=obj["stable_price"],
            last_update_timestamp=obj["last_update_timestamp"],
            delay_prices=obj["delay_prices"],
            delay_accumulator_price=obj["delay_accumulator_price"],
            delay_accumulator_time=obj["delay_accumulator_time"],
            delay_interval_seconds=obj["delay_interval_seconds"],
            delay_growth_limit=obj["delay_growth_limit"],
            stable_growth_limit=obj["stable_growth_limit"],
            last_delay_interval_index=obj["last_delay_interval_index"],
            reset_on_nonzero_price=obj["reset_on_nonzero_price"],
            padding=obj["padding"],
            reserved=obj["reserved"],
        )
