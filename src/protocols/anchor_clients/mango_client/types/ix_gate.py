from __future__ import annotations
import typing
from dataclasses import dataclass
from anchorpy.borsh_extension import EnumForCodegen
import borsh_construct as borsh


class AccountCloseJSON(typing.TypedDict):
    kind: typing.Literal["AccountClose"]


class AccountCreateJSON(typing.TypedDict):
    kind: typing.Literal["AccountCreate"]


class AccountEditJSON(typing.TypedDict):
    kind: typing.Literal["AccountEdit"]


class AccountExpandJSON(typing.TypedDict):
    kind: typing.Literal["AccountExpand"]


class AccountToggleFreezeJSON(typing.TypedDict):
    kind: typing.Literal["AccountToggleFreeze"]


class AltExtendJSON(typing.TypedDict):
    kind: typing.Literal["AltExtend"]


class AltSetJSON(typing.TypedDict):
    kind: typing.Literal["AltSet"]


class FlashLoanJSON(typing.TypedDict):
    kind: typing.Literal["FlashLoan"]


class GroupCloseJSON(typing.TypedDict):
    kind: typing.Literal["GroupClose"]


class GroupCreateJSON(typing.TypedDict):
    kind: typing.Literal["GroupCreate"]


class HealthRegionJSON(typing.TypedDict):
    kind: typing.Literal["HealthRegion"]


class PerpCancelAllOrdersJSON(typing.TypedDict):
    kind: typing.Literal["PerpCancelAllOrders"]


class PerpCancelAllOrdersBySideJSON(typing.TypedDict):
    kind: typing.Literal["PerpCancelAllOrdersBySide"]


class PerpCancelOrderJSON(typing.TypedDict):
    kind: typing.Literal["PerpCancelOrder"]


class PerpCancelOrderByClientOrderIdJSON(typing.TypedDict):
    kind: typing.Literal["PerpCancelOrderByClientOrderId"]


class PerpCloseMarketJSON(typing.TypedDict):
    kind: typing.Literal["PerpCloseMarket"]


class PerpConsumeEventsJSON(typing.TypedDict):
    kind: typing.Literal["PerpConsumeEvents"]


class PerpCreateMarketJSON(typing.TypedDict):
    kind: typing.Literal["PerpCreateMarket"]


class PerpDeactivatePositionJSON(typing.TypedDict):
    kind: typing.Literal["PerpDeactivatePosition"]


class PerpLiqBaseOrPositivePnlJSON(typing.TypedDict):
    kind: typing.Literal["PerpLiqBaseOrPositivePnl"]


class PerpLiqForceCancelOrdersJSON(typing.TypedDict):
    kind: typing.Literal["PerpLiqForceCancelOrders"]


class PerpLiqNegativePnlOrBankruptcyJSON(typing.TypedDict):
    kind: typing.Literal["PerpLiqNegativePnlOrBankruptcy"]


class PerpPlaceOrderJSON(typing.TypedDict):
    kind: typing.Literal["PerpPlaceOrder"]


class PerpSettleFeesJSON(typing.TypedDict):
    kind: typing.Literal["PerpSettleFees"]


class PerpSettlePnlJSON(typing.TypedDict):
    kind: typing.Literal["PerpSettlePnl"]


class PerpUpdateFundingJSON(typing.TypedDict):
    kind: typing.Literal["PerpUpdateFunding"]


class Serum3CancelAllOrdersJSON(typing.TypedDict):
    kind: typing.Literal["Serum3CancelAllOrders"]


class Serum3CancelOrderJSON(typing.TypedDict):
    kind: typing.Literal["Serum3CancelOrder"]


class Serum3CloseOpenOrdersJSON(typing.TypedDict):
    kind: typing.Literal["Serum3CloseOpenOrders"]


class Serum3CreateOpenOrdersJSON(typing.TypedDict):
    kind: typing.Literal["Serum3CreateOpenOrders"]


class Serum3DeregisterMarketJSON(typing.TypedDict):
    kind: typing.Literal["Serum3DeregisterMarket"]


class Serum3EditMarketJSON(typing.TypedDict):
    kind: typing.Literal["Serum3EditMarket"]


class Serum3LiqForceCancelOrdersJSON(typing.TypedDict):
    kind: typing.Literal["Serum3LiqForceCancelOrders"]


class Serum3PlaceOrderJSON(typing.TypedDict):
    kind: typing.Literal["Serum3PlaceOrder"]


class Serum3RegisterMarketJSON(typing.TypedDict):
    kind: typing.Literal["Serum3RegisterMarket"]


class Serum3SettleFundsJSON(typing.TypedDict):
    kind: typing.Literal["Serum3SettleFunds"]


class StubOracleCloseJSON(typing.TypedDict):
    kind: typing.Literal["StubOracleClose"]


class StubOracleCreateJSON(typing.TypedDict):
    kind: typing.Literal["StubOracleCreate"]


class StubOracleSetJSON(typing.TypedDict):
    kind: typing.Literal["StubOracleSet"]


class TokenAddBankJSON(typing.TypedDict):
    kind: typing.Literal["TokenAddBank"]


class TokenDepositJSON(typing.TypedDict):
    kind: typing.Literal["TokenDeposit"]


class TokenDeregisterJSON(typing.TypedDict):
    kind: typing.Literal["TokenDeregister"]


class TokenLiqBankruptcyJSON(typing.TypedDict):
    kind: typing.Literal["TokenLiqBankruptcy"]


class TokenLiqWithTokenJSON(typing.TypedDict):
    kind: typing.Literal["TokenLiqWithToken"]


class TokenRegisterJSON(typing.TypedDict):
    kind: typing.Literal["TokenRegister"]


class TokenRegisterTrustlessJSON(typing.TypedDict):
    kind: typing.Literal["TokenRegisterTrustless"]


class TokenUpdateIndexAndRateJSON(typing.TypedDict):
    kind: typing.Literal["TokenUpdateIndexAndRate"]


class TokenWithdrawJSON(typing.TypedDict):
    kind: typing.Literal["TokenWithdraw"]


class AccountBuybackFeesWithMngoJSON(typing.TypedDict):
    kind: typing.Literal["AccountBuybackFeesWithMngo"]


class TokenForceCloseBorrowsWithTokenJSON(typing.TypedDict):
    kind: typing.Literal["TokenForceCloseBorrowsWithToken"]


class PerpForceClosePositionJSON(typing.TypedDict):
    kind: typing.Literal["PerpForceClosePosition"]


class GroupWithdrawInsuranceFundJSON(typing.TypedDict):
    kind: typing.Literal["GroupWithdrawInsuranceFund"]


class TokenConditionalSwapCreateJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapCreate"]


class TokenConditionalSwapTriggerJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapTrigger"]


class TokenConditionalSwapCancelJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapCancel"]


class OpenbookV2CancelOrderJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2CancelOrder"]


class OpenbookV2CloseOpenOrdersJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2CloseOpenOrders"]


class OpenbookV2CreateOpenOrdersJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2CreateOpenOrders"]


class OpenbookV2DeregisterMarketJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2DeregisterMarket"]


class OpenbookV2EditMarketJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2EditMarket"]


class OpenbookV2LiqForceCancelOrdersJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2LiqForceCancelOrders"]


class OpenbookV2PlaceOrderJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2PlaceOrder"]


class OpenbookV2PlaceTakeOrderJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2PlaceTakeOrder"]


class OpenbookV2RegisterMarketJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2RegisterMarket"]


