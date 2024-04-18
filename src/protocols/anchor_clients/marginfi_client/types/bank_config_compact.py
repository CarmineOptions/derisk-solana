from __future__ import annotations
from . import (
    interest_rate_config_compact,
    wrapped_i80f48,
    bank_operational_state,
    risk_tier,
    oracle_setup,
)
import typing
from dataclasses import dataclass
from construct import Container
from solders.pubkey import Pubkey
from anchorpy.borsh_extension import BorshPubkey
import borsh_construct as borsh


class BankConfigCompactJSON(typing.TypedDict):
    asset_weight_init: wrapped_i80f48.WrappedI80F48JSON
    asset_weight_maint: wrapped_i80f48.WrappedI80F48JSON
    liability_weight_init: wrapped_i80f48.WrappedI80F48JSON
    liability_weight_maint: wrapped_i80f48.WrappedI80F48JSON
    deposit_limit: int
    interest_rate_config: interest_rate_config_compact.InterestRateConfigCompactJSON
    operational_state: bank_operational_state.BankOperationalStateJSON
    oracle_setup: oracle_setup.OracleSetupJSON
    oracle_key: str
    auto_padding_0: list[int]
    borrow_limit: int
    risk_tier: risk_tier.RiskTierJSON
    auto_padding_1: list[int]
    total_asset_value_init_limit: int


@dataclass
class BankConfigCompact:
    layout: typing.ClassVar = borsh.CStruct(
        "asset_weight_init" / wrapped_i80f48.WrappedI80F48.layout,
        "asset_weight_maint" / wrapped_i80f48.WrappedI80F48.layout,
        "liability_weight_init" / wrapped_i80f48.WrappedI80F48.layout,
        "liability_weight_maint" / wrapped_i80f48.WrappedI80F48.layout,
        "deposit_limit" / borsh.U64,
        "interest_rate_config"
        / interest_rate_config_compact.InterestRateConfigCompact.layout,
        "operational_state" / bank_operational_state.layout,
        "oracle_setup" / oracle_setup.layout,
        "oracle_key" / BorshPubkey,
        "auto_padding_0" / borsh.U8[6],
        "borrow_limit" / borsh.U64,
        "risk_tier" / risk_tier.layout,
        "auto_padding_1" / borsh.U8[7],
        "total_asset_value_init_limit" / borsh.U64,
    )
    asset_weight_init: wrapped_i80f48.WrappedI80F48
    asset_weight_maint: wrapped_i80f48.WrappedI80F48
    liability_weight_init: wrapped_i80f48.WrappedI80F48
    liability_weight_maint: wrapped_i80f48.WrappedI80F48
    deposit_limit: int
    interest_rate_config: interest_rate_config_compact.InterestRateConfigCompact
    operational_state: bank_operational_state.BankOperationalStateKind
    oracle_setup: oracle_setup.OracleSetupKind
    oracle_key: Pubkey
    auto_padding_0: list[int]
    borrow_limit: int
    risk_tier: risk_tier.RiskTierKind
    auto_padding_1: list[int]
    total_asset_value_init_limit: int

    @classmethod
    def from_decoded(cls, obj: Container) -> "BankConfigCompact":
        return cls(
            asset_weight_init=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.asset_weight_init
            ),
            asset_weight_maint=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.asset_weight_maint
            ),
            liability_weight_init=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.liability_weight_init
            ),
            liability_weight_maint=wrapped_i80f48.WrappedI80F48.from_decoded(
                obj.liability_weight_maint
            ),
            deposit_limit=obj.deposit_limit,
            interest_rate_config=interest_rate_config_compact.InterestRateConfigCompact.from_decoded(
                obj.interest_rate_config
            ),
            operational_state=bank_operational_state.from_decoded(
                obj.operational_state
            ),
            oracle_setup=oracle_setup.from_decoded(obj.oracle_setup),
            oracle_key=obj.oracle_key,
            auto_padding_0=obj.auto_padding_0,
            borrow_limit=obj.borrow_limit,
            risk_tier=risk_tier.from_decoded(obj.risk_tier),
            auto_padding_1=obj.auto_padding_1,
            total_asset_value_init_limit=obj.total_asset_value_init_limit,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "asset_weight_init": self.asset_weight_init.to_encodable(),
            "asset_weight_maint": self.asset_weight_maint.to_encodable(),
            "liability_weight_init": self.liability_weight_init.to_encodable(),
            "liability_weight_maint": self.liability_weight_maint.to_encodable(),
            "deposit_limit": self.deposit_limit,
            "interest_rate_config": self.interest_rate_config.to_encodable(),
            "operational_state": self.operational_state.to_encodable(),
            "oracle_setup": self.oracle_setup.to_encodable(),
            "oracle_key": self.oracle_key,
            "auto_padding_0": self.auto_padding_0,
            "borrow_limit": self.borrow_limit,
            "risk_tier": self.risk_tier.to_encodable(),
            "auto_padding_1": self.auto_padding_1,
            "total_asset_value_init_limit": self.total_asset_value_init_limit,
        }

    def to_json(self) -> BankConfigCompactJSON:
        return {
            "asset_weight_init": self.asset_weight_init.to_json(),
            "asset_weight_maint": self.asset_weight_maint.to_json(),
            "liability_weight_init": self.liability_weight_init.to_json(),
            "liability_weight_maint": self.liability_weight_maint.to_json(),
            "deposit_limit": self.deposit_limit,
            "interest_rate_config": self.interest_rate_config.to_json(),
            "operational_state": self.operational_state.to_json(),
            "oracle_setup": self.oracle_setup.to_json(),
            "oracle_key": str(self.oracle_key),
            "auto_padding_0": self.auto_padding_0,
            "borrow_limit": self.borrow_limit,
            "risk_tier": self.risk_tier.to_json(),
            "auto_padding_1": self.auto_padding_1,
            "total_asset_value_init_limit": self.total_asset_value_init_limit,
        }

    @classmethod
    def from_json(cls, obj: BankConfigCompactJSON) -> "BankConfigCompact":
        return cls(
            asset_weight_init=wrapped_i80f48.WrappedI80F48.from_json(
                obj["asset_weight_init"]
            ),
            asset_weight_maint=wrapped_i80f48.WrappedI80F48.from_json(
                obj["asset_weight_maint"]
            ),
            liability_weight_init=wrapped_i80f48.WrappedI80F48.from_json(
                obj["liability_weight_init"]
            ),
            liability_weight_maint=wrapped_i80f48.WrappedI80F48.from_json(
                obj["liability_weight_maint"]
            ),
            deposit_limit=obj["deposit_limit"],
            interest_rate_config=interest_rate_config_compact.InterestRateConfigCompact.from_json(
                obj["interest_rate_config"]
            ),
            operational_state=bank_operational_state.from_json(
                obj["operational_state"]
            ),
            oracle_setup=oracle_setup.from_json(obj["oracle_setup"]),
            oracle_key=Pubkey.from_string(obj["oracle_key"]),
            auto_padding_0=obj["auto_padding_0"],
            borrow_limit=obj["borrow_limit"],
            risk_tier=risk_tier.from_json(obj["risk_tier"]),
            auto_padding_1=obj["auto_padding_1"],
            total_asset_value_init_limit=obj["total_asset_value_init_limit"],
        )
