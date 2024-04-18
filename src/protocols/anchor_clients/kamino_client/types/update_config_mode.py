from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class UpdateLoanToValuePctJSON(typing.TypedDict):
    kind: typing.Literal["UpdateLoanToValuePct"]


class UpdateMaxLiquidationBonusBpsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMaxLiquidationBonusBps"]


class UpdateLiquidationThresholdPctJSON(typing.TypedDict):
    kind: typing.Literal["UpdateLiquidationThresholdPct"]


class UpdateProtocolLiquidationFeeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateProtocolLiquidationFee"]


class UpdateProtocolTakeRateJSON(typing.TypedDict):
    kind: typing.Literal["UpdateProtocolTakeRate"]


class UpdateFeesBorrowFeeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateFeesBorrowFee"]


class UpdateFeesFlashLoanFeeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateFeesFlashLoanFee"]


class UpdateFeesReferralFeeBpsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateFeesReferralFeeBps"]


class UpdateDepositLimitJSON(typing.TypedDict):
    kind: typing.Literal["UpdateDepositLimit"]


class UpdateBorrowLimitJSON(typing.TypedDict):
    kind: typing.Literal["UpdateBorrowLimit"]


class UpdateTokenInfoLowerHeuristicJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoLowerHeuristic"]


class UpdateTokenInfoUpperHeuristicJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoUpperHeuristic"]


class UpdateTokenInfoExpHeuristicJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoExpHeuristic"]


class UpdateTokenInfoTwapDivergenceJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoTwapDivergence"]


class UpdateTokenInfoScopeTwapJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoScopeTwap"]


class UpdateTokenInfoScopeChainJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoScopeChain"]


class UpdateTokenInfoNameJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoName"]


class UpdateTokenInfoPriceMaxAgeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoPriceMaxAge"]


class UpdateTokenInfoTwapMaxAgeJSON(typing.TypedDict):
    kind: typing.Literal["UpdateTokenInfoTwapMaxAge"]


class UpdateScopePriceFeedJSON(typing.TypedDict):
    kind: typing.Literal["UpdateScopePriceFeed"]


class UpdatePythPriceJSON(typing.TypedDict):
    kind: typing.Literal["UpdatePythPrice"]


class UpdateSwitchboardFeedJSON(typing.TypedDict):
    kind: typing.Literal["UpdateSwitchboardFeed"]


class UpdateSwitchboardTwapFeedJSON(typing.TypedDict):
    kind: typing.Literal["UpdateSwitchboardTwapFeed"]


class UpdateBorrowRateCurveJSON(typing.TypedDict):
    kind: typing.Literal["UpdateBorrowRateCurve"]


class UpdateEntireReserveConfigJSON(typing.TypedDict):
    kind: typing.Literal["UpdateEntireReserveConfig"]


class UpdateDebtWithdrawalCapJSON(typing.TypedDict):
    kind: typing.Literal["UpdateDebtWithdrawalCap"]


class UpdateDepositWithdrawalCapJSON(typing.TypedDict):
    kind: typing.Literal["UpdateDepositWithdrawalCap"]


class UpdateDebtWithdrawalCapCurrentTotalJSON(typing.TypedDict):
    kind: typing.Literal["UpdateDebtWithdrawalCapCurrentTotal"]


class UpdateDepositWithdrawalCapCurrentTotalJSON(typing.TypedDict):
    kind: typing.Literal["UpdateDepositWithdrawalCapCurrentTotal"]


class UpdateBadDebtLiquidationBonusBpsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateBadDebtLiquidationBonusBps"]


class UpdateMinLiquidationBonusBpsJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMinLiquidationBonusBps"]


class DeleveragingMarginCallPeriodJSON(typing.TypedDict):
    kind: typing.Literal["DeleveragingMarginCallPeriod"]


class UpdateBorrowFactorJSON(typing.TypedDict):
    kind: typing.Literal["UpdateBorrowFactor"]


class UpdateAssetTierJSON(typing.TypedDict):
    kind: typing.Literal["UpdateAssetTier"]


class UpdateElevationGroupJSON(typing.TypedDict):
    kind: typing.Literal["UpdateElevationGroup"]


class DeleveragingThresholdSlotsPerBpsJSON(typing.TypedDict):
    kind: typing.Literal["DeleveragingThresholdSlotsPerBps"]


class UpdateMultiplierSideBoostJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMultiplierSideBoost"]


