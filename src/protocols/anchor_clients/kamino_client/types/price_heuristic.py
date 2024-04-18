from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class PriceHeuristicJSON(typing.TypedDict):
    lower: int
    upper: int
    exp: int


@dataclass
class PriceHeuristic:
    layout: typing.ClassVar = borsh.CStruct(
        "lower" / borsh.U64, "upper" / borsh.U64, "exp" / borsh.U64
    )
    lower: int
    upper: int
    exp: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "PriceHeuristic":
        return cls(lower=obj.lower, upper=obj.upper, exp=obj.exp)

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"lower": self.lower, "upper": self.upper, "exp": self.exp}

    def to_json(self) -> PriceHeuristicJSON:
        return {"lower": self.lower, "upper": self.upper, "exp": self.exp}

    @classmethod
    def from_json(cls, obj: PriceHeuristicJSON) -> "PriceHeuristic":
        return cls(lower=obj["lower"], upper=obj["upper"], exp=obj["exp"])