class OpenbookV2SettleFundsJSON(typing.TypedDict):
    kind: typing.Literal["OpenbookV2SettleFunds"]


class AdminTokenWithdrawFeesJSON(typing.TypedDict):
    kind: typing.Literal["AdminTokenWithdrawFees"]


class AdminPerpWithdrawFeesJSON(typing.TypedDict):
    kind: typing.Literal["AdminPerpWithdrawFees"]


class AccountSizeMigrationJSON(typing.TypedDict):
    kind: typing.Literal["AccountSizeMigration"]


class TokenConditionalSwapStartJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapStart"]


class TokenConditionalSwapCreatePremiumAuctionJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapCreatePremiumAuction"]


class TokenConditionalSwapCreateLinearAuctionJSON(typing.TypedDict):
    kind: typing.Literal["TokenConditionalSwapCreateLinearAuction"]


class Serum3PlaceOrderV2JSON(typing.TypedDict):
    kind: typing.Literal["Serum3PlaceOrderV2"]


class TokenForceWithdrawJSON(typing.TypedDict):
    kind: typing.Literal["TokenForceWithdraw"]


@dataclass
class AccountClose:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "AccountClose"

    @classmethod
    def to_json(cls) -> AccountCloseJSON:
        return AccountCloseJSON(
            kind="AccountClose",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountClose": {},
        }


@dataclass
class AccountCreate:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "AccountCreate"

    @classmethod
    def to_json(cls) -> AccountCreateJSON:
        return AccountCreateJSON(
            kind="AccountCreate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountCreate": {},
        }


@dataclass
class AccountEdit:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "AccountEdit"

    @classmethod
    def to_json(cls) -> AccountEditJSON:
        return AccountEditJSON(
            kind="AccountEdit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountEdit": {},
        }


@dataclass
class AccountExpand:
    discriminator: typing.ClassVar = 3
    kind: typing.ClassVar = "AccountExpand"

    @classmethod
    def to_json(cls) -> AccountExpandJSON:
        return AccountExpandJSON(
            kind="AccountExpand",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountExpand": {},
        }


@dataclass
class AccountToggleFreeze:
    discriminator: typing.ClassVar = 4
    kind: typing.ClassVar = "AccountToggleFreeze"

    @classmethod
    def to_json(cls) -> AccountToggleFreezeJSON:
        return AccountToggleFreezeJSON(
            kind="AccountToggleFreeze",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountToggleFreeze": {},
        }


@dataclass
class AltExtend:
    discriminator: typing.ClassVar = 5
    kind: typing.ClassVar = "AltExtend"

    @classmethod
    def to_json(cls) -> AltExtendJSON:
        return AltExtendJSON(
            kind="AltExtend",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AltExtend": {},
        }


@dataclass
class AltSet:
    discriminator: typing.ClassVar = 6
    kind: typing.ClassVar = "AltSet"

    @classmethod
    def to_json(cls) -> AltSetJSON:
        return AltSetJSON(
            kind="AltSet",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AltSet": {},
        }


@dataclass
class FlashLoan:
    discriminator: typing.ClassVar = 7
    kind: typing.ClassVar = "FlashLoan"

    @classmethod
    def to_json(cls) -> FlashLoanJSON:
        return FlashLoanJSON(
            kind="FlashLoan",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "FlashLoan": {},
        }


@dataclass
class GroupClose:
    discriminator: typing.ClassVar = 8
    kind: typing.ClassVar = "GroupClose"

    @classmethod
    def to_json(cls) -> GroupCloseJSON:
        return GroupCloseJSON(
            kind="GroupClose",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "GroupClose": {},
        }


@dataclass
class GroupCreate:
    discriminator: typing.ClassVar = 9
    kind: typing.ClassVar = "GroupCreate"

    @classmethod
    def to_json(cls) -> GroupCreateJSON:
        return GroupCreateJSON(
            kind="GroupCreate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "GroupCreate": {},
        }


@dataclass
class HealthRegion:
    discriminator: typing.ClassVar = 10
    kind: typing.ClassVar = "HealthRegion"

    @classmethod
    def to_json(cls) -> HealthRegionJSON:
        return HealthRegionJSON(
            kind="HealthRegion",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "HealthRegion": {},
        }


@dataclass
class PerpCancelAllOrders:
    discriminator: typing.ClassVar = 11
    kind: typing.ClassVar = "PerpCancelAllOrders"

    @classmethod
    def to_json(cls) -> PerpCancelAllOrdersJSON:
        return PerpCancelAllOrdersJSON(
            kind="PerpCancelAllOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCancelAllOrders": {},
        }


@dataclass
class PerpCancelAllOrdersBySide:
    discriminator: typing.ClassVar = 12
    kind: typing.ClassVar = "PerpCancelAllOrdersBySide"

    @classmethod
    def to_json(cls) -> PerpCancelAllOrdersBySideJSON:
        return PerpCancelAllOrdersBySideJSON(
            kind="PerpCancelAllOrdersBySide",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCancelAllOrdersBySide": {},
        }


@dataclass
class PerpCancelOrder:
    discriminator: typing.ClassVar = 13
    kind: typing.ClassVar = "PerpCancelOrder"

    @classmethod
    def to_json(cls) -> PerpCancelOrderJSON:
        return PerpCancelOrderJSON(
            kind="PerpCancelOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCancelOrder": {},
        }


@dataclass
class PerpCancelOrderByClientOrderId:
    discriminator: typing.ClassVar = 14
    kind: typing.ClassVar = "PerpCancelOrderByClientOrderId"

    @classmethod
    def to_json(cls) -> PerpCancelOrderByClientOrderIdJSON:
        return PerpCancelOrderByClientOrderIdJSON(
            kind="PerpCancelOrderByClientOrderId",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCancelOrderByClientOrderId": {},
        }


@dataclass
class PerpCloseMarket:
    discriminator: typing.ClassVar = 15
    kind: typing.ClassVar = "PerpCloseMarket"

    @classmethod
    def to_json(cls) -> PerpCloseMarketJSON:
        return PerpCloseMarketJSON(
            kind="PerpCloseMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCloseMarket": {},
        }


@dataclass
class PerpConsumeEvents:
    discriminator: typing.ClassVar = 16
    kind: typing.ClassVar = "PerpConsumeEvents"

    @classmethod
    def to_json(cls) -> PerpConsumeEventsJSON:
        return PerpConsumeEventsJSON(
            kind="PerpConsumeEvents",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpConsumeEvents": {},
        }


@dataclass
class PerpCreateMarket:
    discriminator: typing.ClassVar = 17
    kind: typing.ClassVar = "PerpCreateMarket"

    @classmethod
    def to_json(cls) -> PerpCreateMarketJSON:
        return PerpCreateMarketJSON(
            kind="PerpCreateMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpCreateMarket": {},
        }


@dataclass
class PerpDeactivatePosition:
    discriminator: typing.ClassVar = 18
    kind: typing.ClassVar = "PerpDeactivatePosition"

    @classmethod
    def to_json(cls) -> PerpDeactivatePositionJSON:
        return PerpDeactivatePositionJSON(
            kind="PerpDeactivatePosition",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpDeactivatePosition": {},
        }


@dataclass
class PerpLiqBaseOrPositivePnl:
    discriminator: typing.ClassVar = 19
    kind: typing.ClassVar = "PerpLiqBaseOrPositivePnl"

    @classmethod
    def to_json(cls) -> PerpLiqBaseOrPositivePnlJSON:
        return PerpLiqBaseOrPositivePnlJSON(
            kind="PerpLiqBaseOrPositivePnl",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpLiqBaseOrPositivePnl": {},
        }