class UpdateMultiplierTagBoostJSON(typing.TypedDict):
    kind: typing.Literal["UpdateMultiplierTagBoost"]


class UpdateReserveStatusJSON(typing.TypedDict):
    kind: typing.Literal["UpdateReserveStatus"]


@dataclass
class UpdateLoanToValuePct:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "UpdateLoanToValuePct"

    @classmethod
    def to_json(cls) -> UpdateLoanToValuePctJSON:
        return UpdateLoanToValuePctJSON(
            kind="UpdateLoanToValuePct",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateLoanToValuePct": {},
        }


@dataclass
class UpdateMaxLiquidationBonusBps:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "UpdateMaxLiquidationBonusBps"

    @classmethod
    def to_json(cls) -> UpdateMaxLiquidationBonusBpsJSON:
        return UpdateMaxLiquidationBonusBpsJSON(
            kind="UpdateMaxLiquidationBonusBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMaxLiquidationBonusBps": {},
        }


@dataclass
class UpdateLiquidationThresholdPct:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "UpdateLiquidationThresholdPct"

    @classmethod
    def to_json(cls) -> UpdateLiquidationThresholdPctJSON:
        return UpdateLiquidationThresholdPctJSON(
            kind="UpdateLiquidationThresholdPct",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateLiquidationThresholdPct": {},
        }


@dataclass
class UpdateProtocolLiquidationFee:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "UpdateProtocolLiquidationFee"

    @classmethod
    def to_json(cls) -> UpdateProtocolLiquidationFeeJSON:
        return UpdateProtocolLiquidationFeeJSON(
            kind="UpdateProtocolLiquidationFee",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateProtocolLiquidationFee": {},
        }


@dataclass
class UpdateProtocolTakeRate:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "UpdateProtocolTakeRate"

    @classmethod
    def to_json(cls) -> UpdateProtocolTakeRateJSON:
        return UpdateProtocolTakeRateJSON(
            kind="UpdateProtocolTakeRate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateProtocolTakeRate": {},
        }


@dataclass
class UpdateFeesBorrowFee:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "UpdateFeesBorrowFee"

    @classmethod
    def to_json(cls) -> UpdateFeesBorrowFeeJSON:
        return UpdateFeesBorrowFeeJSON(
            kind="UpdateFeesBorrowFee",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateFeesBorrowFee": {},
        }


@dataclass
class UpdateFeesFlashLoanFee:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "UpdateFeesFlashLoanFee"

    @classmethod
    def to_json(cls) -> UpdateFeesFlashLoanFeeJSON:
        return UpdateFeesFlashLoanFeeJSON(
            kind="UpdateFeesFlashLoanFee",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateFeesFlashLoanFee": {},
        }


@dataclass
class UpdateFeesReferralFeeBps:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "UpdateFeesReferralFeeBps"

    @classmethod
    def to_json(cls) -> UpdateFeesReferralFeeBpsJSON:
        return UpdateFeesReferralFeeBpsJSON(
            kind="UpdateFeesReferralFeeBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateFeesReferralFeeBps": {},
        }


@dataclass
class UpdateDepositLimit:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "UpdateDepositLimit"

    @classmethod
    def to_json(cls) -> UpdateDepositLimitJSON:
        return UpdateDepositLimitJSON(
            kind="UpdateDepositLimit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateDepositLimit": {},
        }


@dataclass
class UpdateBorrowLimit:
    discriminator: typing.ClassVar = 9
    kind: typing.ClassVar = "UpdateBorrowLimit"

    @classmethod
    def to_json(cls) -> UpdateBorrowLimitJSON:
        return UpdateBorrowLimitJSON(
            kind="UpdateBorrowLimit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateBorrowLimit": {},
        }


@dataclass
class UpdateTokenInfoLowerHeuristic:
    discriminator: typing.ClassVar = 10
    kind: typing.ClassVar = "UpdateTokenInfoLowerHeuristic"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoLowerHeuristicJSON:
        return UpdateTokenInfoLowerHeuristicJSON(
            kind="UpdateTokenInfoLowerHeuristic",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoLowerHeuristic": {},
        }


@dataclass
class UpdateTokenInfoUpperHeuristic:
    discriminator: typing.ClassVar = 11
    kind: typing.ClassVar = "UpdateTokenInfoUpperHeuristic"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoUpperHeuristicJSON:
        return UpdateTokenInfoUpperHeuristicJSON(
            kind="UpdateTokenInfoUpperHeuristic",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoUpperHeuristic": {},
        }


