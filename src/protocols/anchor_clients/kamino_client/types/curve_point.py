from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class CurvePointJSON(typing.TypedDict):
    utilization_rate_bps: int
    borrow_rate_bps: int


@dataclass
class CurvePoint:
    layout: typing.ClassVar = borsh.CStruct(
        "utilization_rate_bps" / borsh.U32, "borrow_rate_bps" / borsh.U32
    )
    utilization_rate_bps: int
    borrow_rate_bps: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "CurvePoint":
        return cls(
            utilization_rate_bps=obj.utilization_rate_bps,
            borrow_rate_bps=obj.borrow_rate_bps,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "utilization_rate_bps": self.utilization_rate_bps,
            "borrow_rate_bps": self.borrow_rate_bps,
        }

    def to_json(self) -> CurvePointJSON:
        return {
            "utilization_rate_bps": self.utilization_rate_bps,
            "borrow_rate_bps": self.borrow_rate_bps,
        }

    @classmethod
    def from_json(cls, obj: CurvePointJSON) -> "CurvePoint":
        return cls(
            utilization_rate_bps=obj["utilization_rate_bps"],
            borrow_rate_bps=obj["borrow_rate_bps"],
        )