@dataclass
class PerpLiqForceCancelOrders:
    discriminator: typing.ClassVar = 20
    kind: typing.ClassVar = "PerpLiqForceCancelOrders"

    @classmethod
    def to_json(cls) -> PerpLiqForceCancelOrdersJSON:
        return PerpLiqForceCancelOrdersJSON(
            kind="PerpLiqForceCancelOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpLiqForceCancelOrders": {},
        }


@dataclass
class PerpLiqNegativePnlOrBankruptcy:
    discriminator: typing.ClassVar = 21
    kind: typing.ClassVar = "PerpLiqNegativePnlOrBankruptcy"

    @classmethod
    def to_json(cls) -> PerpLiqNegativePnlOrBankruptcyJSON:
        return PerpLiqNegativePnlOrBankruptcyJSON(
            kind="PerpLiqNegativePnlOrBankruptcy",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpLiqNegativePnlOrBankruptcy": {},
        }


@dataclass
class PerpPlaceOrder:
    discriminator: typing.ClassVar = 22
    kind: typing.ClassVar = "PerpPlaceOrder"

    @classmethod
    def to_json(cls) -> PerpPlaceOrderJSON:
        return PerpPlaceOrderJSON(
            kind="PerpPlaceOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpPlaceOrder": {},
        }


@dataclass
class PerpSettleFees:
    discriminator: typing.ClassVar = 23
    kind: typing.ClassVar = "PerpSettleFees"

    @classmethod
    def to_json(cls) -> PerpSettleFeesJSON:
        return PerpSettleFeesJSON(
            kind="PerpSettleFees",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpSettleFees": {},
        }


@dataclass
class PerpSettlePnl:
    discriminator: typing.ClassVar = 24
    kind: typing.ClassVar = "PerpSettlePnl"

    @classmethod
    def to_json(cls) -> PerpSettlePnlJSON:
        return PerpSettlePnlJSON(
            kind="PerpSettlePnl",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpSettlePnl": {},
        }


@dataclass
class PerpUpdateFunding:
    discriminator: typing.ClassVar = 25
    kind: typing.ClassVar = "PerpUpdateFunding"

    @classmethod
    def to_json(cls) -> PerpUpdateFundingJSON:
        return PerpUpdateFundingJSON(
            kind="PerpUpdateFunding",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpUpdateFunding": {},
        }


@dataclass
class Serum3CancelAllOrders:
    discriminator: typing.ClassVar = 26
    kind: typing.ClassVar = "Serum3CancelAllOrders"

    @classmethod
    def to_json(cls) -> Serum3CancelAllOrdersJSON:
        return Serum3CancelAllOrdersJSON(
            kind="Serum3CancelAllOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3CancelAllOrders": {},
        }


@dataclass
class Serum3CancelOrder:
    discriminator: typing.ClassVar = 27
    kind: typing.ClassVar = "Serum3CancelOrder"

    @classmethod
    def to_json(cls) -> Serum3CancelOrderJSON:
        return Serum3CancelOrderJSON(
            kind="Serum3CancelOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3CancelOrder": {},
        }


@dataclass
class Serum3CloseOpenOrders:
    discriminator: typing.ClassVar = 28
    kind: typing.ClassVar = "Serum3CloseOpenOrders"

    @classmethod
    def to_json(cls) -> Serum3CloseOpenOrdersJSON:
        return Serum3CloseOpenOrdersJSON(
            kind="Serum3CloseOpenOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3CloseOpenOrders": {},
        }


@dataclass
class Serum3CreateOpenOrders:
    discriminator: typing.ClassVar = 29
    kind: typing.ClassVar = "Serum3CreateOpenOrders"

    @classmethod
    def to_json(cls) -> Serum3CreateOpenOrdersJSON:
        return Serum3CreateOpenOrdersJSON(
            kind="Serum3CreateOpenOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3CreateOpenOrders": {},
        }


@dataclass
class Serum3DeregisterMarket:
    discriminator: typing.ClassVar = 30
    kind: typing.ClassVar = "Serum3DeregisterMarket"

    @classmethod
    def to_json(cls) -> Serum3DeregisterMarketJSON:
        return Serum3DeregisterMarketJSON(
            kind="Serum3DeregisterMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3DeregisterMarket": {},
        }


@dataclass
class Serum3EditMarket:
    discriminator: typing.ClassVar = 31
    kind: typing.ClassVar = "Serum3EditMarket"

    @classmethod
    def to_json(cls) -> Serum3EditMarketJSON:
        return Serum3EditMarketJSON(
            kind="Serum3EditMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3EditMarket": {},
        }


@dataclass
class Serum3LiqForceCancelOrders:
    discriminator: typing.ClassVar = 32
    kind: typing.ClassVar = "Serum3LiqForceCancelOrders"

    @classmethod
    def to_json(cls) -> Serum3LiqForceCancelOrdersJSON:
        return Serum3LiqForceCancelOrdersJSON(
            kind="Serum3LiqForceCancelOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3LiqForceCancelOrders": {},
        }


@dataclass
class Serum3PlaceOrder:
    discriminator: typing.ClassVar = 33
    kind: typing.ClassVar = "Serum3PlaceOrder"

    @classmethod
    def to_json(cls) -> Serum3PlaceOrderJSON:
        return Serum3PlaceOrderJSON(
            kind="Serum3PlaceOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3PlaceOrder": {},
        }


@dataclass
class Serum3RegisterMarket:
    discriminator: typing.ClassVar = 34
    kind: typing.ClassVar = "Serum3RegisterMarket"

    @classmethod
    def to_json(cls) -> Serum3RegisterMarketJSON:
        return Serum3RegisterMarketJSON(
            kind="Serum3RegisterMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3RegisterMarket": {},
        }


@dataclass
class Serum3SettleFunds:
    discriminator: typing.ClassVar = 35
    kind: typing.ClassVar = "Serum3SettleFunds"

    @classmethod
    def to_json(cls) -> Serum3SettleFundsJSON:
        return Serum3SettleFundsJSON(
            kind="Serum3SettleFunds",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3SettleFunds": {},
        }


@dataclass
class StubOracleClose:
    discriminator: typing.ClassVar = 36
    kind: typing.ClassVar = "StubOracleClose"

    @classmethod
    def to_json(cls) -> StubOracleCloseJSON:
        return StubOracleCloseJSON(
            kind="StubOracleClose",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "StubOracleClose": {},
        }


@dataclass
class StubOracleCreate:
    discriminator: typing.ClassVar = 37
    kind: typing.ClassVar = "StubOracleCreate"

    @classmethod
    def to_json(cls) -> StubOracleCreateJSON:
        return StubOracleCreateJSON(
            kind="StubOracleCreate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "StubOracleCreate": {},
        }


@dataclass
class StubOracleSet:
    discriminator: typing.ClassVar = 38
    kind: typing.ClassVar = "StubOracleSet"

    @classmethod
    def to_json(cls) -> StubOracleSetJSON:
        return StubOracleSetJSON(
            kind="StubOracleSet",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "StubOracleSet": {},
        }


@dataclass
class TokenAddBank:
    discriminator: typing.ClassVar = 39
    kind: typing.ClassVar = "TokenAddBank"

    @classmethod
    def to_json(cls) -> TokenAddBankJSON:
        return TokenAddBankJSON(
            kind="TokenAddBank",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenAddBank": {},
        }


