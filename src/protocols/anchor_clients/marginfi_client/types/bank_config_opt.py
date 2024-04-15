from __future__ import annotations
from . import (
    interest_rate_config_opt,
    wrapped_i80f48,
    oracle_config,
    bank_operational_state,
    risk_tier,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class BankConfigOptJSON(typing.TypedDict):
    asset_weight_init: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    asset_weight_maint: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    liability_weight_init: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    liability_weight_maint: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    deposit_limit: typing.Optional[int]
    borrow_limit: typing.Optional[int]
    operational_state: typing.Optional[bank_operational_state.BankOperationalStateJSON]
    oracle: typing.Optional[oracle_config.OracleConfigJSON]
    interest_rate_config: typing.Optional[
        interest_rate_config_opt.InterestRateConfigOptJSON
    ]
    risk_tier: typing.Optional[risk_tier.RiskTierJSON]
    total_asset_value_init_limit: typing.Optional[int]


@dataclass
class BankConfigOpt:
    layout: typing.ClassVar = borsh.CStruct(
        "asset_weight_init" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "asset_weight_maint" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "liability_weight_init" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "liability_weight_maint" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "deposit_limit" / borsh.Option(borsh.U64),
        "borrow_limit" / borsh.Option(borsh.U64),
        "operational_state" / borsh.Option(bank_operational_state.layout),
        "oracle" / borsh.Option(oracle_config.OracleConfig.layout),
        "interest_rate_config"
        / borsh.Option(interest_rate_config_opt.InterestRateConfigOpt.layout),
        "risk_tier" / borsh.Option(risk_tier.layout),
        "total_asset_value_init_limit" / borsh.Option(borsh.U64),
    )
    asset_weight_init: typing.Optional[wrapped_i80f48.WrappedI80F48]
    asset_weight_maint: typing.Optional[wrapped_i80f48.WrappedI80F48]
    liability_weight_init: typing.Optional[wrapped_i80f48.WrappedI80F48]
    liability_weight_maint: typing.Optional[wrapped_i80f48.WrappedI80F48]
    deposit_limit: typing.Optional[int]
    borrow_limit: typing.Optional[int]
    operational_state: typing.Optional[bank_operational_state.BankOperationalStateKind]
    oracle: typing.Optional[oracle_config.OracleConfig]
    interest_rate_config: typing.Optional[
        interest_rate_config_opt.InterestRateConfigOpt
    ]
    risk_tier: typing.Optional[risk_tier.RiskTierKind]
    total_asset_value_init_limit: typing.Optional[int]

    @classmethod
    def from_decoded(cls, obj: Container) -> "BankConfigOpt":
        return cls(
            asset_weight_init=(
                None
                if obj.asset_weight_init is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(obj.asset_weight_init)
            ),
            asset_weight_maint=(
                None
                if obj.asset_weight_maint is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(obj.asset_weight_maint)
            ),
            liability_weight_init=(
                None
                if obj.liability_weight_init is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.liability_weight_init
                )
            ),
            liability_weight_maint=(
                None
                if obj.liability_weight_maint is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.liability_weight_maint
                )
            ),
            deposit_limit=obj.deposit_limit,
            borrow_limit=obj.borrow_limit,
            operational_state=(
                None
                if obj.operational_state is None
                else bank_operational_state.from_decoded(obj.operational_state)
            ),
            oracle=(
                None
                if obj.oracle is None
                else oracle_config.OracleConfig.from_decoded(obj.oracle)
            ),
            interest_rate_config=(
                None
                if obj.interest_rate_config is None
                else interest_rate_config_opt.InterestRateConfigOpt.from_decoded(
                    obj.interest_rate_config
                )
            ),
            risk_tier=(
                None if obj.risk_tier is None else risk_tier.from_decoded(obj.risk_tier)
            ),
            total_asset_value_init_limit=obj.total_asset_value_init_limit,
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "asset_weight_init": (
                None
                if self.asset_weight_init is None
                else self.asset_weight_init.to_encodable()
            ),
            "asset_weight_maint": (
                None
                if self.asset_weight_maint is None
                else self.asset_weight_maint.to_encodable()
            ),
            "liability_weight_init": (
                None
                if self.liability_weight_init is None
                else self.liability_weight_init.to_encodable()
            ),
            "liability_weight_maint": (
                None
                if self.liability_weight_maint is None
                else self.liability_weight_maint.to_encodable()
            ),
            "deposit_limit": self.deposit_limit,
            "borrow_limit": self.borrow_limit,
            "operational_state": (
                None
                if self.operational_state is None
                else self.operational_state.to_encodable()
            ),
            "oracle": (None if self.oracle is None else self.oracle.to_encodable()),
            "interest_rate_config": (
                None
                if self.interest_rate_config is None
                else self.interest_rate_config.to_encodable()
            ),
            "risk_tier": (
                None if self.risk_tier is None else self.risk_tier.to_encodable()
            ),
            "total_asset_value_init_limit": self.total_asset_value_init_limit,
        }

    def to_json(self) -> BankConfigOptJSON:
        return {
            "asset_weight_init": (
                None
                if self.asset_weight_init is None
                else self.asset_weight_init.to_json()
            ),
            "asset_weight_maint": (
                None
                if self.asset_weight_maint is None
                else self.asset_weight_maint.to_json()
            ),
            "liability_weight_init": (
                None
                if self.liability_weight_init is None
                else self.liability_weight_init.to_json()
            ),
            "liability_weight_maint": (
                None
                if self.liability_weight_maint is None
                else self.liability_weight_maint.to_json()
            ),
            "deposit_limit": self.deposit_limit,
            "borrow_limit": self.borrow_limit,
            "operational_state": (
                None
                if self.operational_state is None
                else self.operational_state.to_json()
            ),
            "oracle": (None if self.oracle is None else self.oracle.to_json()),
            "interest_rate_config": (
                None
                if self.interest_rate_config is None
                else self.interest_rate_config.to_json()
            ),
            "risk_tier": (None if self.risk_tier is None else self.risk_tier.to_json()),
            "total_asset_value_init_limit": self.total_asset_value_init_limit,
        }

    @classmethod
    def from_json(cls, obj: BankConfigOptJSON) -> "BankConfigOpt":
        return cls(
            asset_weight_init=(
                None
                if obj["asset_weight_init"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(obj["asset_weight_init"])
            ),
            asset_weight_maint=(
                None
                if obj["asset_weight_maint"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(obj["asset_weight_maint"])
            ),
            liability_weight_init=(
                None
                if obj["liability_weight_init"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["liability_weight_init"]
                )
            ),
            liability_weight_maint=(
                None
                if obj["liability_weight_maint"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["liability_weight_maint"]
                )
            ),
            deposit_limit=obj["deposit_limit"],
            borrow_limit=obj["borrow_limit"],
            operational_state=(
                None
                if obj["operational_state"] is None
                else bank_operational_state.from_json(obj["operational_state"])
            ),
            oracle=(
                None
                if obj["oracle"] is None
                else oracle_config.OracleConfig.from_json(obj["oracle"])
            ),
            interest_rate_config=(
                None
                if obj["interest_rate_config"] is None
                else interest_rate_config_opt.InterestRateConfigOpt.from_json(
                    obj["interest_rate_config"]
                )
            ),
            risk_tier=(
                None
                if obj["risk_tier"] is None
                else risk_tier.from_json(obj["risk_tier"])
            ),
            total_asset_value_init_limit=obj["total_asset_value_init_limit"],
        )
