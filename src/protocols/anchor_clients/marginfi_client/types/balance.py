from __future__ import annotations
from . import (
    wrapped_i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class BalanceJSON(typing.TypedDict):
    active: bool
    bank_pk: str
    auto_padding_0: list[int]
    asset_shares: wrapped_i80f48.WrappedI80F48JSON
    liability_shares: wrapped_i80f48.WrappedI80F48JSON
    emissions_outstanding: wrapped_i80f48.WrappedI80F48JSON
    last_update: int
    padding: list[int]


@dataclass
class Balance:
    layout: typing.ClassVar = borsh.CStruct(
        "active" / borsh.Bool,
        "bank_pk" / BorshPubkey,
        "auto_padding_0" / borsh.U8[7],
        "asset_shares" / wrapped_i80f48.WrappedI80F48.layout,
        "liability_shares" / wrapped_i80f48.WrappedI80F48.layout,
        "emissions_outstanding" / wrapped_i80f48.WrappedI80F48.layout,
        "last_update" / borsh.U64,
        "padding" / borsh.U64[1],
    )
    active: bool
    bank_pk: Pubkey
    auto_padding_0: list[int]
    asset_shares: wrapped_i80f48.WrappedI80F48
    liability_shares: wrapped_i80f48.WrappedI80F48
    emissions_outstanding: wrapped_i80f48.WrappedI80F48
    last_update: int
    padding: list[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "Balance":
        return cls(
            active=obj.active,
            bank_pk=obj.bank_pk,
            auto_padding_0=obj.auto_padding_0,
            asset_shares=wrapped_i80f48.WrappedI80F48.from_decoded(obj.asset_shares),
            liability_shares=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.liability_shares
            ),
            emissions_outstanding=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.emissions_outstanding
            ),
            last_update=obj.last_update,
            padding=obj.padding,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "active": self.active,
            "bank_pk": self.bank_pk,
            "auto_padding_0": self.auto_padding_0,
            "asset_shares": self.asset_shares.to_encodable(),
            "liability_shares": self.liability_shares.to_encodable(),
            "emissions_outstanding": self.emissions_outstanding.to_encodable(),
            "last_update": self.last_update,
            "padding": self.padding,
        }

    def to_json(self) -> BalanceJSON:
        return {
            "active": self.active,
            "bank_pk": str(self.bank_pk),
            "auto_padding_0": self.auto_padding_0,
            "asset_shares": self.asset_shares.to_json(),
            "liability_shares": self.liability_shares.to_json(),
            "emissions_outstanding": self.emissions_outstanding.to_json(),
            "last_update": self.last_update,
            "padding": self.padding,
        }

    @classmethod
    def from_json(cls, obj: BalanceJSON) -> "Balance":
        return cls(
            active=obj["active"],
            bank_pk=Pubkey.from_string(obj["bank_pk"]),
            auto_padding_0=obj["auto_padding_0"],
            asset_shares=wrapped_i80f48.WrappedI80F48.from_json(obj["asset_shares"]),
            liability_shares=wrapped_i80f48.WrappedI80F48.from_json(
                obj["liability_shares"]
            ),
            emissions_outstanding=wrapped_i80f48.WrappedI80F48.from_json(
                obj["emissions_outstanding"]
            ),
            last_update=obj["last_update"],
            padding=obj["padding"],
        )