@dataclass
class TokenDeposit:
    discriminator: typing.ClassVar = 40
    kind: typing.ClassVar = "TokenDeposit"

    @classmethod
    def to_json(cls) -> TokenDepositJSON:
        return TokenDepositJSON(
            kind="TokenDeposit",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenDeposit": {},
        }


@dataclass
class TokenDeregister:
    discriminator: typing.ClassVar = 41
    kind: typing.ClassVar = "TokenDeregister"

    @classmethod
    def to_json(cls) -> TokenDeregisterJSON:
        return TokenDeregisterJSON(
            kind="TokenDeregister",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenDeregister": {},
        }


@dataclass
class TokenLiqBankruptcy:
    discriminator: typing.ClassVar = 42
    kind: typing.ClassVar = "TokenLiqBankruptcy"

    @classmethod
    def to_json(cls) -> TokenLiqBankruptcyJSON:
        return TokenLiqBankruptcyJSON(
            kind="TokenLiqBankruptcy",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenLiqBankruptcy": {},
        }


@dataclass
class TokenLiqWithToken:
    discriminator: typing.ClassVar = 43
    kind: typing.ClassVar = "TokenLiqWithToken"

    @classmethod
    def to_json(cls) -> TokenLiqWithTokenJSON:
        return TokenLiqWithTokenJSON(
            kind="TokenLiqWithToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenLiqWithToken": {},
        }


@dataclass
class TokenRegister:
    discriminator: typing.ClassVar = 44
    kind: typing.ClassVar = "TokenRegister"

    @classmethod
    def to_json(cls) -> TokenRegisterJSON:
        return TokenRegisterJSON(
            kind="TokenRegister",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenRegister": {},
        }


@dataclass
class TokenRegisterTrustless:
    discriminator: typing.ClassVar = 45
    kind: typing.ClassVar = "TokenRegisterTrustless"

    @classmethod
    def to_json(cls) -> TokenRegisterTrustlessJSON:
        return TokenRegisterTrustlessJSON(
            kind="TokenRegisterTrustless",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenRegisterTrustless": {},
        }


@dataclass
class TokenUpdateIndexAndRate:
    discriminator: typing.ClassVar = 46
    kind: typing.ClassVar = "TokenUpdateIndexAndRate"

    @classmethod
    def to_json(cls) -> TokenUpdateIndexAndRateJSON:
        return TokenUpdateIndexAndRateJSON(
            kind="TokenUpdateIndexAndRate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenUpdateIndexAndRate": {},
        }


@dataclass
class TokenWithdraw:
    discriminator: typing.ClassVar = 47
    kind: typing.ClassVar = "TokenWithdraw"

    @classmethod
    def to_json(cls) -> TokenWithdrawJSON:
        return TokenWithdrawJSON(
            kind="TokenWithdraw",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenWithdraw": {},
        }


@dataclass
class AccountBuybackFeesWithMngo:
    discriminator: typing.ClassVar = 48
    kind: typing.ClassVar = "AccountBuybackFeesWithMngo"

    @classmethod
    def to_json(cls) -> AccountBuybackFeesWithMngoJSON:
        return AccountBuybackFeesWithMngoJSON(
            kind="AccountBuybackFeesWithMngo",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountBuybackFeesWithMngo": {},
        }


@dataclass
class TokenForceCloseBorrowsWithToken:
    discriminator: typing.ClassVar = 49
    kind: typing.ClassVar = "TokenForceCloseBorrowsWithToken"

    @classmethod
    def to_json(cls) -> TokenForceCloseBorrowsWithTokenJSON:
        return TokenForceCloseBorrowsWithTokenJSON(
            kind="TokenForceCloseBorrowsWithToken",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenForceCloseBorrowsWithToken": {},
        }


@dataclass
class PerpForceClosePosition:
    discriminator: typing.ClassVar = 50
    kind: typing.ClassVar = "PerpForceClosePosition"

    @classmethod
    def to_json(cls) -> PerpForceClosePositionJSON:
        return PerpForceClosePositionJSON(
            kind="PerpForceClosePosition",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "PerpForceClosePosition": {},
        }


@dataclass
class GroupWithdrawInsuranceFund:
    discriminator: typing.ClassVar = 51
    kind: typing.ClassVar = "GroupWithdrawInsuranceFund"

    @classmethod
    def to_json(cls) -> GroupWithdrawInsuranceFundJSON:
        return GroupWithdrawInsuranceFundJSON(
            kind="GroupWithdrawInsuranceFund",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "GroupWithdrawInsuranceFund": {},
        }


@dataclass
class TokenConditionalSwapCreate:
    discriminator: typing.ClassVar = 52
    kind: typing.ClassVar = "TokenConditionalSwapCreate"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapCreateJSON:
        return TokenConditionalSwapCreateJSON(
            kind="TokenConditionalSwapCreate",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapCreate": {},
        }


@dataclass
class TokenConditionalSwapTrigger:
    discriminator: typing.ClassVar = 53
    kind: typing.ClassVar = "TokenConditionalSwapTrigger"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapTriggerJSON:
        return TokenConditionalSwapTriggerJSON(
            kind="TokenConditionalSwapTrigger",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapTrigger": {},
        }


@dataclass
class TokenConditionalSwapCancel:
    discriminator: typing.ClassVar = 54
    kind: typing.ClassVar = "TokenConditionalSwapCancel"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapCancelJSON:
        return TokenConditionalSwapCancelJSON(
            kind="TokenConditionalSwapCancel",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapCancel": {},
        }


@dataclass
class OpenbookV2CancelOrder:
    discriminator: typing.ClassVar = 55
    kind: typing.ClassVar = "OpenbookV2CancelOrder"

    @classmethod
    def to_json(cls) -> OpenbookV2CancelOrderJSON:
        return OpenbookV2CancelOrderJSON(
            kind="OpenbookV2CancelOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2CancelOrder": {},
        }


@dataclass
class OpenbookV2CloseOpenOrders:
    discriminator: typing.ClassVar = 56
    kind: typing.ClassVar = "OpenbookV2CloseOpenOrders"

    @classmethod
    def to_json(cls) -> OpenbookV2CloseOpenOrdersJSON:
        return OpenbookV2CloseOpenOrdersJSON(
            kind="OpenbookV2CloseOpenOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2CloseOpenOrders": {},
        }


@dataclass
class OpenbookV2CreateOpenOrders:
    discriminator: typing.ClassVar = 57
    kind: typing.ClassVar = "OpenbookV2CreateOpenOrders"

    @classmethod
    def to_json(cls) -> OpenbookV2CreateOpenOrdersJSON:
        return OpenbookV2CreateOpenOrdersJSON(
            kind="OpenbookV2CreateOpenOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2CreateOpenOrders": {},
        }


@dataclass
class OpenbookV2DeregisterMarket:
    discriminator: typing.ClassVar = 58
    kind: typing.ClassVar = "OpenbookV2DeregisterMarket"

    @classmethod
    def to_json(cls) -> OpenbookV2DeregisterMarketJSON:
        return OpenbookV2DeregisterMarketJSON(
            kind="OpenbookV2DeregisterMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2DeregisterMarket": {},
        }


@dataclass
class OpenbookV2EditMarket:
    discriminator: typing.ClassVar = 59
    kind: typing.ClassVar = "OpenbookV2EditMarket"

    @classmethod
    def to_json(cls) -> OpenbookV2EditMarketJSON:
        return OpenbookV2EditMarketJSON(
            kind="OpenbookV2EditMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2EditMarket": {},
        }


