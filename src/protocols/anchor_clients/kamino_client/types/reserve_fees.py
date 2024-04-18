from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class ReserveFeesJSON(typing.TypedDict):
    borrow_fee_sf: int
    flash_loan_fee_sf: int
    padding: list[int]


@dataclass
class ReserveFees:
    layout: typing.ClassVar = borsh.CStruct(
        "borrow_fee_sf" / borsh.U64,
        "flash_loan_fee_sf" / borsh.U64,
        "padding" / borsh.U8[8],
    )
    borrow_fee_sf: int
    flash_loan_fee_sf: int
    padding: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ReserveFees":
        return cls(
            borrow_fee_sf=obj.borrow_fee_sf,
            flash_loan_fee_sf=obj.flash_loan_fee_sf,
            padding=obj.padding,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "borrow_fee_sf": self.borrow_fee_sf,
            "flash_loan_fee_sf": self.flash_loan_fee_sf,
            "padding": self.padding,
        }

    def to_json(self) -> ReserveFeesJSON:
        return {
            "borrow_fee_sf": self.borrow_fee_sf,
            "flash_loan_fee_sf": self.flash_loan_fee_sf,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: ReserveFeesJSON) -> "ReserveFees":
        return cls(
            borrow_fee_sf=obj["borrow_fee_sf"],
            flash_loan_fee_sf=obj["flash_loan_fee_sf"],
            padding=obj["padding"],
        )
