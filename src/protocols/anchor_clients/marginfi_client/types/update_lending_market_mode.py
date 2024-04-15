from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class UpdateOwnerJSON(typing.TypedDict):
    kind: typing.Literal["UpdateOwner"]


class UpdateEmergencyModeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateEmergencyMode"]


class UpdateLiquidationCloseFactorJSON(typing.TypedDict):
    kind: typing.Literal["UpdateLiquidationCloseFactor"]


class UpdateLiquidationMaxValueJSON(typing.TypedDict):
    kind: typing.Literal["UpdateLiquidationMaxValue"]


class UpdateGlobalUnhealthyBorrowJSON(typing.TypedDict):
    kind: typing.Literal["UpdateGlobalUnhealthyBorrow"]


class UpdateGlobalAllowedBorrowJSON(typing.TypedDict):
    kind: typing.Literal["UpdateGlobalAllowedBorrow"]


class UpdateRiskCouncilJSON(typing.TypedDict):
    kind: typing.Literal["UpdateRiskCouncil"]


class UpdateMinFullLiquidationThresholdJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMinFullLiquidationThreshold"]


class UpdateInsolvencyRiskLtvJSON(typing.TypedDict):
    kind: typing.Literal["UpdateInsolvencyRiskLtv"]


class UpdateElevationGroupJSON(typing.TypedDict):
    kind: typing.Literal["UpdateElevationGroup"]


class UpdateReferralFeeBpsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateReferralFeeBps"]


class UpdateMultiplierPointsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMultiplierPoints"]


class UpdatePriceRefreshTriggerToMaxAgePctJSON(typing.TypedDict):
    kind: typing.Literal["UpdatePriceRefreshTriggerToMaxAgePct"]


class UpdateAutodeleverageEnabledJSON(typing.TypedDict):
    kind: typing.Literal["UpdateAutodeleverageEnabled"]


@dataclass
class UpdateOwner:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "UpdateOwner"

    @classmethod
    def to_json(cls) -> UpdateOwnerJSON:
        return UpdateOwnerJSON(
            kind="UpdateOwner",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateOwner": {},
        }


@dataclass
class UpdateEmergencyMode:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "UpdateEmergencyMode"

    @classmethod
    def to_json(cls) -> UpdateEmergencyModeJSON:
        return UpdateEmergencyModeJSON(
            kind="UpdateEmergencyMode",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateEmergencyMode": {},
        }


@dataclass
class UpdateLiquidationCloseFactor:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "UpdateLiquidationCloseFactor"

    @classmethod
    def to_json(cls) -> UpdateLiquidationCloseFactorJSON:
        return UpdateLiquidationCloseFactorJSON(
            kind="UpdateLiquidationCloseFactor",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateLiquidationCloseFactor": {},
        }


@dataclass
class UpdateLiquidationMaxValue:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "UpdateLiquidationMaxValue"

    @classmethod
    def to_json(cls) -> UpdateLiquidationMaxValueJSON:
        return UpdateLiquidationMaxValueJSON(
            kind="UpdateLiquidationMaxValue",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateLiquidationMaxValue": {},
        }


@dataclass
class UpdateGlobalUnhealthyBorrow:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "UpdateGlobalUnhealthyBorrow"

    @classmethod
    def to_json(cls) -> UpdateGlobalUnhealthyBorrowJSON:
        return UpdateGlobalUnhealthyBorrowJSON(
            kind="UpdateGlobalUnhealthyBorrow",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateGlobalUnhealthyBorrow": {},
        }


@dataclass
class UpdateGlobalAllowedBorrow:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "UpdateGlobalAllowedBorrow"

    @classmethod
    def to_json(cls) -> UpdateGlobalAllowedBorrowJSON:
        return UpdateGlobalAllowedBorrowJSON(
            kind="UpdateGlobalAllowedBorrow",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateGlobalAllowedBorrow": {},
        }


@dataclass
class UpdateRiskCouncil:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "UpdateRiskCouncil"

    @classmethod
    def to_json(cls) -> UpdateRiskCouncilJSON:
        return UpdateRiskCouncilJSON(
            kind="UpdateRiskCouncil",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateRiskCouncil": {},
        }


