from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class OracleConfigParamsJSON(typing.TypedDict):
    conf_filter: float
    max_staleness_slots: typing.Optional[int]


@dataclass
class OracleConfigParams:
    layout: typing.ClassVar = borsh.CStruct(
        "conf_filter" / borsh.F32, "max_staleness_slots" / borsh.Option(borsh.U32)
    )
    conf_filter: float
    max_staleness_slots: typing.Optional[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "OracleConfigParams":
        return cls(
            conf_filter=obj.conf_filter, max_staleness_slots=obj.max_staleness_slots
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "conf_filter": self.conf_filter,
            "max_staleness_slots": self.max_staleness_slots,
        }

    def to_json(self) -> OracleConfigParamsJSON:
        return {
            "conf_filter": self.conf_filter,
            "max_staleness_slots": self.max_staleness_slots,
        }

    @classmethod
    def from_json(cls, obj: OracleConfigParamsJSON) -> "OracleConfigParams":
        return cls(
            conf_filter=obj["conf_filter"],
            max_staleness_slots=obj["max_staleness_slots"],
        )
