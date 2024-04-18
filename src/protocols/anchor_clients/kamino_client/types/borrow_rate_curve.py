from __future__ import annotations
from . import (
    curve_point,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class BorrowRateCurveJSON(typing.TypedDict):
    points: list[curve_point.CurvePointJSON]


@dataclass
class BorrowRateCurve:
    layout: typing.ClassVar = borsh.CStruct(
        "points" / curve_point.CurvePoint.layout[11]
    )
    points: list[curve_point.CurvePoint]

    @classmethod
    def from_decoded(cls, obj: Container) -> "BorrowRateCurve":
        return cls(
            points=list(
                map(lambda item: curve_point.CurvePoint.from_decoded(item), obj.points)
            )
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"points": list(map(lambda item: item.to_encodable(), self.points))}

    def to_json(self) -> BorrowRateCurveJSON:
        return {"points": list(map(lambda item: item.to_json(), self.points))}

    @classmethod
    def from_json(cls, obj: BorrowRateCurveJSON) -> "BorrowRateCurve":
        return cls(
            points=list(
                map(lambda item: curve_point.CurvePoint.from_json(item), obj["points"])
            )
        )