@dataclass
class UpdateTokenInfoExpHeuristic:
    discriminator: typing.ClassVar = 12
    kind: typing.ClassVar = "UpdateTokenInfoExpHeuristic"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoExpHeuristicJSON:
        return UpdateTokenInfoExpHeuristicJSON(
            kind="UpdateTokenInfoExpHeuristic",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoExpHeuristic": {},
        }


@dataclass
class UpdateTokenInfoTwapDivergence:
    discriminator: typing.ClassVar = 13
    kind: typing.ClassVar = "UpdateTokenInfoTwapDivergence"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoTwapDivergenceJSON:
        return UpdateTokenInfoTwapDivergenceJSON(
            kind="UpdateTokenInfoTwapDivergence",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoTwapDivergence": {},
        }


@dataclass
class UpdateTokenInfoScopeTwap:
    discriminator: typing.ClassVar = 14
    kind: typing.ClassVar = "UpdateTokenInfoScopeTwap"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoScopeTwapJSON:
        return UpdateTokenInfoScopeTwapJSON(
            kind="UpdateTokenInfoScopeTwap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoScopeTwap": {},
        }


@dataclass
class UpdateTokenInfoScopeChain:
    discriminator: typing.ClassVar = 15
    kind: typing.ClassVar = "UpdateTokenInfoScopeChain"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoScopeChainJSON:
        return UpdateTokenInfoScopeChainJSON(
            kind="UpdateTokenInfoScopeChain",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoScopeChain": {},
        }


@dataclass
class UpdateTokenInfoName:
    discriminator: typing.ClassVar = 16
    kind: typing.ClassVar = "UpdateTokenInfoName"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoNameJSON:
        return UpdateTokenInfoNameJSON(
            kind="UpdateTokenInfoName",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoName": {},
        }


@dataclass
class UpdateTokenInfoPriceMaxAge:
    discriminator: typing.ClassVar = 17
    kind: typing.ClassVar = "UpdateTokenInfoPriceMaxAge"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoPriceMaxAgeJSON:
        return UpdateTokenInfoPriceMaxAgeJSON(
            kind="UpdateTokenInfoPriceMaxAge",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoPriceMaxAge": {},
        }


@dataclass
class UpdateTokenInfoTwapMaxAge:
    discriminator: typing.ClassVar = 18
    kind: typing.ClassVar = "UpdateTokenInfoTwapMaxAge"

    @classmethod
    def to_json(cls) -> UpdateTokenInfoTwapMaxAgeJSON:
        return UpdateTokenInfoTwapMaxAgeJSON(
            kind="UpdateTokenInfoTwapMaxAge",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateTokenInfoTwapMaxAge": {},
        }


@dataclass
class UpdateScopePriceFeed:
    discriminator: typing.ClassVar = 19
    kind: typing.ClassVar = "UpdateScopePriceFeed"

    @classmethod
    def to_json(cls) -> UpdateScopePriceFeedJSON:
        return UpdateScopePriceFeedJSON(
            kind="UpdateScopePriceFeed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateScopePriceFeed": {},
        }


@dataclass
class UpdatePythPrice:
    discriminator: typing.ClassVar = 20
    kind: typing.ClassVar = "UpdatePythPrice"

    @classmethod
    def to_json(cls) -> UpdatePythPriceJSON:
        return UpdatePythPriceJSON(
            kind="UpdatePythPrice",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdatePythPrice": {},
        }


@dataclass
class UpdateSwitchboardFeed:
    discriminator: typing.ClassVar = 21
    kind: typing.ClassVar = "UpdateSwitchboardFeed"

    @classmethod
    def to_json(cls) -> UpdateSwitchboardFeedJSON:
        return UpdateSwitchboardFeedJSON(
            kind="UpdateSwitchboardFeed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateSwitchboardFeed": {},
        }


@dataclass
class UpdateSwitchboardTwapFeed:
    discriminator: typing.ClassVar = 22
    kind: typing.ClassVar = "UpdateSwitchboardTwapFeed"

    @classmethod
    def to_json(cls) -> UpdateSwitchboardTwapFeedJSON:
        return UpdateSwitchboardTwapFeedJSON(
            kind="UpdateSwitchboardTwapFeed",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateSwitchboardTwapFeed": {},
        }


