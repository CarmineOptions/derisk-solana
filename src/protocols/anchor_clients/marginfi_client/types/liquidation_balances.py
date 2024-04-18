from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class LiquidationBalancesJSON(typing.TypedDict):
    liquidatee_asset_balance: float
    liquidatee_liability_balance: float
    liquidator_asset_balance: float
    liquidator_liability_balance: float


@dataclass
class LiquidationBalances:
    layout: typing.ClassVar = borsh.CStruct(
        "liquidatee_asset_balance" / borsh.F64,
        "liquidatee_liability_balance" / borsh.F64,
        "liquidator_asset_balance" / borsh.F64,
        "liquidator_liability_balance" / borsh.F64,
    )
    liquidatee_asset_balance: float
    liquidatee_liability_balance: float
    liquidator_asset_balance: float
    liquidator_liability_balance: float

    @classmethod
    def from_decoded(cls, obj: Container) -> "LiquidationBalances":
        return cls(
            liquidatee_asset_balance=obj.liquidatee_asset_balance,
            liquidatee_liability_balance=obj.liquidatee_liability_balance,
            liquidator_asset_balance=obj.liquidator_asset_balance,
            liquidator_liability_balance=obj.liquidator_liability_balance,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "liquidatee_asset_balance": self.liquidatee_asset_balance,
            "liquidatee_liability_balance": self.liquidatee_liability_balance,
            "liquidator_asset_balance": self.liquidator_asset_balance,
            "liquidator_liability_balance": self.liquidator_liability_balance,
        }

    def to_json(self) -> LiquidationBalancesJSON:
        return {
            "liquidatee_asset_balance": self.liquidatee_asset_balance,
            "liquidatee_liability_balance": self.liquidatee_liability_balance,
            "liquidator_asset_balance": self.liquidator_asset_balance,
            "liquidator_liability_balance": self.liquidator_liability_balance,
        }

    @classmethod
    def from_json(cls, obj: LiquidationBalancesJSON) -> "LiquidationBalances":
        return cls(
            liquidatee_asset_balance=obj["liquidatee_asset_balance"],
            liquidatee_liability_balance=obj["liquidatee_liability_balance"],
            liquidator_asset_balance=obj["liquidator_asset_balance"],
            liquidator_liability_balance=obj["liquidator_liability_balance"],
        )