@dataclass
class OpenbookV2LiqForceCancelOrders:
    discriminator: typing.ClassVar = 60
    kind: typing.ClassVar = "OpenbookV2LiqForceCancelOrders"

    @classmethod
    def to_json(cls) -> OpenbookV2LiqForceCancelOrdersJSON:
        return OpenbookV2LiqForceCancelOrdersJSON(
            kind="OpenbookV2LiqForceCancelOrders",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2LiqForceCancelOrders": {},
        }


@dataclass
class OpenbookV2PlaceOrder:
    discriminator: typing.ClassVar = 61
    kind: typing.ClassVar = "OpenbookV2PlaceOrder"

    @classmethod
    def to_json(cls) -> OpenbookV2PlaceOrderJSON:
        return OpenbookV2PlaceOrderJSON(
            kind="OpenbookV2PlaceOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2PlaceOrder": {},
        }


@dataclass
class OpenbookV2PlaceTakeOrder:
    discriminator: typing.ClassVar = 62
    kind: typing.ClassVar = "OpenbookV2PlaceTakeOrder"

    @classmethod
    def to_json(cls) -> OpenbookV2PlaceTakeOrderJSON:
        return OpenbookV2PlaceTakeOrderJSON(
            kind="OpenbookV2PlaceTakeOrder",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2PlaceTakeOrder": {},
        }


@dataclass
class OpenbookV2RegisterMarket:
    discriminator: typing.ClassVar = 63
    kind: typing.ClassVar = "OpenbookV2RegisterMarket"

    @classmethod
    def to_json(cls) -> OpenbookV2RegisterMarketJSON:
        return OpenbookV2RegisterMarketJSON(
            kind="OpenbookV2RegisterMarket",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2RegisterMarket": {},
        }


@dataclass
class OpenbookV2SettleFunds:
    discriminator: typing.ClassVar = 64
    kind: typing.ClassVar = "OpenbookV2SettleFunds"

    @classmethod
    def to_json(cls) -> OpenbookV2SettleFundsJSON:
        return OpenbookV2SettleFundsJSON(
            kind="OpenbookV2SettleFunds",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "OpenbookV2SettleFunds": {},
        }


@dataclass
class AdminTokenWithdrawFees:
    discriminator: typing.ClassVar = 65
    kind: typing.ClassVar = "AdminTokenWithdrawFees"

    @classmethod
    def to_json(cls) -> AdminTokenWithdrawFeesJSON:
        return AdminTokenWithdrawFeesJSON(
            kind="AdminTokenWithdrawFees",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AdminTokenWithdrawFees": {},
        }


@dataclass
class AdminPerpWithdrawFees:
    discriminator: typing.ClassVar = 66
    kind: typing.ClassVar = "AdminPerpWithdrawFees"

    @classmethod
    def to_json(cls) -> AdminPerpWithdrawFeesJSON:
        return AdminPerpWithdrawFeesJSON(
            kind="AdminPerpWithdrawFees",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AdminPerpWithdrawFees": {},
        }


@dataclass
class AccountSizeMigration:
    discriminator: typing.ClassVar = 67
    kind: typing.ClassVar = "AccountSizeMigration"

    @classmethod
    def to_json(cls) -> AccountSizeMigrationJSON:
        return AccountSizeMigrationJSON(
            kind="AccountSizeMigration",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "AccountSizeMigration": {},
        }


@dataclass
class TokenConditionalSwapStart:
    discriminator: typing.ClassVar = 68
    kind: typing.ClassVar = "TokenConditionalSwapStart"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapStartJSON:
        return TokenConditionalSwapStartJSON(
            kind="TokenConditionalSwapStart",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapStart": {},
        }


@dataclass
class TokenConditionalSwapCreatePremiumAuction:
    discriminator: typing.ClassVar = 69
    kind: typing.ClassVar = "TokenConditionalSwapCreatePremiumAuction"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapCreatePremiumAuctionJSON:
        return TokenConditionalSwapCreatePremiumAuctionJSON(
            kind="TokenConditionalSwapCreatePremiumAuction",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapCreatePremiumAuction": {},
        }


@dataclass
class TokenConditionalSwapCreateLinearAuction:
    discriminator: typing.ClassVar = 70
    kind: typing.ClassVar = "TokenConditionalSwapCreateLinearAuction"

    @classmethod
    def to_json(cls) -> TokenConditionalSwapCreateLinearAuctionJSON:
        return TokenConditionalSwapCreateLinearAuctionJSON(
            kind="TokenConditionalSwapCreateLinearAuction",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenConditionalSwapCreateLinearAuction": {},
        }


@dataclass
class Serum3PlaceOrderV2:
    discriminator: typing.ClassVar = 71
    kind: typing.ClassVar = "Serum3PlaceOrderV2"

    @classmethod
    def to_json(cls) -> Serum3PlaceOrderV2JSON:
        return Serum3PlaceOrderV2JSON(
            kind="Serum3PlaceOrderV2",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Serum3PlaceOrderV2": {},
        }


@dataclass
class TokenForceWithdraw:
    discriminator: typing.ClassVar = 72
    kind: typing.ClassVar = "TokenForceWithdraw"

    @classmethod
    def to_json(cls) -> TokenForceWithdrawJSON:
        return TokenForceWithdrawJSON(
            kind="TokenForceWithdraw",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "TokenForceWithdraw": {},
        }