@dataclass
class UpdateBorrowRateCurve:
    discriminator: typing.ClassVar = 23
    kind: typing.ClassVar = "UpdateBorrowRateCurve"

    @classmethod
    def to_json(cls) -> UpdateBorrowRateCurveJSON:
        return UpdateBorrowRateCurveJSON(
            kind="UpdateBorrowRateCurve",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateBorrowRateCurve": {},
        }


@dataclass
class UpdateEntireReserveConfig:
    discriminator: typing.ClassVar = 24
    kind: typing.ClassVar = "UpdateEntireReserveConfig"

    @classmethod
    def to_json(cls) -> UpdateEntireReserveConfigJSON:
        return UpdateEntireReserveConfigJSON(
            kind="UpdateEntireReserveConfig",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateEntireReserveConfig": {},
        }


@dataclass
class UpdateDebtWithdrawalCap:
    discriminator: typing.ClassVar = 25
    kind: typing.ClassVar = "UpdateDebtWithdrawalCap"

    @classmethod
    def to_json(cls) -> UpdateDebtWithdrawalCapJSON:
        return UpdateDebtWithdrawalCapJSON(
            kind="UpdateDebtWithdrawalCap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateDebtWithdrawalCap": {},
        }


@dataclass
class UpdateDepositWithdrawalCap:
    discriminator: typing.ClassVar = 26
    kind: typing.ClassVar = "UpdateDepositWithdrawalCap"

    @classmethod
    def to_json(cls) -> UpdateDepositWithdrawalCapJSON:
        return UpdateDepositWithdrawalCapJSON(
            kind="UpdateDepositWithdrawalCap",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateDepositWithdrawalCap": {},
        }


@dataclass
class UpdateDebtWithdrawalCapCurrentTotal:
    discriminator: typing.ClassVar = 27
    kind: typing.ClassVar = "UpdateDebtWithdrawalCapCurrentTotal"

    @classmethod
    def to_json(cls) -> UpdateDebtWithdrawalCapCurrentTotalJSON:
        return UpdateDebtWithdrawalCapCurrentTotalJSON(
            kind="UpdateDebtWithdrawalCapCurrentTotal",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateDebtWithdrawalCapCurrentTotal": {},
        }


@dataclass
class UpdateDepositWithdrawalCapCurrentTotal:
    discriminator: typing.ClassVar = 28
    kind: typing.ClassVar = "UpdateDepositWithdrawalCapCurrentTotal"

    @classmethod
    def to_json(cls) -> UpdateDepositWithdrawalCapCurrentTotalJSON:
        return UpdateDepositWithdrawalCapCurrentTotalJSON(
            kind="UpdateDepositWithdrawalCapCurrentTotal",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateDepositWithdrawalCapCurrentTotal": {},
        }


@dataclass
class UpdateBadDebtLiquidationBonusBps:
    discriminator: typing.ClassVar = 29
    kind: typing.ClassVar = "UpdateBadDebtLiquidationBonusBps"

    @classmethod
    def to_json(cls) -> UpdateBadDebtLiquidationBonusBpsJSON:
        return UpdateBadDebtLiquidationBonusBpsJSON(
            kind="UpdateBadDebtLiquidationBonusBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateBadDebtLiquidationBonusBps": {},
        }


@dataclass
class UpdateMinLiquidationBonusBps:
    discriminator: typing.ClassVar = 30
    kind: typing.ClassVar = "UpdateMinLiquidationBonusBps"

    @classmethod
    def to_json(cls) -> UpdateMinLiquidationBonusBpsJSON:
        return UpdateMinLiquidationBonusBpsJSON(
            kind="UpdateMinLiquidationBonusBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMinLiquidationBonusBps": {},
        }


@dataclass
class DeleveragingMarginCallPeriod:
    discriminator: typing.ClassVar = 31
    kind: typing.ClassVar = "DeleveragingMarginCallPeriod"

    @classmethod
    def to_json(cls) -> DeleveragingMarginCallPeriodJSON:
        return DeleveragingMarginCallPeriodJSON(
            kind="DeleveragingMarginCallPeriod",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "DeleveragingMarginCallPeriod": {},
        }


@dataclass
class UpdateBorrowFactor:
    discriminator: typing.ClassVar = 32
    kind: typing.ClassVar = "UpdateBorrowFactor"

    @classmethod
    def to_json(cls) -> UpdateBorrowFactorJSON:
        return UpdateBorrowFactorJSON(
            kind="UpdateBorrowFactor",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateBorrowFactor": {},
        }


