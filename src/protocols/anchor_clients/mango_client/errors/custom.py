import typing
from anchorpy.error import ProgramError


class SomeError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "")

    code = 6000
    name = "SomeError"
    msg = ""


class NotImplementedError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "")

    code = 6001
    name = "NotImplementedError"
    msg = ""


class MathError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "checked math error")

    code = 6002
    name = "MathError"
    msg = "checked math error"


class UnexpectedOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "")

    code = 6003
    name = "UnexpectedOracle"
    msg = ""


class UnknownOracleType(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "oracle type cannot be determined")

    code = 6004
    name = "UnknownOracleType"
    msg = "oracle type cannot be determined"


class InvalidFlashLoanTargetCpiProgram(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "")

    code = 6005
    name = "InvalidFlashLoanTargetCpiProgram"
    msg = ""


class HealthMustBePositive(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "health must be positive")

    code = 6006
    name = "HealthMustBePositive"
    msg = "health must be positive"


class HealthMustBePositiveOrIncrease(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "health must be positive or not decrease")

    code = 6007
    name = "HealthMustBePositiveOrIncrease"
    msg = "health must be positive or not decrease"


class HealthMustBeNegative(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "health must be negative")

    code = 6008
    name = "HealthMustBeNegative"
    msg = "health must be negative"


class IsBankrupt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "the account is bankrupt")

    code = 6009
    name = "IsBankrupt"
    msg = "the account is bankrupt"


class IsNotBankrupt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "the account is not bankrupt")

    code = 6010
    name = "IsNotBankrupt"
    msg = "the account is not bankrupt"


class NoFreeTokenPositionIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "no free token position index")

    code = 6011
    name = "NoFreeTokenPositionIndex"
    msg = "no free token position index"


class NoFreeSerum3OpenOrdersIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "no free serum3 open orders index")

    code = 6012
    name = "NoFreeSerum3OpenOrdersIndex"
    msg = "no free serum3 open orders index"


class NoFreePerpPositionIndex(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "no free perp position index")

    code = 6013
    name = "NoFreePerpPositionIndex"
    msg = "no free perp position index"


class Serum3OpenOrdersExistAlready(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "serum3 open orders exist already")

    code = 6014
    name = "Serum3OpenOrdersExistAlready"
    msg = "serum3 open orders exist already"


class InsufficentBankVaultFunds(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "bank vault has insufficent funds")

    code = 6015
    name = "InsufficentBankVaultFunds"
    msg = "bank vault has insufficent funds"


class BeingLiquidated(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "account is currently being liquidated")

    code = 6016
    name = "BeingLiquidated"
    msg = "account is currently being liquidated"


class InvalidBank(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "invalid bank")

    code = 6017
    name = "InvalidBank"
    msg = "invalid bank"


class ProfitabilityMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "account profitability is mismatched")

    code = 6018
    name = "ProfitabilityMismatch"
    msg = "account profitability is mismatched"


class CannotSettleWithSelf(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "cannot settle with self")

    code = 6019
    name = "CannotSettleWithSelf"
    msg = "cannot settle with self"


class PerpPositionDoesNotExist(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "perp position does not exist")

    code = 6020
    name = "PerpPositionDoesNotExist"
    msg = "perp position does not exist"


class MaxSettleAmountMustBeGreaterThanZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "max settle amount must be greater than zero")

    code = 6021
    name = "MaxSettleAmountMustBeGreaterThanZero"
    msg = "max settle amount must be greater than zero"


class HasOpenPerpOrders(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6022, "the perp position has open orders or unprocessed fill events"
        )

    code = 6022
    name = "HasOpenPerpOrders"
    msg = "the perp position has open orders or unprocessed fill events"


class OracleConfidence(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "an oracle does not reach the confidence threshold")

    code = 6023
    name = "OracleConfidence"
    msg = "an oracle does not reach the confidence threshold"


class OracleStale(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, "an oracle is stale")

    code = 6024
    name = "OracleStale"
    msg = "an oracle is stale"


class SettlementAmountMustBePositive(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, "settlement amount must always be positive")

    code = 6025
    name = "SettlementAmountMustBePositive"
    msg = "settlement amount must always be positive"


class BankBorrowLimitReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, "bank utilization has reached limit")

    code = 6026
    name = "BankBorrowLimitReached"
    msg = "bank utilization has reached limit"


class BankNetBorrowsLimitReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6027,
            "bank net borrows has reached limit - this is an intermittent error - the limit will reset regularly",
        )

    code = 6027
    name = "BankNetBorrowsLimitReached"
    msg = "bank net borrows has reached limit - this is an intermittent error - the limit will reset regularly"


class TokenPositionDoesNotExist(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, "token position does not exist")

    code = 6028
    name = "TokenPositionDoesNotExist"
    msg = "token position does not exist"


class DepositsIntoLiquidatingMustRecover(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6029,
            "token deposits into accounts that are being liquidated must bring their health above the init threshold",
        )

    code = 6029
    name = "DepositsIntoLiquidatingMustRecover"
    msg = "token deposits into accounts that are being liquidated must bring their health above the init threshold"


class TokenInReduceOnlyMode(ProgramError):
    def __init__(self) -> None:
        super().__init__(6030, "token is in reduce only mode")

    code = 6030
    name = "TokenInReduceOnlyMode"
    msg = "token is in reduce only mode"


class MarketInReduceOnlyMode(ProgramError):
    def __init__(self) -> None:
        super().__init__(6031, "market is in reduce only mode")

    code = 6031
    name = "MarketInReduceOnlyMode"
    msg = "market is in reduce only mode"


class GroupIsHalted(ProgramError):
    def __init__(self) -> None:
        super().__init__(6032, "group is halted")

    code = 6032
    name = "GroupIsHalted"
    msg = "group is halted"


class PerpHasBaseLots(ProgramError):
    def __init__(self) -> None:
        super().__init__(6033, "the perp position has non-zero base lots")

    code = 6033
    name = "PerpHasBaseLots"
    msg = "the perp position has non-zero base lots"


class HasOpenOrUnsettledSerum3Orders(ProgramError):
    def __init__(self) -> None:
        super().__init__(6034, "there are open or unsettled serum3 orders")

    code = 6034
    name = "HasOpenOrUnsettledSerum3Orders"
    msg = "there are open or unsettled serum3 orders"


class HasLiquidatableTokenPosition(ProgramError):
    def __init__(self) -> None:
        super().__init__(6035, "has liquidatable token position")

    code = 6035
    name = "HasLiquidatableTokenPosition"
    msg = "has liquidatable token position"


class HasLiquidatablePerpBasePosition(ProgramError):
    def __init__(self) -> None:
        super().__init__(6036, "has liquidatable perp base position")

    code = 6036
    name = "HasLiquidatablePerpBasePosition"
    msg = "has liquidatable perp base position"


class HasLiquidatablePositivePerpPnl(ProgramError):
    def __init__(self) -> None:
        super().__init__(6037, "has liquidatable positive perp pnl")

    code = 6037
    name = "HasLiquidatablePositivePerpPnl"
    msg = "has liquidatable positive perp pnl"


class AccountIsFrozen(ProgramError):
    def __init__(self) -> None:
        super().__init__(6038, "account is frozen")

    code = 6038
    name = "AccountIsFrozen"
    msg = "account is frozen"


class InitAssetWeightCantBeNegative(ProgramError):
    def __init__(self) -> None:
        super().__init__(6039, "Init Asset Weight can't be negative")

    code = 6039
    name = "InitAssetWeightCantBeNegative"
    msg = "Init Asset Weight can't be negative"


class HasOpenPerpTakerFills(ProgramError):
    def __init__(self) -> None:
        super().__init__(6040, "has open perp taker fills")

    code = 6040
    name = "HasOpenPerpTakerFills"
    msg = "has open perp taker fills"


class DepositLimit(ProgramError):
    def __init__(self) -> None:
        super().__init__(6041, "deposit crosses the current group deposit limit")

    code = 6041
    name = "DepositLimit"
    msg = "deposit crosses the current group deposit limit"


class IxIsDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6042, "instruction is disabled")

    code = 6042
    name = "IxIsDisabled"
    msg = "instruction is disabled"


class NoLiquidatablePerpBasePosition(ProgramError):
    def __init__(self) -> None:
        super().__init__(6043, "no liquidatable perp base position")

    code = 6043
    name = "NoLiquidatablePerpBasePosition"
    msg = "no liquidatable perp base position"


class PerpOrderIdNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6044, "perp order id not found on the orderbook")

    code = 6044
    name = "PerpOrderIdNotFound"
    msg = "perp order id not found on the orderbook"


class HealthRegionBadInnerInstruction(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6045, "HealthRegions allow only specific instructions between Begin and End"
        )

    code = 6045
    name = "HealthRegionBadInnerInstruction"
    msg = "HealthRegions allow only specific instructions between Begin and End"


class TokenInForceClose(ProgramError):
    def __init__(self) -> None:
        super().__init__(6046, "token is in force close")

    code = 6046
    name = "TokenInForceClose"
    msg = "token is in force close"


class InvalidHealthAccountCount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6047, "incorrect number of health accounts")

    code = 6047
    name = "InvalidHealthAccountCount"
    msg = "incorrect number of health accounts"


class WouldSelfTrade(ProgramError):
    def __init__(self) -> None:
        super().__init__(6048, "would self trade")

    code = 6048
    name = "WouldSelfTrade"
    msg = "would self trade"


class TokenConditionalSwapPriceNotInRange(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6049, "token conditional swap oracle price is not in execution range"
        )

    code = 6049
    name = "TokenConditionalSwapPriceNotInRange"
    msg = "token conditional swap oracle price is not in execution range"


class TokenConditionalSwapExpired(ProgramError):
    def __init__(self) -> None:
        super().__init__(6050, "token conditional swap is expired")

    code = 6050
    name = "TokenConditionalSwapExpired"
    msg = "token conditional swap is expired"


class TokenConditionalSwapNotStarted(ProgramError):
    def __init__(self) -> None:
        super().__init__(6051, "token conditional swap is not available yet")

    code = 6051
    name = "TokenConditionalSwapNotStarted"
    msg = "token conditional swap is not available yet"


class TokenConditionalSwapAlreadyStarted(ProgramError):
    def __init__(self) -> None:
        super().__init__(6052, "token conditional swap was already started")

    code = 6052
    name = "TokenConditionalSwapAlreadyStarted"
    msg = "token conditional swap was already started"


class TokenConditionalSwapNotSet(ProgramError):
    def __init__(self) -> None:
        super().__init__(6053, "token conditional swap it not set")

    code = 6053
    name = "TokenConditionalSwapNotSet"
    msg = "token conditional swap it not set"


class TokenConditionalSwapMinBuyTokenNotReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6054, "token conditional swap trigger did not reach min_buy_token"
        )

    code = 6054
    name = "TokenConditionalSwapMinBuyTokenNotReached"
    msg = "token conditional swap trigger did not reach min_buy_token"


class TokenConditionalSwapCantPayIncentive(ProgramError):
    def __init__(self) -> None:
        super().__init__(6055, "token conditional swap cannot pay incentive")

    code = 6055
    name = "TokenConditionalSwapCantPayIncentive"
    msg = "token conditional swap cannot pay incentive"


class TokenConditionalSwapTakerPriceTooLow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6056, "token conditional swap taker price is too low")

    code = 6056
    name = "TokenConditionalSwapTakerPriceTooLow"
    msg = "token conditional swap taker price is too low"


class TokenConditionalSwapIndexIdMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6057, "token conditional swap index and id don't match")

    code = 6057
    name = "TokenConditionalSwapIndexIdMismatch"
    msg = "token conditional swap index and id don't match"


class TokenConditionalSwapTooSmallForStartIncentive(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6058,
            "token conditional swap volume is too small compared to the cost of starting it",
        )

    code = 6058
    name = "TokenConditionalSwapTooSmallForStartIncentive"
    msg = (
        "token conditional swap volume is too small compared to the cost of starting it"
    )


class TokenConditionalSwapTypeNotStartable(ProgramError):
    def __init__(self) -> None:
        super().__init__(6059, "token conditional swap type cannot be started")

    code = 6059
    name = "TokenConditionalSwapTypeNotStartable"
    msg = "token conditional swap type cannot be started"


class HealthAccountBankNotWritable(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6060, "a bank in the health account list should be writable but is not"
        )

    code = 6060
    name = "HealthAccountBankNotWritable"
    msg = "a bank in the health account list should be writable but is not"


