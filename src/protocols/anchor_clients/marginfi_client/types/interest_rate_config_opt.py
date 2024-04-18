from __future__ import annotations
from . import (
    wrapped_i80f48,
)
import typing
from dataclasses import dataclass
from construct import Container
import borsh_construct as borsh


class InterestRateConfigOptJSON(typing.TypedDict):
    optimal_utilization_rate: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    plateau_interest_rate: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    max_interest_rate: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    insurance_fee_fixed_apr: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    insurance_ir_fee: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    protocol_fixed_fee_apr: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]
    protocol_ir_fee: typing.Optional[wrapped_i80f48.WrappedI80F48JSON]


@dataclass
class InterestRateConfigOpt:
    layout: typing.ClassVar = borsh.CStruct(
        "optimal_utilization_rate" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "plateau_interest_rate" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "max_interest_rate" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "insurance_fee_fixed_apr" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "insurance_ir_fee" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "protocol_fixed_fee_apr" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
        "protocol_ir_fee" / borsh.Option(wrapped_i80f48.WrappedI80F48.layout),
    )
    optimal_utilization_rate: typing.Optional[wrapped_i80f48.WrappedI80F48]
    plateau_interest_rate: typing.Optional[wrapped_i80f48.WrappedI80F48]
    max_interest_rate: typing.Optional[wrapped_i80f48.WrappedI80F48]
    insurance_fee_fixed_apr: typing.Optional[wrapped_i80f48.WrappedI80F48]
    insurance_ir_fee: typing.Optional[wrapped_i80f48.WrappedI80F48]
    protocol_fixed_fee_apr: typing.Optional[wrapped_i80f48.WrappedI80F48]
    protocol_ir_fee: typing.Optional[wrapped_i80f48.WrappedI80F48]

    @classmethod
    def from_decoded(cls, obj: Container) -> "InterestRateConfigOpt":
        return cls(
            optimal_utilization_rate=(
                None
                if obj.optimal_utilization_rate is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.optimal_utilization_rate
                )
            ),
            plateau_interest_rate=(
                None
                if obj.plateau_interest_rate is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.plateau_interest_rate
                )
            ),
            max_interest_rate=(
                None
                if obj.max_interest_rate is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(obj.max_interest_rate)
            ),
            insurance_fee_fixed_apr=(
                None
                if obj.insurance_fee_fixed_apr is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.insurance_fee_fixed_apr
                )
            ),
            insurance_ir_fee=(
                None
                if obj.insurance_ir_fee is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(obj.insurance_ir_fee)
            ),
            protocol_fixed_fee_apr=(
                None
                if obj.protocol_fixed_fee_apr is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(
                    obj.protocol_fixed_fee_apr
                )
            ),
            protocol_ir_fee=(
                None
                if obj.protocol_ir_fee is None
                else wrapped_i80f48.WrappedI80F48.from_decoded(obj.protocol_ir_fee)
            ),
        )

    def to_encodable(self) -> dict[str, typing.Any]:
        return {
            "optimal_utilization_rate": (
                None
                if self.optimal_utilization_rate is None
                else self.optimal_utilization_rate.to_encodable()
            ),
            "plateau_interest_rate": (
                None
                if self.plateau_interest_rate is None
                else self.plateau_interest_rate.to_encodable()
            ),
            "max_interest_rate": (
                None
                if self.max_interest_rate is None
                else self.max_interest_rate.to_encodable()
            ),
            "insurance_fee_fixed_apr": (
                None
                if self.insurance_fee_fixed_apr is None
                else self.insurance_fee_fixed_apr.to_encodable()
            ),
            "insurance_ir_fee": (
                None
                if self.insurance_ir_fee is None
                else self.insurance_ir_fee.to_encodable()
            ),
            "protocol_fixed_fee_apr": (
                None
                if self.protocol_fixed_fee_apr is None
                else self.protocol_fixed_fee_apr.to_encodable()
            ),
            "protocol_ir_fee": (
                None
                if self.protocol_ir_fee is None
                else self.protocol_ir_fee.to_encodable()
            ),
        }

    def to_json(self) -> InterestRateConfigOptJSON:
        return {
            "optimal_utilization_rate": (
                None
                if self.optimal_utilization_rate is None
                else self.optimal_utilization_rate.to_json()
            ),
            "plateau_interest_rate": (
                None
                if self.plateau_interest_rate is None
                else self.plateau_interest_rate.to_json()
            ),
            "max_interest_rate": (
                None
                if self.max_interest_rate is None
                else self.max_interest_rate.to_json()
            ),
            "insurance_fee_fixed_apr": (
                None
                if self.insurance_fee_fixed_apr is None
                else self.insurance_fee_fixed_apr.to_json()
            ),
            "insurance_ir_fee": (
                None
                if self.insurance_ir_fee is None
                else self.insurance_ir_fee.to_json()
            ),
            "protocol_fixed_fee_apr": (
                None
                if self.protocol_fixed_fee_apr is None
                else self.protocol_fixed_fee_apr.to_json()
            ),
            "protocol_ir_fee": (
                None if self.protocol_ir_fee is None else self.protocol_ir_fee.to_json()
            ),
        }

    @classmethod
    def from_json(cls, obj: InterestRateConfigOptJSON) -> "InterestRateConfigOpt":
        return cls(
            optimal_utilization_rate=(
                None
                if obj["optimal_utilization_rate"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["optimal_utilization_rate"]
                )
            ),
            plateau_interest_rate=(
                None
                if obj["plateau_interest_rate"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["plateau_interest_rate"]
                )
            ),
            max_interest_rate=(
                None
                if obj["max_interest_rate"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(obj["max_interest_rate"])
            ),
            insurance_fee_fixed_apr=(
                None
                if obj["insurance_fee_fixed_apr"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["insurance_fee_fixed_apr"]
                )
            ),
            insurance_ir_fee=(
                None
                if obj["insurance_ir_fee"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(obj["insurance_ir_fee"])
            ),
            protocol_fixed_fee_apr=(
                None
                if obj["protocol_fixed_fee_apr"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(
                    obj["protocol_fixed_fee_apr"]
                )
            ),
            protocol_ir_fee=(
                None
                if obj["protocol_ir_fee"] is None
                else wrapped_i80f48.WrappedI80F48.from_json(obj["protocol_ir_fee"])
            ),
        )