@dataclass
class UpdateMinFullLiquidationThreshold:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "UpdateMinFullLiquidationThreshold"

    @classmethod
    def to_json(cls) -> UpdateMinFullLiquidationThresholdJSON:
        return UpdateMinFullLiquidationThresholdJSON(
            kind="UpdateMinFullLiquidationThreshold",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMinFullLiquidationThreshold": {},
        }


@dataclass
class UpdateInsolvencyRiskLtv:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "UpdateInsolvencyRiskLtv"

    @classmethod
    def to_json(cls) -> UpdateInsolvencyRiskLtvJSON:
        return UpdateInsolvencyRiskLtvJSON(
            kind="UpdateInsolvencyRiskLtv",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateInsolvencyRiskLtv": {},
        }


@dataclass
class UpdateElevationGroup:
    discriminator: typing.ClassVar = 9
    kind: typing.ClassVar = "UpdateElevationGroup"

    @classmethod
    def to_json(cls) -> UpdateElevationGroupJSON:
        return UpdateElevationGroupJSON(
            kind="UpdateElevationGroup",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateElevationGroup": {},
        }


@dataclass
class UpdateReferralFeeBps:
    discriminator: typing.ClassVar = 10
    kind: typing.ClassVar = "UpdateReferralFeeBps"

    @classmethod
    def to_json(cls) -> UpdateReferralFeeBpsJSON:
        return UpdateReferralFeeBpsJSON(
            kind="UpdateReferralFeeBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateReferralFeeBps": {},
        }


@dataclass
class UpdateMultiplierPoints:
    discriminator: typing.ClassVar = 11
    kind: typing.ClassVar = "UpdateMultiplierPoints"

    @classmethod
    def to_json(cls) -> UpdateMultiplierPointsJSON:
        return UpdateMultiplierPointsJSON(
            kind="UpdateMultiplierPoints",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMultiplierPoints": {},
        }


@dataclass
class UpdatePriceRefreshTriggerToMaxAgePct:
    discriminator: typing.ClassVar = 12
    kind: typing.ClassVar = "UpdatePriceRefreshTriggerToMaxAgePct"

    @classmethod
    def to_json(cls) -> UpdatePriceRefreshTriggerToMaxAgePctJSON:
        return UpdatePriceRefreshTriggerToMaxAgePctJSON(
            kind="UpdatePriceRefreshTriggerToMaxAgePct",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdatePriceRefreshTriggerToMaxAgePct": {},
        }


@dataclass
class UpdateAutodeleverageEnabled:
    discriminator: typing.ClassVar = 13
    kind: typing.ClassVar = "UpdateAutodeleverageEnabled"

    @classmethod
    def to_json(cls) -> UpdateAutodeleverageEnabledJSON:
        return UpdateAutodeleverageEnabledJSON(
            kind="UpdateAutodeleverageEnabled",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateAutodeleverageEnabled": {},
        }


UpdateLendingMarketModeKind = typing.Union[
    UpdateOwner,
    UpdateEmergencyMode,
    UpdateLiquidationCloseFactor,
    UpdateLiquidationMaxValue,
    UpdateGlobalUnhealthyBorrow,
    UpdateGlobalAllowedBorrow,
    UpdateRiskCouncil,
    UpdateMinFullLiquidationThreshold,
    UpdateInsolvencyRiskLtv,
    UpdateElevationGroup,
    UpdateReferralFeeBps,
    UpdateMultiplierPoints,
    UpdatePriceRefreshTriggerToMaxAgePct,
    UpdateAutodeleverageEnabled,
]
UpdateLendingMarketModeJSON = typing.Union[
    UpdateOwnerJSON,
    UpdateEmergencyModeJSON,
    UpdateLiquidationCloseFactorJSON,
    UpdateLiquidationMaxValueJSON,
    UpdateGlobalUnhealthyBorrowJSON,
    UpdateGlobalAllowedBorrowJSON,
    UpdateRiskCouncilJSON,
    UpdateMinFullLiquidationThresholdJSON,
    UpdateInsolvencyRiskLtvJSON,
    UpdateElevationGroupJSON,
    UpdateReferralFeeBpsJSON,
    UpdateMultiplierPointsJSON,
    UpdatePriceRefreshTriggerToMaxAgePctJSON,
    UpdateAutodeleverageEnabledJSON,
]