class Serum3PriceBandExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6061,
            "the market does not allow limit orders too far from the current oracle value",
        )

    code = 6061
    name = "Serum3PriceBandExceeded"
    msg = "the market does not allow limit orders too far from the current oracle value"


class BankDepositLimit(ProgramError):
    def __init__(self) -> None:
        super().__init__(6062, "deposit crosses the token's deposit limit")

    code = 6062
    name = "BankDepositLimit"
    msg = "deposit crosses the token's deposit limit"


class DelegateWithdrawOnlyToOwnerAta(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6063, "delegates can only withdraw to the owner's associated token account"
        )

    code = 6063
    name = "DelegateWithdrawOnlyToOwnerAta"
    msg = "delegates can only withdraw to the owner's associated token account"


class DelegateWithdrawMustClosePosition(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6064, "delegates can only withdraw if they close the token position"
        )

    code = 6064
    name = "DelegateWithdrawMustClosePosition"
    msg = "delegates can only withdraw if they close the token position"


class DelegateWithdrawSmall(ProgramError):
    def __init__(self) -> None:
        super().__init__(6065, "delegates can only withdraw small amounts")

    code = 6065
    name = "DelegateWithdrawSmall"
    msg = "delegates can only withdraw small amounts"


class InvalidCLMMOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(6066, "The provided CLMM oracle is not valid")

    code = 6066
    name = "InvalidCLMMOracle"
    msg = "The provided CLMM oracle is not valid"


class InvalidFeedForCLMMOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(6067, "invalid usdc/usd feed provided for the CLMM oracle")

    code = 6067
    name = "InvalidFeedForCLMMOracle"
    msg = "invalid usdc/usd feed provided for the CLMM oracle"


class MissingFeedForCLMMOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6068, "Pyth USDC/USD or SOL/USD feed not found (required by CLMM oracle)"
        )

    code = 6068
    name = "MissingFeedForCLMMOracle"
    msg = "Pyth USDC/USD or SOL/USD feed not found (required by CLMM oracle)"


class TokenAssetLiquidationDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6069, "the asset does not allow liquidation")

    code = 6069
    name = "TokenAssetLiquidationDisabled"
    msg = "the asset does not allow liquidation"