IxGateKind = typing.Union[
    AccountClose,
    AccountCreate,
    AccountEdit,
    AccountExpand,
    AccountToggleFreeze,
    AltExtend,
    AltSet,
    FlashLoan,
    GroupClose,
    GroupCreate,
    HealthRegion,
    PerpCancelAllOrders,
    PerpCancelAllOrdersBySide,
    PerpCancelOrder,
    PerpCancelOrderByClientOrderId,
    PerpCloseMarket,
    PerpConsumeEvents,
    PerpCreateMarket,
    PerpDeactivatePosition,
    PerpLiqBaseOrPositivePnl,
    PerpLiqForceCancelOrders,
    PerpLiqNegativePnlOrBankruptcy,
    PerpPlaceOrder,
    PerpSettleFees,
    PerpSettlePnl,
    PerpUpdateFunding,
    Serum3CancelAllOrders,
    Serum3CancelOrder,
    Serum3CloseOpenOrders,
    Serum3CreateOpenOrders,
    Serum3DeregisterMarket,
    Serum3EditMarket,
    Serum3LiqForceCancelOrders,
    Serum3PlaceOrder,
    Serum3RegisterMarket,
    Serum3SettleFunds,
    StubOracleClose,
    StubOracleCreate,
    StubOracleSet,
    TokenAddBank,
    TokenDeposit,
    TokenDeregister,
    TokenLiqBankruptcy,
    TokenLiqWithToken,
    TokenRegister,
    TokenRegisterTrustless,
    TokenUpdateIndexAndRate,
    TokenWithdraw,
    AccountBuybackFeesWithMngo,
    TokenForceCloseBorrowsWithToken,
    PerpForceClosePosition,
    GroupWithdrawInsuranceFund,
    TokenConditionalSwapCreate,
    TokenConditionalSwapTrigger,
    TokenConditionalSwapCancel,
    OpenbookV2CancelOrder,
    OpenbookV2CloseOpenOrders,
    OpenbookV2CreateOpenOrders,
    OpenbookV2DeregisterMarket,
    OpenbookV2EditMarket,
    OpenbookV2LiqForceCancelOrders,
    OpenbookV2PlaceOrder,
    OpenbookV2PlaceTakeOrder,
    OpenbookV2RegisterMarket,
    OpenbookV2SettleFunds,
    AdminTokenWithdrawFees,
    AdminPerpWithdrawFees,
    AccountSizeMigration,
    TokenConditionalSwapStart,
    TokenConditionalSwapCreatePremiumAuction,
    TokenConditionalSwapCreateLinearAuction,
    Serum3PlaceOrderV2,
    TokenForceWithdraw,
]
IxGateJSON = typing.Union[
    AccountCloseJSON,
    AccountCreateJSON,
    AccountEditJSON,
    AccountExpandJSON,
    AccountToggleFreezeJSON,
    AltExtendJSON,
    AltSetJSON,
    FlashLoanJSON,
    GroupCloseJSON,
    GroupCreateJSON,
    HealthRegionJSON,
    PerpCancelAllOrdersJSON,
    PerpCancelAllOrdersBySideJSON,
    PerpCancelOrderJSON,
    PerpCancelOrderByClientOrderIdJSON,
    PerpCloseMarketJSON,
    PerpConsumeEventsJSON,
    PerpCreateMarketJSON,
    PerpDeactivatePositionJSON,
    PerpLiqBaseOrPositivePnlJSON,
    PerpLiqForceCancelOrdersJSON,
    PerpLiqNegativePnlOrBankruptcyJSON,
    PerpPlaceOrderJSON,
    PerpSettleFeesJSON,
    PerpSettlePnlJSON,
    PerpUpdateFundingJSON,
    Serum3CancelAllOrdersJSON,
    Serum3CancelOrderJSON,
    Serum3CloseOpenOrdersJSON,
    Serum3CreateOpenOrdersJSON,
    Serum3DeregisterMarketJSON,
    Serum3EditMarketJSON,
    Serum3LiqForceCancelOrdersJSON,
    Serum3PlaceOrderJSON,
    Serum3RegisterMarketJSON,
    Serum3SettleFundsJSON,
    StubOracleCloseJSON,
    StubOracleCreateJSON,
    StubOracleSetJSON,
    TokenAddBankJSON,
    TokenDepositJSON,
    TokenDeregisterJSON,
    TokenLiqBankruptcyJSON,
    TokenLiqWithTokenJSON,
    TokenRegisterJSON,
    TokenRegisterTrustlessJSON,
    TokenUpdateIndexAndRateJSON,
    TokenWithdrawJSON,
    AccountBuybackFeesWithMngoJSON,
    TokenForceCloseBorrowsWithTokenJSON,
    PerpForceClosePositionJSON,
    GroupWithdrawInsuranceFundJSON,
    TokenConditionalSwapCreateJSON,
    TokenConditionalSwapTriggerJSON,
    TokenConditionalSwapCancelJSON,
    OpenbookV2CancelOrderJSON,
    OpenbookV2CloseOpenOrdersJSON,
    OpenbookV2CreateOpenOrdersJSON,
    OpenbookV2DeregisterMarketJSON,
    OpenbookV2EditMarketJSON,
    OpenbookV2LiqForceCancelOrdersJSON,
    OpenbookV2PlaceOrderJSON,
    OpenbookV2PlaceTakeOrderJSON,
    OpenbookV2RegisterMarketJSON,
    OpenbookV2SettleFundsJSON,
    AdminTokenWithdrawFeesJSON,
    AdminPerpWithdrawFeesJSON,
    AccountSizeMigrationJSON,
    TokenConditionalSwapStartJSON,
    TokenConditionalSwapCreatePremiumAuctionJSON,
    TokenConditionalSwapCreateLinearAuctionJSON,
    Serum3PlaceOrderV2JSON,
    TokenForceWithdrawJSON,
]


def from_decoded(obj: dict) -> IxGateKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "AccountClose" in obj:
        return AccountClose()
    if "AccountCreate" in obj:
        return AccountCreate()
    if "AccountEdit" in obj:
        return AccountEdit()
    if "AccountExpand" in obj:
        return AccountExpand()
    if "AccountToggleFreeze" in obj:
        return AccountToggleFreeze()
    if "AltExtend" in obj:
        return AltExtend()
    if "AltSet" in obj:
        return AltSet()
    if "FlashLoan" in obj:
        return FlashLoan()
    if "GroupClose" in obj:
        return GroupClose()
    if "GroupCreate" in obj:
        return GroupCreate()
    if "HealthRegion" in obj:
        return HealthRegion()
    if "PerpCancelAllOrders" in obj:
        return PerpCancelAllOrders()
    if "PerpCancelAllOrdersBySide" in obj:
        return PerpCancelAllOrdersBySide()
    if "PerpCancelOrder" in obj:
        return PerpCancelOrder()
    if "PerpCancelOrderByClientOrderId" in obj:
        return PerpCancelOrderByClientOrderId()
    if "PerpCloseMarket" in obj:
        return PerpCloseMarket()
    if "PerpConsumeEvents" in obj:
        return PerpConsumeEvents()
    if "PerpCreateMarket" in obj:
        return PerpCreateMarket()
    if "PerpDeactivatePosition" in obj:
        return PerpDeactivatePosition()
    if "PerpLiqBaseOrPositivePnl" in obj:
        return PerpLiqBaseOrPositivePnl()
    if "PerpLiqForceCancelOrders" in obj:
        return PerpLiqForceCancelOrders()
    if "PerpLiqNegativePnlOrBankruptcy" in obj:
        return PerpLiqNegativePnlOrBankruptcy()
    if "PerpPlaceOrder" in obj:
        return PerpPlaceOrder()
    if "PerpSettleFees" in obj:
        return PerpSettleFees()
    if "PerpSettlePnl" in obj:
        return PerpSettlePnl()
    if "PerpUpdateFunding" in obj:
        return PerpUpdateFunding()
    if "Serum3CancelAllOrders" in obj:
        return Serum3CancelAllOrders()
    if "Serum3CancelOrder" in obj:
        return Serum3CancelOrder()
    if "Serum3CloseOpenOrders" in obj:
        return Serum3CloseOpenOrders()
    if "Serum3CreateOpenOrders" in obj:
        return Serum3CreateOpenOrders()
    if "Serum3DeregisterMarket" in obj:
        return Serum3DeregisterMarket()
    if "Serum3EditMarket" in obj:
        return Serum3EditMarket()
    if "Serum3LiqForceCancelOrders" in obj:
        return Serum3LiqForceCancelOrders()
    if "Serum3PlaceOrder" in obj:
        return Serum3PlaceOrder()
    if "Serum3RegisterMarket" in obj:
        return Serum3RegisterMarket()
    if "Serum3SettleFunds" in obj:
        return Serum3SettleFunds()
    if "StubOracleClose" in obj:
        return StubOracleClose()
    if "StubOracleCreate" in obj:
        return StubOracleCreate()
    if "StubOracleSet" in obj:
        return StubOracleSet()
    if "TokenAddBank" in obj:
        return TokenAddBank()
    if "TokenDeposit" in obj:
        return TokenDeposit()
    if "TokenDeregister" in obj:
        return TokenDeregister()
    if "TokenLiqBankruptcy" in obj:
        return TokenLiqBankruptcy()
    if "TokenLiqWithToken" in obj:
        return TokenLiqWithToken()
    if "TokenRegister" in obj:
        return TokenRegister()
    if "TokenRegisterTrustless" in obj:
        return TokenRegisterTrustless()
    if "TokenUpdateIndexAndRate" in obj:
        return TokenUpdateIndexAndRate()
    if "TokenWithdraw" in obj:
        return TokenWithdraw()
    if "AccountBuybackFeesWithMngo" in obj:
        return AccountBuybackFeesWithMngo()
    if "TokenForceCloseBorrowsWithToken" in obj:
        return TokenForceCloseBorrowsWithToken()
    if "PerpForceClosePosition" in obj:
        return PerpForceClosePosition()
    if "GroupWithdrawInsuranceFund" in obj:
        return GroupWithdrawInsuranceFund()
    if "TokenConditionalSwapCreate" in obj:
        return TokenConditionalSwapCreate()
    if "TokenConditionalSwapTrigger" in obj:
        return TokenConditionalSwapTrigger()
    if "TokenConditionalSwapCancel" in obj:
        return TokenConditionalSwapCancel()
    if "OpenbookV2CancelOrder" in obj:
        return OpenbookV2CancelOrder()
    if "OpenbookV2CloseOpenOrders" in obj:
        return OpenbookV2CloseOpenOrders()
    if "OpenbookV2CreateOpenOrders" in obj:
        return OpenbookV2CreateOpenOrders()
    if "OpenbookV2DeregisterMarket" in obj:
        return OpenbookV2DeregisterMarket()
    if "OpenbookV2EditMarket" in obj:
        return OpenbookV2EditMarket()
    if "OpenbookV2LiqForceCancelOrders" in obj:
        return OpenbookV2LiqForceCancelOrders()
    if "OpenbookV2PlaceOrder" in obj:
        return OpenbookV2PlaceOrder()
    if "OpenbookV2PlaceTakeOrder" in obj:
        return OpenbookV2PlaceTakeOrder()
    if "OpenbookV2RegisterMarket" in obj:
        return OpenbookV2RegisterMarket()
    if "OpenbookV2SettleFunds" in obj:
        return OpenbookV2SettleFunds()
    if "AdminTokenWithdrawFees" in obj:
        return AdminTokenWithdrawFees()
    if "AdminPerpWithdrawFees" in obj:
        return AdminPerpWithdrawFees()
    if "AccountSizeMigration" in obj:
        return AccountSizeMigration()
    if "TokenConditionalSwapStart" in obj:
        return TokenConditionalSwapStart()
    if "TokenConditionalSwapCreatePremiumAuction" in obj:
        return TokenConditionalSwapCreatePremiumAuction()
    if "TokenConditionalSwapCreateLinearAuction" in obj:
        return TokenConditionalSwapCreateLinearAuction()
    if "Serum3PlaceOrderV2" in obj:
        return Serum3PlaceOrderV2()
    if "TokenForceWithdraw" in obj:
        return TokenForceWithdraw()
    raise ValueError("Invalid enum object")