@dataclass
class UpdateAssetTier:
    discriminator: typing.ClassVar = 33
    kind: typing.ClassVar = "UpdateAssetTier"

    @classmethod
    def to_json(cls) -> UpdateAssetTierJSON:
        return UpdateAssetTierJSON(
            kind="UpdateAssetTier",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateAssetTier": {},
        }


@dataclass
class UpdateElevationGroup:
    discriminator: typing.ClassVar = 34
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
class DeleveragingThresholdSlotsPerBps:
    discriminator: typing.ClassVar = 35
    kind: typing.ClassVar = "DeleveragingThresholdSlotsPerBps"

    @classmethod
    def to_json(cls) -> DeleveragingThresholdSlotsPerBpsJSON:
        return DeleveragingThresholdSlotsPerBpsJSON(
            kind="DeleveragingThresholdSlotsPerBps",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "DeleveragingThresholdSlotsPerBps": {},
        }


@dataclass
class UpdateMultiplierSideBoost:
    discriminator: typing.ClassVar = 36
    kind: typing.ClassVar = "UpdateMultiplierSideBoost"

    @classmethod
    def to_json(cls) -> UpdateMultiplierSideBoostJSON:
        return UpdateMultiplierSideBoostJSON(
            kind="UpdateMultiplierSideBoost",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMultiplierSideBoost": {},
        }


@dataclass
class UpdateMultiplierTagBoost:
    discriminator: typing.ClassVar = 37
    kind: typing.ClassVar = "UpdateMultiplierTagBoost"

    @classmethod
    def to_json(cls) -> UpdateMultiplierTagBoostJSON:
        return UpdateMultiplierTagBoostJSON(
            kind="UpdateMultiplierTagBoost",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateMultiplierTagBoost": {},
        }


@dataclass
class UpdateReserveStatus:
    discriminator: typing.ClassVar = 38
    kind: typing.ClassVar = "UpdateReserveStatus"

    @classmethod
    def to_json(cls) -> UpdateReserveStatusJSON:
        return UpdateReserveStatusJSON(
            kind="UpdateReserveStatus",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "UpdateReserveStatus": {},
        }


UpdateConfigModeKind = typing.Union[
    UpdateLoanToValuePct,
    UpdateMaxLiquidationBonusBps,
    UpdateLiquidationThresholdPct,
    UpdateProtocolLiquidationFee,
    UpdateProtocolTakeRate,
    UpdateFeesBorrowFee,
    UpdateFeesFlashLoanFee,
    UpdateFeesReferralFeeBps,
    UpdateDepositLimit,
    UpdateBorrowLimit,
    UpdateTokenInfoLowerHeuristic,
    UpdateTokenInfoUpperHeuristic,
    UpdateTokenInfoExpHeuristic,
    UpdateTokenInfoTwapDivergence,
    UpdateTokenInfoScopeTwap,
    UpdateTokenInfoScopeChain,
    UpdateTokenInfoName,
    UpdateTokenInfoPriceMaxAge,
    UpdateTokenInfoTwapMaxAge,
    UpdateScopePriceFeed,
    UpdatePythPrice,
    UpdateSwitchboardFeed,
    UpdateSwitchboardTwapFeed,
    UpdateBorrowRateCurve,
    UpdateEntireReserveConfig,
    UpdateDebtWithdrawalCap,
    UpdateDepositWithdrawalCap,
    UpdateDebtWithdrawalCapCurrentTotal,
    UpdateDepositWithdrawalCapCurrentTotal,
    UpdateBadDebtLiquidationBonusBps,
    UpdateMinLiquidationBonusBps,
    DeleveragingMarginCallPeriod,
    UpdateBorrowFactor,
    UpdateAssetTier,
    UpdateElevationGroup,
    DeleveragingThresholdSlotsPerBps,
    UpdateMultiplierSideBoost,
    UpdateMultiplierTagBoost,
    UpdateReserveStatus,
]
UpdateConfigModeJSON = typing.Union[
    UpdateLoanToValuePctJSON,
    UpdateMaxLiquidationBonusBpsJSON,
    UpdateLiquidationThresholdPctJSON,
    UpdateProtocolLiquidationFeeJSON,
    UpdateProtocolTakeRateJSON,
    UpdateFeesBorrowFeeJSON,
    UpdateFeesFlashLoanFeeJSON,
    UpdateFeesReferralFeeBpsJSON,
    UpdateDepositLimitJSON,
    UpdateBorrowLimitJSON,
    UpdateTokenInfoLowerHeuristicJSON,
    UpdateTokenInfoUpperHeuristicJSON,
    UpdateTokenInfoExpHeuristicJSON,
    UpdateTokenInfoTwapDivergenceJSON,
    UpdateTokenInfoScopeTwapJSON,
    UpdateTokenInfoScopeChainJSON,
    UpdateTokenInfoNameJSON,
    UpdateTokenInfoPriceMaxAgeJSON,
    UpdateTokenInfoTwapMaxAgeJSON,
    UpdateScopePriceFeedJSON,
    UpdatePythPriceJSON,
    UpdateSwitchboardFeedJSON,
    UpdateSwitchboardTwapFeedJSON,
    UpdateBorrowRateCurveJSON,
    UpdateEntireReserveConfigJSON,
    UpdateDebtWithdrawalCapJSON,
    UpdateDepositWithdrawalCapJSON,
    UpdateDebtWithdrawalCapCurrentTotalJSON,
    UpdateDepositWithdrawalCapCurrentTotalJSON,
    UpdateBadDebtLiquidationBonusBpsJSON,
    UpdateMinLiquidationBonusBpsJSON,
    DeleveragingMarginCallPeriodJSON,
    UpdateBorrowFactorJSON,
    UpdateAssetTierJSON,
    UpdateElevationGroupJSON,
    DeleveragingThresholdSlotsPerBpsJSON,
    UpdateMultiplierSideBoostJSON,
    UpdateMultiplierTagBoostJSON,
    UpdateReserveStatusJSON,
]