CustomError = typing.Union[
    SomeError,
    NotImplementedError,
    MathError,
    UnexpectedOracle,
    UnknownOracleType,
    InvalidFlashLoanTargetCpiProgram,
    HealthMustBePositive,
    HealthMustBePositiveOrIncrease,
    HealthMustBeNegative,
    IsBankrupt,
    IsNotBankrupt,
    NoFreeTokenPositionIndex,
    NoFreeSerum3OpenOrdersIndex,
    NoFreePerpPositionIndex,
    Serum3OpenOrdersExistAlready,
    InsufficentBankVaultFunds,
    BeingLiquidated,
    InvalidBank,
    ProfitabilityMismatch,
    CannotSettleWithSelf,
    PerpPositionDoesNotExist,
    MaxSettleAmountMustBeGreaterThanZero,
    HasOpenPerpOrders,
    OracleConfidence,
    OracleStale,
    SettlementAmountMustBePositive,
    BankBorrowLimitReached,
    BankNetBorrowsLimitReached,
    TokenPositionDoesNotExist,
    DepositsIntoLiquidatingMustRecover,
    TokenInReduceOnlyMode,
    MarketInReduceOnlyMode,
    GroupIsHalted,
    PerpHasBaseLots,
    HasOpenOrUnsettledSerum3Orders,
    HasLiquidatableTokenPosition,
    HasLiquidatablePerpBasePosition,
    HasLiquidatablePositivePerpPnl,
    AccountIsFrozen,
    InitAssetWeightCantBeNegative,
    HasOpenPerpTakerFills,
    DepositLimit,
    IxIsDisabled,
    NoLiquidatablePerpBasePosition,
    PerpOrderIdNotFound,
    HealthRegionBadInnerInstruction,
    TokenInForceClose,
    InvalidHealthAccountCount,
    WouldSelfTrade,
    TokenConditionalSwapPriceNotInRange,
    TokenConditionalSwapExpired,
    TokenConditionalSwapNotStarted,
    TokenConditionalSwapAlreadyStarted,
    TokenConditionalSwapNotSet,
    TokenConditionalSwapMinBuyTokenNotReached,
    TokenConditionalSwapCantPayIncentive,
    TokenConditionalSwapTakerPriceTooLow,
    TokenConditionalSwapIndexIdMismatch,
    TokenConditionalSwapTooSmallForStartIncentive,
    TokenConditionalSwapTypeNotStartable,
    HealthAccountBankNotWritable,
    Serum3PriceBandExceeded,
    BankDepositLimit,
    DelegateWithdrawOnlyToOwnerAta,
    DelegateWithdrawMustClosePosition,
    DelegateWithdrawSmall,
    InvalidCLMMOracle,
    InvalidFeedForCLMMOracle,
    MissingFeedForCLMMOracle,
    TokenAssetLiquidationDisabled,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: SomeError(),
    6001: NotImplementedError(),
    6002: MathError(),
    6003: UnexpectedOracle(),
    6004: UnknownOracleType(),
    6005: InvalidFlashLoanTargetCpiProgram(),
    6006: HealthMustBePositive(),
    6007: HealthMustBePositiveOrIncrease(),
    6008: HealthMustBeNegative(),
    6009: IsBankrupt(),
    6010: IsNotBankrupt(),
    6011: NoFreeTokenPositionIndex(),
    6012: NoFreeSerum3OpenOrdersIndex(),
    6013: NoFreePerpPositionIndex(),
    6014: Serum3OpenOrdersExistAlready(),
    6015: InsufficentBankVaultFunds(),
    6016: BeingLiquidated(),
    6017: InvalidBank(),
    6018: ProfitabilityMismatch(),
    6019: CannotSettleWithSelf(),
    6020: PerpPositionDoesNotExist(),
    6021: MaxSettleAmountMustBeGreaterThanZero(),
    6022: HasOpenPerpOrders(),
    6023: OracleConfidence(),
    6024: OracleStale(),
    6025: SettlementAmountMustBePositive(),
    6026: BankBorrowLimitReached(),
    6027: BankNetBorrowsLimitReached(),
    6028: TokenPositionDoesNotExist(),
    6029: DepositsIntoLiquidatingMustRecover(),
    6030: TokenInReduceOnlyMode(),
    6031: MarketInReduceOnlyMode(),
    6032: GroupIsHalted(),
    6033: PerpHasBaseLots(),
    6034: HasOpenOrUnsettledSerum3Orders(),
    6035: HasLiquidatableTokenPosition(),
    6036: HasLiquidatablePerpBasePosition(),
    6037: HasLiquidatablePositivePerpPnl(),
    6038: AccountIsFrozen(),
    6039: InitAssetWeightCantBeNegative(),
    6040: HasOpenPerpTakerFills(),
    6041: DepositLimit(),
    6042: IxIsDisabled(),
    6043: NoLiquidatablePerpBasePosition(),
    6044: PerpOrderIdNotFound(),
    6045: HealthRegionBadInnerInstruction(),
    6046: TokenInForceClose(),
    6047: InvalidHealthAccountCount(),
    6048: WouldSelfTrade(),
    6049: TokenConditionalSwapPriceNotInRange(),
    6050: TokenConditionalSwapExpired(),
    6051: TokenConditionalSwapNotStarted(),
    6052: TokenConditionalSwapAlreadyStarted(),
    6053: TokenConditionalSwapNotSet(),
    6054: TokenConditionalSwapMinBuyTokenNotReached(),
    6055: TokenConditionalSwapCantPayIncentive(),
    6056: TokenConditionalSwapTakerPriceTooLow(),
    6057: TokenConditionalSwapIndexIdMismatch(),
    6058: TokenConditionalSwapTooSmallForStartIncentive(),
    6059: TokenConditionalSwapTypeNotStartable(),
    6060: HealthAccountBankNotWritable(),
    6061: Serum3PriceBandExceeded(),
    6062: BankDepositLimit(),
    6063: DelegateWithdrawOnlyToOwnerAta(),
    6064: DelegateWithdrawMustClosePosition(),
    6065: DelegateWithdrawSmall(),
    6066: InvalidCLMMOracle(),
    6067: InvalidFeedForCLMMOracle(),
    6068: MissingFeedForCLMMOracle(),
    6069: TokenAssetLiquidationDisabled(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
