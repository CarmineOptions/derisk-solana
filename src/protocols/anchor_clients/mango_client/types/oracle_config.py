from __future__ import annotations
from . import (
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class OracleConfigJSON(typing.TypedDict):
    conf_filter: i80f48.I80F48JSON
    max_staleness_slots: int
    reserved: list[int]


@dataclass
class OracleConfig:
    layout: typing.ClassVar = borsh.CStruct(
        "conf_filter" / i80f48.I80F48.layout,
        "max_staleness_slots" / borsh.I64,
        "reserved" / borsh.U8[72],
    )
    conf_filter: i80f48.I80F48
    max_staleness_slots: int
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "OracleConfig":
        return cls(
            conf_filter=i80f48.I80F48.from_decoded(obj.conf_filter),
            max_staleness_slots=obj.max_staleness_slots,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "conf_filter": self.conf_filter.to_encodable(),
            "max_staleness_slots": self.max_staleness_slots,
            "reserved": self.reserved,
        }

    def to_json(self) -> OracleConfigJSON:
        return {
            "conf_filter": self.conf_filter.to_json(),
            "max_staleness_slots": self.max_staleness_slots,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: OracleConfigJSON) -> "OracleConfig":
        return cls(
            conf_filter=i80f48.I80F48.from_json(obj["conf_filter"]),
            max_staleness_slots=obj["max_staleness_slots"],
            reserved=obj["reserved"],
        )
