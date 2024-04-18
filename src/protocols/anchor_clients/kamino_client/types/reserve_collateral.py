from __future__ import annotations
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class ReserveCollateralJSON(typing.TypedDict):
    mint_pubkey: str
    mint_total_supply: int
    supply_vault: str
    padding1: list[int]
    padding2: list[int]


@dataclass
class ReserveCollateral:
    layout: typing.ClassVar = borsh.CStruct(
        "mint_pubkey" / BorshPubkey,
        "mint_total_supply" / borsh.U64,
        "supply_vault" / BorshPubkey,
        "padding1" / borsh.U128[32],
        "padding2" / borsh.U128[32],
    )
    mint_pubkey: Pubkey
    mint_total_supply: int
    supply_vault: Pubkey
    padding1: list[int]
    padding2: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "ReserveCollateral":
        return cls(
            mint_pubkey=obj.mint_pubkey,
            mint_total_supply=obj.mint_total_supply,
            supply_vault=obj.supply_vault,
            padding1=obj.padding1,
            padding2=obj.padding2,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "mint_pubkey": self.mint_pubkey,
            "mint_total_supply": self.mint_total_supply,
            "supply_vault": self.supply_vault,
            "padding1": self.padding1,
            "padding2": self.padding2,
        }

    def to_json(self) -> ReserveCollateralJSON:
        return {
            "mint_pubkey": str(self.mint_pubkey),
            "mint_total_supply": self.mint_total_supply,
            "supply_vault": str(self.supply_vault),
            "padding1": self.padding1,
            "padding2": self.padding2,
        }

    @classmethod
    def from_json(cls, obj: ReserveCollateralJSON) -> "ReserveCollateral":
        return cls(
            mint_pubkey=Pubkey.from_string(obj["mint_pubkey"]),
            mint_total_supply=obj["mint_total_supply"],
            supply_vault=Pubkey.from_string(obj["supply_vault"]),
            padding1=obj["padding1"],
            padding2=obj["padding2"],
        )
