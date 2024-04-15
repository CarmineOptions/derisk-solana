from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class FlashLoanTokenDetailV2JSON(typing.TypedDict):
    token_index: int
    change_amount: int
    loan: int
    loan_origination_fee: int
    deposit_index: int
    borrow_index: int
    price: int
    deposit_fee: int
    approved_amount: int


@dataclass
class FlashLoanTokenDetailV2:
    layout: typing.ClassVar = borsh.CStruct(
        "token_index" / borsh.U16,
        "change_amount" / borsh.I128,
        "loan" / borsh.I128,
        "loan_origination_fee" / borsh.I128,
        "deposit_index" / borsh.I128,
        "borrow_index" / borsh.I128,
        "price" / borsh.I128,
        "deposit_fee" / borsh.I128,
        "approved_amount" / borsh.U64,
    )
    token_index: int
    change_amount: int
    loan: int
    loan_origination_fee: int
    deposit_index: int
    borrow_index: int
    price: int
    deposit_fee: int
    approved_amount: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "FlashLoanTokenDetailV2":
        return cls(
            token_index=obj.token_index,
            change_amount=obj.change_amount,
            loan=obj.loan,
            loan_origination_fee=obj.loan_origination_fee,
            deposit_index=obj.deposit_index,
            borrow_index=obj.borrow_index,
            price=obj.price,
            deposit_fee=obj.deposit_fee,
            approved_amount=obj.approved_amount,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "token_index": self.token_index,
            "change_amount": self.change_amount,
            "loan": self.loan,
            "loan_origination_fee": self.loan_origination_fee,
            "deposit_index": self.deposit_index,
            "borrow_index": self.borrow_index,
            "price": self.price,
            "deposit_fee": self.deposit_fee,
            "approved_amount": self.approved_amount,
        }

    def to_json(self) -> FlashLoanTokenDetailV2JSON:
        return {
            "token_index": self.token_index,
            "change_amount": self.change_amount,
            "loan": self.loan,
            "loan_origination_fee": self.loan_origination_fee,
            "deposit_index": self.deposit_index,
            "borrow_index": self.borrow_index,
            "price": self.price,
            "deposit_fee": self.deposit_fee,
            "approved_amount": self.approved_amount,
        }

    @classmethod
    def from_json(cls, obj: FlashLoanTokenDetailV2JSON) -> "FlashLoanTokenDetailV2":
        return cls(
            token_index=obj["token_index"],
            change_amount=obj["change_amount"],
            loan=obj["loan"],
            loan_origination_fee=obj["loan_origination_fee"],
            deposit_index=obj["deposit_index"],
            borrow_index=obj["borrow_index"],
            price=obj["price"],
            deposit_fee=obj["deposit_fee"],
            approved_amount=obj["approved_amount"],
        )
