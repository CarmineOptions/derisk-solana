from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class WithdrawalCapsJSON(typing.TypedDict):
    config_capacity: int
    current_total: int
    last_interval_start_timestamp: int
    config_interval_length_seconds: int


@dataclass
class WithdrawalCaps:
    layout: typing.ClassVar = borsh.CStruct(
        "config_capacity" / borsh.I64,
        "current_total" / borsh.I64,
        "last_interval_start_timestamp" / borsh.U64,
        "config_interval_length_seconds" / borsh.U64,
    )
    config_capacity: int
    current_total: int
    last_interval_start_timestamp: int
    config_interval_length_seconds: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "WithdrawalCaps":
        return cls(
            config_capacity=obj.config_capacity,
            current_total=obj.current_total,
            last_interval_start_timestamp=obj.last_interval_start_timestamp,
            config_interval_length_seconds=obj.config_interval_length_seconds,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "config_capacity": self.config_capacity,
            "current_total": self.current_total,
            "last_interval_start_timestamp": self.last_interval_start_timestamp,
            "config_interval_length_seconds": self.config_interval_length_seconds,
        }

    def to_json(self) -> WithdrawalCapsJSON:
        return {
            "config_capacity": self.config_capacity,
            "current_total": self.current_total,
            "last_interval_start_timestamp": self.last_interval_start_timestamp,
            "config_interval_length_seconds": self.config_interval_length_seconds,
        }

    @classmethod
    def from_json(cls, obj: WithdrawalCapsJSON) -> "WithdrawalCaps":
        return cls(
            config_capacity=obj["config_capacity"],
            current_total=obj["current_total"],
            last_interval_start_timestamp=obj["last_interval_start_timestamp"],
            config_interval_length_seconds=obj["config_interval_length_seconds"],
        )