def from_decoded(obj: dict) -> UpdateLendingMarketModeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "UpdateOwner" in obj:
        return UpdateOwner()
    if "UpdateEmergencyMode" in obj:
        return UpdateEmergencyMode()
    if "UpdateLiquidationCloseFactor" in obj:
        return UpdateLiquidationCloseFactor()
    if "UpdateLiquidationMaxValue" in obj:
        return UpdateLiquidationMaxValue()
    if "UpdateGlobalUnhealthyBorrow" in obj:
        return UpdateGlobalUnhealthyBorrow()
    if "UpdateGlobalAllowedBorrow" in obj:
        return UpdateGlobalAllowedBorrow()
    if "UpdateRiskCouncil" in obj:
        return UpdateRiskCouncil()
    if "UpdateMinFullLiquidationThreshold" in obj:
        return UpdateMinFullLiquidationThreshold()
    if "UpdateInsolvencyRiskLtv" in obj:
        return UpdateInsolvencyRiskLtv()
    if "UpdateElevationGroup" in obj:
        return UpdateElevationGroup()
    if "UpdateReferralFeeBps" in obj:
        return UpdateReferralFeeBps()
    if "UpdateMultiplierPoints" in obj:
        return UpdateMultiplierPoints()
    if "UpdatePriceRefreshTriggerToMaxAgePct" in obj:
        return UpdatePriceRefreshTriggerToMaxAgePct()
    if "UpdateAutodeleverageEnabled" in obj:
        return UpdateAutodeleverageEnabled()
    raise ValueError("Invalid enum object")


def from_json(obj: UpdateLendingMarketModeJSON) -> UpdateLendingMarketModeKind:
    if obj["kind"] == "UpdateOwner":
        return UpdateOwner()
    if obj["kind"] == "UpdateEmergencyMode":
        return UpdateEmergencyMode()
    if obj["kind"] == "UpdateLiquidationCloseFactor":
        return UpdateLiquidationCloseFactor()
    if obj["kind"] == "UpdateLiquidationMaxValue":
        return UpdateLiquidationMaxValue()
    if obj["kind"] == "UpdateGlobalUnhealthyBorrow":
        return UpdateGlobalUnhealthyBorrow()
    if obj["kind"] == "UpdateGlobalAllowedBorrow":
        return UpdateGlobalAllowedBorrow()
    if obj["kind"] == "UpdateRiskCouncil":
        return UpdateRiskCouncil()
    if obj["kind"] == "UpdateMinFullLiquidationThreshold":
        return UpdateMinFullLiquidationThreshold()
    if obj["kind"] == "UpdateInsolvencyRiskLtv":
        return UpdateInsolvencyRiskLtv()
    if obj["kind"] == "UpdateElevationGroup":
        return UpdateElevationGroup()
    if obj["kind"] == "UpdateReferralFeeBps":
        return UpdateReferralFeeBps()
    if obj["kind"] == "UpdateMultiplierPoints":
        return UpdateMultiplierPoints()
    if obj["kind"] == "UpdatePriceRefreshTriggerToMaxAgePct":
        return UpdatePriceRefreshTriggerToMaxAgePct()
    if obj["kind"] == "UpdateAutodeleverageEnabled":
        return UpdateAutodeleverageEnabled()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "UpdateOwner" / borsh.CStruct(),
    "UpdateEmergencyMode" / borsh.CStruct(),
    "UpdateLiquidationCloseFactor" / borsh.CStruct(),
    "UpdateLiquidationMaxValue" / borsh.CStruct(),
    "UpdateGlobalUnhealthyBorrow" / borsh.CStruct(),
    "UpdateGlobalAllowedBorrow" / borsh.CStruct(),
    "UpdateRiskCouncil" / borsh.CStruct(),
    "UpdateMinFullLiquidationThreshold" / borsh.CStruct(),
    "UpdateInsolvencyRiskLtv" / borsh.CStruct(),
    "UpdateElevationGroup" / borsh.CStruct(),
    "UpdateReferralFeeBps" / borsh.CStruct(),
    "UpdateMultiplierPoints" / borsh.CStruct(),
    "UpdatePriceRefreshTriggerToMaxAgePct" / borsh.CStruct(),
    "UpdateAutodeleverageEnabled" / borsh.CStruct(),
)