def from_json(obj: IxGateJSON) -> IxGateKind:
    if obj["kind"] == "AccountClose":
        return AccountClose()
    if obj["kind"] == "AccountCreate":
        return AccountCreate()
    if obj["kind"] == "AccountEdit":
        return AccountEdit()
    if obj["kind"] == "AccountExpand":
        return AccountExpand()
    if obj["kind"] == "AccountToggleFreeze":
        return AccountToggleFreeze()
    if obj["kind"] == "AltExtend":
        return AltExtend()
    if obj["kind"] == "AltSet":
        return AltSet()
    if obj["kind"] == "FlashLoan":
        return FlashLoan()
    if obj["kind"] == "GroupClose":
        return GroupClose()
    if obj["kind"] == "GroupCreate":
        return GroupCreate()
    if obj["kind"] == "HealthRegion":
        return HealthRegion()
    if obj["kind"] == "PerpCancelAllOrders":
        return PerpCancelAllOrders()
    if obj["kind"] == "PerpCancelAllOrdersBySide":
        return PerpCancelAllOrdersBySide()
    if obj["kind"] == "PerpCancelOrder":
        return PerpCancelOrder()
    if obj["kind"] == "PerpCancelOrderByClientOrderId":
        return PerpCancelOrderByClientOrderId()
    if obj["kind"] == "PerpCloseMarket":
        return PerpCloseMarket()
    if obj["kind"] == "PerpConsumeEvents":
        return PerpConsumeEvents()
    if obj["kind"] == "PerpCreateMarket":
        return PerpCreateMarket()
    if obj["kind"] == "PerpDeactivatePosition":
        return PerpDeactivatePosition()
    if obj["kind"] == "PerpLiqBaseOrPositivePnl":
        return PerpLiqBaseOrPositivePnl()
    if obj["kind"] == "PerpLiqForceCancelOrders":
        return PerpLiqForceCancelOrders()
    if obj["kind"] == "PerpLiqNegativePnlOrBankruptcy":
        return PerpLiqNegativePnlOrBankruptcy()
    if obj["kind"] == "PerpPlaceOrder":
        return PerpPlaceOrder()
    if obj["kind"] == "PerpSettleFees":
        return PerpSettleFees()
    if obj["kind"] == "PerpSettlePnl":
        return PerpSettlePnl()
    if obj["kind"] == "PerpUpdateFunding":
        return PerpUpdateFunding()
    if obj["kind"] == "Serum3CancelAllOrders":
        return Serum3CancelAllOrders()
    if obj["kind"] == "Serum3CancelOrder":
        return Serum3CancelOrder()
    if obj["kind"] == "Serum3CloseOpenOrders":
        return Serum3CloseOpenOrders()
    if obj["kind"] == "Serum3CreateOpenOrders":
        return Serum3CreateOpenOrders()
    if obj["kind"] == "Serum3DeregisterMarket":
        return Serum3DeregisterMarket()
    if obj["kind"] == "Serum3EditMarket":
        return Serum3EditMarket()
    if obj["kind"] == "Serum3LiqForceCancelOrders":
        return Serum3LiqForceCancelOrders()
    if obj["kind"] == "Serum3PlaceOrder":
        return Serum3PlaceOrder()
    if obj["kind"] == "Serum3RegisterMarket":
        return Serum3RegisterMarket()
    if obj["kind"] == "Serum3SettleFunds":
        return Serum3SettleFunds()
    if obj["kind"] == "StubOracleClose":
        return StubOracleClose()
    if obj["kind"] == "StubOracleCreate":
        return StubOracleCreate()
    if obj["kind"] == "StubOracleSet":
        return StubOracleSet()
    if obj["kind"] == "TokenAddBank":
        return TokenAddBank()
    if obj["kind"] == "TokenDeposit":
        return TokenDeposit()
    if obj["kind"] == "TokenDeregister":
        return TokenDeregister()
    if obj["kind"] == "TokenLiqBankruptcy":
        return TokenLiqBankruptcy()
    if obj["kind"] == "TokenLiqWithToken":
        return TokenLiqWithToken()
    if obj["kind"] == "TokenRegister":
        return TokenRegister()
    if obj["kind"] == "TokenRegisterTrustless":
        return TokenRegisterTrustless()
    if obj["kind"] == "TokenUpdateIndexAndRate":
        return TokenUpdateIndexAndRate()
    if obj["kind"] == "TokenWithdraw":
        return TokenWithdraw()
    if obj["kind"] == "AccountBuybackFeesWithMngo":
        return AccountBuybackFeesWithMngo()
    if obj["kind"] == "TokenForceCloseBorrowsWithToken":
        return TokenForceCloseBorrowsWithToken()
    if obj["kind"] == "PerpForceClosePosition":
        return PerpForceClosePosition()
    if obj["kind"] == "GroupWithdrawInsuranceFund":
        return GroupWithdrawInsuranceFund()
    if obj["kind"] == "TokenConditionalSwapCreate":
        return TokenConditionalSwapCreate()
    if obj["kind"] == "TokenConditionalSwapTrigger":
        return TokenConditionalSwapTrigger()
    if obj["kind"] == "TokenConditionalSwapCancel":
        return TokenConditionalSwapCancel()
    if obj["kind"] == "OpenbookV2CancelOrder":
        return OpenbookV2CancelOrder()
    if obj["kind"] == "OpenbookV2CloseOpenOrders":
        return OpenbookV2CloseOpenOrders()
    if obj["kind"] == "OpenbookV2CreateOpenOrders":
        return OpenbookV2CreateOpenOrders()
    if obj["kind"] == "OpenbookV2DeregisterMarket":
        return OpenbookV2DeregisterMarket()
    if obj["kind"] == "OpenbookV2EditMarket":
        return OpenbookV2EditMarket()
    if obj["kind"] == "OpenbookV2LiqForceCancelOrders":
        return OpenbookV2LiqForceCancelOrders()
    if obj["kind"] == "OpenbookV2PlaceOrder":
        return OpenbookV2PlaceOrder()
    if obj["kind"] == "OpenbookV2PlaceTakeOrder":
        return OpenbookV2PlaceTakeOrder()
    if obj["kind"] == "OpenbookV2RegisterMarket":
        return OpenbookV2RegisterMarket()
    if obj["kind"] == "OpenbookV2SettleFunds":
        return OpenbookV2SettleFunds()
    if obj["kind"] == "AdminTokenWithdrawFees":
        return AdminTokenWithdrawFees()
    if obj["kind"] == "AdminPerpWithdrawFees":
        return AdminPerpWithdrawFees()
    if obj["kind"] == "AccountSizeMigration":
        return AccountSizeMigration()
    if obj["kind"] == "TokenConditionalSwapStart":
        return TokenConditionalSwapStart()
    if obj["kind"] == "TokenConditionalSwapCreatePremiumAuction":
        return TokenConditionalSwapCreatePremiumAuction()
    if obj["kind"] == "TokenConditionalSwapCreateLinearAuction":
        return TokenConditionalSwapCreateLinearAuction()
    if obj["kind"] == "Serum3PlaceOrderV2":
        return Serum3PlaceOrderV2()
    if obj["kind"] == "TokenForceWithdraw":
        return TokenForceWithdraw()
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "AccountClose" / borsh.CStruct(),
    "AccountCreate" / borsh.CStruct(),
    "AccountEdit" / borsh.CStruct(),
    "AccountExpand" / borsh.CStruct(),
    "AccountToggleFreeze" / borsh.CStruct(),
    "AltExtend" / borsh.CStruct(),
    "AltSet" / borsh.CStruct(),
    "FlashLoan" / borsh.CStruct(),
    "GroupClose" / borsh.CStruct(),
    "GroupCreate" / borsh.CStruct(),
    "HealthRegion" / borsh.CStruct(),
    "PerpCancelAllOrders" / borsh.CStruct(),
    "PerpCancelAllOrdersBySide" / borsh.CStruct(),
    "PerpCancelOrder" / borsh.CStruct(),
    "PerpCancelOrderByClientOrderId" / borsh.CStruct(),
    "PerpCloseMarket" / borsh.CStruct(),
    "PerpConsumeEvents" / borsh.CStruct(),
    "PerpCreateMarket" / borsh.CStruct(),
    "PerpDeactivatePosition" / borsh.CStruct(),
    "PerpLiqBaseOrPositivePnl" / borsh.CStruct(),
    "PerpLiqForceCancelOrders" / borsh.CStruct(),
    "PerpLiqNegativePnlOrBankruptcy" / borsh.CStruct(),
    "PerpPlaceOrder" / borsh.CStruct(),
    "PerpSettleFees" / borsh.CStruct(),
    "PerpSettlePnl" / borsh.CStruct(),
    "PerpUpdateFunding" / borsh.CStruct(),
    "Serum3CancelAllOrders" / borsh.CStruct(),
    "Serum3CancelOrder" / borsh.CStruct(),
    "Serum3CloseOpenOrders" / borsh.CStruct(),
    "Serum3CreateOpenOrders" / borsh.CStruct(),
    "Serum3DeregisterMarket" / borsh.CStruct(),
    "Serum3EditMarket" / borsh.CStruct(),
    "Serum3LiqForceCancelOrders" / borsh.CStruct(),
    "Serum3PlaceOrder" / borsh.CStruct(),
    "Serum3RegisterMarket" / borsh.CStruct(),
    "Serum3SettleFunds" / borsh.CStruct(),
    "StubOracleClose" / borsh.CStruct(),
    "StubOracleCreate" / borsh.CStruct(),
    "StubOracleSet" / borsh.CStruct(),
    "TokenAddBank" / borsh.CStruct(),
    "TokenDeposit" / borsh.CStruct(),
    "TokenDeregister" / borsh.CStruct(),
    "TokenLiqBankruptcy" / borsh.CStruct(),
    "TokenLiqWithToken" / borsh.CStruct(),
    "TokenRegister" / borsh.CStruct(),
    "TokenRegisterTrustless" / borsh.CStruct(),
    "TokenUpdateIndexAndRate" / borsh.CStruct(),
    "TokenWithdraw" / borsh.CStruct(),
    "AccountBuybackFeesWithMngo" / borsh.CStruct(),
    "TokenForceCloseBorrowsWithToken" / borsh.CStruct(),
    "PerpForceClosePosition" / borsh.CStruct(),
    "GroupWithdrawInsuranceFund" / borsh.CStruct(),
    "TokenConditionalSwapCreate" / borsh.CStruct(),
    "TokenConditionalSwapTrigger" / borsh.CStruct(),
    "TokenConditionalSwapCancel" / borsh.CStruct(),
    "OpenbookV2CancelOrder" / borsh.CStruct(),
    "OpenbookV2CloseOpenOrders" / borsh.CStruct(),
    "OpenbookV2CreateOpenOrders" / borsh.CStruct(),
    "OpenbookV2DeregisterMarket" / borsh.CStruct(),
    "OpenbookV2EditMarket" / borsh.CStruct(),
    "OpenbookV2LiqForceCancelOrders" / borsh.CStruct(),
    "OpenbookV2PlaceOrder" / borsh.CStruct(),
    "OpenbookV2PlaceTakeOrder" / borsh.CStruct(),
    "OpenbookV2RegisterMarket" / borsh.CStruct(),
    "OpenbookV2SettleFunds" / borsh.CStruct(),
    "AdminTokenWithdrawFees" / borsh.CStruct(),
    "AdminPerpWithdrawFees" / borsh.CStruct(),
    "AccountSizeMigration" / borsh.CStruct(),
    "TokenConditionalSwapStart" / borsh.CStruct(),
    "TokenConditionalSwapCreatePremiumAuction" / borsh.CStruct(),
    "TokenConditionalSwapCreateLinearAuction" / borsh.CStruct(),
    "Serum3PlaceOrderV2" / borsh.CStruct(),
    "TokenForceWithdraw" / borsh.CStruct(),
)