def from_decoded(obj: dict) -> UpdateConfigModeKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "UpdateLoanToValuePct" in obj:
        return UpdateLoanToValuePct()
    if "UpdateMaxLiquidationBonusBps" in obj:
        return UpdateMaxLiquidationBonusBps()
    if "UpdateLiquidationThresholdPct" in obj:
        return UpdateLiquidationThresholdPct()
    if "UpdateProtocolLiquidationFee" in obj:
        return UpdateProtocolLiquidationFee()
    if "UpdateProtocolTakeRate" in obj:
        return UpdateProtocolTakeRate()
    if "UpdateFeesBorrowFee" in obj:
        return UpdateFeesBorrowFee()
    if "UpdateFeesFlashLoanFee" in obj:
        return UpdateFeesFlashLoanFee()
    if "UpdateFeesReferralFeeBps" in obj:
        return UpdateFeesReferralFeeBps()
    if "UpdateDepositLimit" in obj:
        return UpdateDepositLimit()
    if "UpdateBorrowLimit" in obj:
        return UpdateBorrowLimit()
    if "UpdateTokenInfoLowerHeuristic" in obj:
        return UpdateTokenInfoLowerHeuristic()
    if "UpdateTokenInfoUpperHeuristic" in obj:
        return UpdateTokenInfoUpperHeuristic()
    if "UpdateTokenInfoExpHeuristic" in obj:
        return UpdateTokenInfoExpHeuristic()
    if "UpdateTokenInfoTwapDivergence" in obj:
        return UpdateTokenInfoTwapDivergence()
    if "UpdateTokenInfoScopeTwap" in obj:
        return UpdateTokenInfoScopeTwap()
    if "UpdateTokenInfoScopeChain" in obj:
        return UpdateTokenInfoScopeChain()
    if "UpdateTokenInfoName" in obj:
        return UpdateTokenInfoName()
    if "UpdateTokenInfoPriceMaxAge" in obj:
        return UpdateTokenInfoPriceMaxAge()
    if "UpdateTokenInfoTwapMaxAge" in obj:
        return UpdateTokenInfoTwapMaxAge()
    if "UpdateScopePriceFeed" in obj:
        return UpdateScopePriceFeed()
    if "UpdatePythPrice" in obj:
        return UpdatePythPrice()
    if "UpdateSwitchboardFeed" in obj:
        return UpdateSwitchboardFeed()
    if "UpdateSwitchboardTwapFeed" in obj:
        return UpdateSwitchboardTwapFeed()
    if "UpdateBorrowRateCurve" in obj:
        return UpdateBorrowRateCurve()
    if "UpdateEntireReserveConfig" in obj:
        return UpdateEntireReserveConfig()
    if "UpdateDebtWithdrawalCap" in obj:
        return UpdateDebtWithdrawalCap()
    if "UpdateDepositWithdrawalCap" in obj:
        return UpdateDepositWithdrawalCap()
    if "UpdateDebtWithdrawalCapCurrentTotal" in obj:
        return UpdateDebtWithdrawalCapCurrentTotal()
    if "UpdateDepositWithdrawalCapCurrentTotal" in obj:
        return UpdateDepositWithdrawalCapCurrentTotal()
    if "UpdateBadDebtLiquidationBonusBps" in obj:
        return UpdateBadDebtLiquidationBonusBps()
    if "UpdateMinLiquidationBonusBps" in obj:
        return UpdateMinLiquidationBonusBps()
    if "DeleveragingMarginCallPeriod" in obj:
        return DeleveragingMarginCallPeriod()
    if "UpdateBorrowFactor" in obj:
        return UpdateBorrowFactor()
    if "UpdateAssetTier" in obj:
        return UpdateAssetTier()
    if "UpdateElevationGroup" in obj:
        return UpdateElevationGroup()
    if "DeleveragingThresholdSlotsPerBps" in obj:
        return DeleveragingThresholdSlotsPerBps()
    if "UpdateMultiplierSideBoost" in obj:
        return UpdateMultiplierSideBoost()
    if "UpdateMultiplierTagBoost" in obj:
        return UpdateMultiplierTagBoost()
    if "UpdateReserveStatus" in obj:
        return UpdateReserveStatus()
    raise ValueError("Invalid enum object")


