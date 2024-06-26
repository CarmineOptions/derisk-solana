from __future__ import annotations
from . import (
    i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class TokenPositionJSON(typing.TypedDict):
    indexed_position: i80f48.I80F48JSON
    token_index: int
    in_use_count: int
    padding: list[int]
    previous_index: i80f48.I80F48JSON
    cumulative_deposit_interest: float
    cumulative_borrow_interest: float
    reserved: list[int]


@dataclass
class TokenPosition:
    layout: typing.ClassVar = borsh.CStruct(
        "indexed_position" / i80f48.I80F48.layout,
        "token_index" / borsh.U16,
        "in_use_count" / borsh.U16,
        "padding" / borsh.U8[4],
        "previous_index" / i80f48.I80F48.layout,
        "cumulative_deposit_interest" / borsh.F64,
        "cumulative_borrow_interest" / borsh.F64,
        "reserved" / borsh.U8[128],
    )
    indexed_position: i80f48.I80F48
    token_index: int
    in_use_count: int
    padding: list[int]
    previous_index: i80f48.I80F48
    cumulative_deposit_interest: float
    cumulative_borrow_interest: float
    reserved: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "TokenPosition":
        return cls(
            indexed_position=i80f48.I80F48.from_decoded(obj.indexed_position),
            token_index=obj.token_index,
            in_use_count=obj.in_use_count,
            padding=obj.padding,
            previous_index=i80f48.I80F48.from_decoded(obj.previous_index),
            cumulative_deposit_interest=obj.cumulative_deposit_interest,
            cumulative_borrow_interest=obj.cumulative_borrow_interest,
            reserved=obj.reserved,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "indexed_position": self.indexed_position.to_encodable(),
            "token_index": self.token_index,
            "in_use_count": self.in_use_count,
            "padding": self.padding,
            "previous_index": self.previous_index.to_encodable(),
            "cumulative_deposit_interest": self.cumulative_deposit_interest,
            "cumulative_borrow_interest": self.cumulative_borrow_interest,
            "reserved": self.reserved,
        }

    def to_json(self) -> TokenPositionJSON:
        return {
            "indexed_position": self.indexed_position.to_json(),
            "token_index": self.token_index,
            "in_use_count": self.in_use_count,
            "padding": self.padding,
            "previous_index": self.previous_index.to_json(),
            "cumulative_deposit_interest": self.cumulative_deposit_interest,
            "cumulative_borrow_interest": self.cumulative_borrow_interest,
            "reserved": self.reserved,
        }

    @classmethod
    def from_json(cls, obj: TokenPositionJSON) -> "TokenPosition":
        return cls(
            indexed_position=i80f48.I80F48.from_json(obj["indexed_position"]),
            token_index=obj["token_index"],
            in_use_count=obj["in_use_count"],
            padding=obj["padding"],
            previous_index=i80f48.I80F48.from_json(obj["previous_index"]),
            cumulative_deposit_interest=obj["cumulative_deposit_interest"],
            cumulative_borrow_interest=obj["cumulative_borrow_interest"],
            reserved=obj["reserved"],
        )