def from_json(obj: UpdateConfigModeJSON) -> UpdateConfigModeKind:
    if obj["kind"] == "UpdateLoanToValuePct":
        return UpdateLoanToValuePct()
    if obj["kind"] == "UpdateMaxLiquidationBonusBps":
        return UpdateMaxLiquidationBonusBps()
    if obj["kind"] == "UpdateLiquidationThresholdPct":
        return UpdateLiquidationThresholdPct()
    if obj["kind"] == "UpdateProtocolLiquidationFee":
        return UpdateProtocolLiquidationFee()
    if obj["kind"] == "UpdateProtocolTakeRate":
        return UpdateProtocolTakeRate()
    if obj["kind"] == "UpdateFeesBorrowFee":
        return UpdateFeesBorrowFee()
    if obj["kind"] == "UpdateFeesFlashLoanFee":
        return UpdateFeesFlashLoanFee()
    if obj["kind"] == "UpdateFeesReferralFeeBps":
        return UpdateFeesReferralFeeBps()
    if obj["kind"] == "UpdateDepositLimit":
        return UpdateDepositLimit()
    if obj["kind"] == "UpdateBorrowLimit":
        return UpdateBorrowLimit()
    if obj["kind"] == "UpdateTokenInfoLowerHeuristic":
        return UpdateTokenInfoLowerHeuristic()
    if obj["kind"] == "UpdateTokenInfoUpperHeuristic":
        return UpdateTokenInfoUpperHeuristic()
    if obj["kind"] == "UpdateTokenInfoExpHeuristic":
        return UpdateTokenInfoExpHeuristic()
    if obj["kind"] == "UpdateTokenInfoTwapDivergence":
        return UpdateTokenInfoTwapDivergence()
    if obj["kind"] == "UpdateTokenInfoScopeTwap":
        return UpdateTokenInfoScopeTwap()
    if obj["kind"] == "UpdateTokenInfoScopeChain":
        return UpdateTokenInfoScopeChain()
    if obj["kind"] == "UpdateTokenInfoName":
        return UpdateTokenInfoName()
    if obj["kind"] == "UpdateTokenInfoPriceMaxAge":
        return UpdateTokenInfoPriceMaxAge()
    if obj["kind"] == "UpdateTokenInfoTwapMaxAge":
        return UpdateTokenInfoTwapMaxAge()
    if obj["kind"] == "UpdateScopePriceFeed":
        return UpdateScopePriceFeed()
    if obj["kind"] == "UpdatePythPrice":
        return UpdatePythPrice()
    if obj["kind"] == "UpdateSwitchboardFeed":
        return UpdateSwitchboardFeed()
    if obj["kind"] == "UpdateSwitchboardTwapFeed":
        return UpdateSwitchboardTwapFeed()
    if obj["kind"] == "UpdateBorrowRateCurve":
        return UpdateBorrowRateCurve()
    if obj["kind"] == "UpdateEntireReserveConfig":
        return UpdateEntireReserveConfig()
    if obj["kind"] == "UpdateDebtWithdrawalCap":
        return UpdateDebtWithdrawalCap()
    if obj["kind"] == "UpdateDepositWithdrawalCap":
        return UpdateDepositWithdrawalCap()
    if obj["kind"] == "UpdateDebtWithdrawalCapCurrentTotal":
        return UpdateDebtWithdrawalCapCurrentTotal()
    if obj["kind"] == "UpdateDepositWithdrawalCapCurrentTotal":
        return UpdateDepositWithdrawalCapCurrentTotal()
    if obj["kind"] == "UpdateBadDebtLiquidationBonusBps":
        return UpdateBadDebtLiquidationBonusBps()
    if obj["kind"] == "UpdateMinLiquidationBonusBps":
        return UpdateMinLiquidationBonusBps()
    if obj["kind"] == "DeleveragingMarginCallPeriod":
        return DeleveragingMarginCallPeriod()
    if obj["kind"] == "UpdateBorrowFactor":
        return UpdateBorrowFactor()
    if obj["kind"] == "UpdateAssetTier":
        return UpdateAssetTier()
    if obj["kind"] == "UpdateElevationGroup":
        return UpdateElevationGroup()
    if obj["kind"] == "DeleveragingThresholdSlotsPerBps":
        return DeleveragingThresholdSlotsPerBps()
    if obj["kind"] == "UpdateMultiplierSideBoost":
        return UpdateMultiplierSideBoost()
    if obj["kind"] == "UpdateMultiplierTagBoost":
        return UpdateMultiplierTagBoost()
    if obj["kind"] == "UpdateReserveStatus":
        return UpdateReserveStatus()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "UpdateLoanToValuePct" / borsh.CStruct(),
    "UpdateMaxLiquidationBonusBps" / borsh.CStruct(),
    "UpdateLiquidationThresholdPct" / borsh.CStruct(),
    "UpdateProtocolLiquidationFee" / borsh.CStruct(),
    "UpdateProtocolTakeRate" / borsh.CStruct(),
    "UpdateFeesBorrowFee" / borsh.CStruct(),
    "UpdateFeesFlashLoanFee" / borsh.CStruct(),
    "UpdateFeesReferralFeeBps" / borsh.CStruct(),
    "UpdateDepositLimit" / borsh.CStruct(),
    "UpdateBorrowLimit" / borsh.CStruct(),
    "UpdateTokenInfoLowerHeuristic" / borsh.CStruct(),
    "UpdateTokenInfoUpperHeuristic" / borsh.CStruct(),
    "UpdateTokenInfoExpHeuristic" / borsh.CStruct(),
    "UpdateTokenInfoTwapDivergence" / borsh.CStruct(),
    "UpdateTokenInfoScopeTwap" / borsh.CStruct(),
    "UpdateTokenInfoScopeChain" / borsh.CStruct(),
    "UpdateTokenInfoName" / borsh.CStruct(),
    "UpdateTokenInfoPriceMaxAge" / borsh.CStruct(),
    "UpdateTokenInfoTwapMaxAge" / borsh.CStruct(),
    "UpdateScopePriceFeed" / borsh.CStruct(),
    "UpdatePythPrice" / borsh.CStruct(),
    "UpdateSwitchboardFeed" / borsh.CStruct(),
    "UpdateSwitchboardTwapFeed" / borsh.CStruct(),
    "UpdateBorrowRateCurve" / borsh.CStruct(),
    "UpdateEntireReserveConfig" / borsh.CStruct(),
    "UpdateDebtWithdrawalCap" / borsh.CStruct(),
    "UpdateDepositWithdrawalCap" / borsh.CStruct(),
    "UpdateDebtWithdrawalCapCurrentTotal" / borsh.CStruct(),
    "UpdateDepositWithdrawalCapCurrentTotal" / borsh.CStruct(),
    "UpdateBadDebtLiquidationBonusBps" / borsh.CStruct(),
    "UpdateMinLiquidationBonusBps" / borsh.CStruct(),
    "DeleveragingMarginCallPeriod" / borsh.CStruct(),
    "UpdateBorrowFactor" / borsh.CStruct(),
    "UpdateAssetTier" / borsh.CStruct(),
    "UpdateElevationGroup" / borsh.CStruct(),
    "DeleveragingThresholdSlotsPerBps" / borsh.CStruct(),
    "UpdateMultiplierSideBoost" / borsh.CStruct(),
    "UpdateMultiplierTagBoost" / borsh.CStruct(),
    "UpdateReserveStatus" / borsh.CStruct(),
)
