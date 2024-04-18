import typing
from anchorpy.error import ProgramError


class InvalidMarketAuthority(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Market authority is invalid")

    code = 6000
    name = "InvalidMarketAuthority"
    msg = "Market authority is invalid"


class InvalidMarketOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Market owner is invalid")

    code = 6001
    name = "InvalidMarketOwner"
    msg = "Market owner is invalid"


class InvalidAccountOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Input account owner is not the program address")

    code = 6002
    name = "InvalidAccountOwner"
    msg = "Input account owner is not the program address"


class InvalidAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Input amount is invalid")

    code = 6003
    name = "InvalidAmount"
    msg = "Input amount is invalid"


class InvalidConfig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Input config value is invalid")

    code = 6004
    name = "InvalidConfig"
    msg = "Input config value is invalid"


class InvalidSigner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Input account must be a signer")

    code = 6005
    name = "InvalidSigner"
    msg = "Input account must be a signer"


class InvalidAccountInput(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Invalid account input")

    code = 6006
    name = "InvalidAccountInput"
    msg = "Invalid account input"


class MathOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Math operation overflow")

    code = 6007
    name = "MathOverflow"
    msg = "Math operation overflow"


class InsufficientLiquidity(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Insufficient liquidity available")

    code = 6008
    name = "InsufficientLiquidity"
    msg = "Insufficient liquidity available"


class ReserveStale(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Reserve state needs to be refreshed")

    code = 6009
    name = "ReserveStale"
    msg = "Reserve state needs to be refreshed"


class WithdrawTooSmall(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Withdraw amount too small")

    code = 6010
    name = "WithdrawTooSmall"
    msg = "Withdraw amount too small"


class WithdrawTooLarge(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Withdraw amount too large")

    code = 6011
    name = "WithdrawTooLarge"
    msg = "Withdraw amount too large"


class BorrowTooSmall(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6012, "Borrow amount too small to receive liquidity after fees"
        )

    code = 6012
    name = "BorrowTooSmall"
    msg = "Borrow amount too small to receive liquidity after fees"


class BorrowTooLarge(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "Borrow amount too large for deposited collateral")

    code = 6013
    name = "BorrowTooLarge"
    msg = "Borrow amount too large for deposited collateral"


class RepayTooSmall(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Repay amount too small to transfer liquidity")

    code = 6014
    name = "RepayTooSmall"
    msg = "Repay amount too small to transfer liquidity"


class LiquidationTooSmall(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Liquidation amount too small to receive collateral")

    code = 6015
    name = "LiquidationTooSmall"
    msg = "Liquidation amount too small to receive collateral"


class ObligationHealthy(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Cannot liquidate healthy obligations")

    code = 6016
    name = "ObligationHealthy"
    msg = "Cannot liquidate healthy obligations"


class ObligationStale(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "Obligation state needs to be refreshed")

    code = 6017
    name = "ObligationStale"
    msg = "Obligation state needs to be refreshed"


class ObligationReserveLimit(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "Obligation reserve limit exceeded")

    code = 6018
    name = "ObligationReserveLimit"
    msg = "Obligation reserve limit exceeded"


class InvalidObligationOwner(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "Obligation owner is invalid")

    code = 6019
    name = "InvalidObligationOwner"
    msg = "Obligation owner is invalid"


class ObligationDepositsEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "Obligation deposits are empty")

    code = 6020
    name = "ObligationDepositsEmpty"
    msg = "Obligation deposits are empty"


class ObligationBorrowsEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "Obligation borrows are empty")

    code = 6021
    name = "ObligationBorrowsEmpty"
    msg = "Obligation borrows are empty"


class ObligationDepositsZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6022, "Obligation deposits have zero value")

    code = 6022
    name = "ObligationDepositsZero"
    msg = "Obligation deposits have zero value"


class ObligationBorrowsZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "Obligation borrows have zero value")

    code = 6023
    name = "ObligationBorrowsZero"
    msg = "Obligation borrows have zero value"


class InvalidObligationCollateral(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, "Invalid obligation collateral")

    code = 6024
    name = "InvalidObligationCollateral"
    msg = "Invalid obligation collateral"


class InvalidObligationLiquidity(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, "Invalid obligation liquidity")

    code = 6025
    name = "InvalidObligationLiquidity"
    msg = "Invalid obligation liquidity"


class ObligationCollateralEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, "Obligation collateral is empty")

    code = 6026
    name = "ObligationCollateralEmpty"
    msg = "Obligation collateral is empty"


class ObligationLiquidityEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6027, "Obligation liquidity is empty")

    code = 6027
    name = "ObligationLiquidityEmpty"
    msg = "Obligation liquidity is empty"


class NegativeInterestRate(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, "Interest rate is negative")

    code = 6028
    name = "NegativeInterestRate"
    msg = "Interest rate is negative"


class InvalidOracleConfig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6029, "Input oracle config is invalid")

    code = 6029
    name = "InvalidOracleConfig"
    msg = "Input oracle config is invalid"


class InsufficientProtocolFeesToRedeem(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6030, "Insufficient protocol fees to claim or no liquidity available"
        )

    code = 6030
    name = "InsufficientProtocolFeesToRedeem"
    msg = "Insufficient protocol fees to claim or no liquidity available"


class FlashBorrowCpi(ProgramError):
    def __init__(self) -> None:
        super().__init__(6031, "No cpi flash borrows allowed")

    code = 6031
    name = "FlashBorrowCpi"
    msg = "No cpi flash borrows allowed"


class NoFlashRepayFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6032, "No corresponding repay found for flash borrow")

    code = 6032
    name = "NoFlashRepayFound"
    msg = "No corresponding repay found for flash borrow"


class InvalidFlashRepay(ProgramError):
    def __init__(self) -> None:
        super().__init__(6033, "Invalid repay found")

    code = 6033
    name = "InvalidFlashRepay"
    msg = "Invalid repay found"


class FlashRepayCpi(ProgramError):
    def __init__(self) -> None:
        super().__init__(6034, "No cpi flash repays allowed")

    code = 6034
    name = "FlashRepayCpi"
    msg = "No cpi flash repays allowed"


class MultipleFlashBorrows(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6035, "Multiple flash borrows not allowed in the same transaction"
        )

    code = 6035
    name = "MultipleFlashBorrows"
    msg = "Multiple flash borrows not allowed in the same transaction"


class FlashLoansDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6036, "Flash loans are disabled for this reserve")

    code = 6036
    name = "FlashLoansDisabled"
    msg = "Flash loans are disabled for this reserve"


class SwitchboardV2Error(ProgramError):
    def __init__(self) -> None:
        super().__init__(6037, "Switchboard error")

    code = 6037
    name = "SwitchboardV2Error"
    msg = "Switchboard error"


class CouldNotDeserializeScope(ProgramError):
    def __init__(self) -> None:
        super().__init__(6038, "Cannot deserialize the scope price account")

    code = 6038
    name = "CouldNotDeserializeScope"
    msg = "Cannot deserialize the scope price account"


class PriceTooOld(ProgramError):
    def __init__(self) -> None:
        super().__init__(6039, "Price too old")

    code = 6039
    name = "PriceTooOld"
    msg = "Price too old"


class PriceTooDivergentFromTwap(ProgramError):
    def __init__(self) -> None:
        super().__init__(6040, "Price too divergent from twap")

    code = 6040
    name = "PriceTooDivergentFromTwap"
    msg = "Price too divergent from twap"


class InvalidTwapPrice(ProgramError):
    def __init__(self) -> None:
        super().__init__(6041, "Invalid twap price")

    code = 6041
    name = "InvalidTwapPrice"
    msg = "Invalid twap price"


class GlobalEmergencyMode(ProgramError):
    def __init__(self) -> None:
        super().__init__(6042, "Emergency mode is enabled")

    code = 6042
    name = "GlobalEmergencyMode"
    msg = "Emergency mode is enabled"


class InvalidFlag(ProgramError):
    def __init__(self) -> None:
        super().__init__(6043, "Invalid lending market config")

    code = 6043
    name = "InvalidFlag"
    msg = "Invalid lending market config"


class PriceNotValid(ProgramError):
    def __init__(self) -> None:
        super().__init__(6044, "Price is not valid")

    code = 6044
    name = "PriceNotValid"
    msg = "Price is not valid"


class PriceIsBiggerThanHeuristic(ProgramError):
    def __init__(self) -> None:
        super().__init__(6045, "Price is bigger than allowed by heuristic")

    code = 6045
    name = "PriceIsBiggerThanHeuristic"
    msg = "Price is bigger than allowed by heuristic"


class PriceIsLowerThanHeuristic(ProgramError):
    def __init__(self) -> None:
        super().__init__(6046, "Price lower than allowed by heuristic")

    code = 6046
    name = "PriceIsLowerThanHeuristic"
    msg = "Price lower than allowed by heuristic"


class PriceIsZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(6047, "Price is zero")

    code = 6047
    name = "PriceIsZero"
    msg = "Price is zero"


class PriceConfidenceTooWide(ProgramError):
    def __init__(self) -> None:
        super().__init__(6048, "Price confidence too wide")

    code = 6048
    name = "PriceConfidenceTooWide"
    msg = "Price confidence too wide"


class IntegerOverflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6049, "Conversion between integers failed")

    code = 6049
    name = "IntegerOverflow"
    msg = "Conversion between integers failed"


class NoFarmForReserve(ProgramError):
    def __init__(self) -> None:
        super().__init__(6050, "This reserve does not have a farm")

    code = 6050
    name = "NoFarmForReserve"
    msg = "This reserve does not have a farm"


class IncorrectInstructionInPosition(ProgramError):
    def __init__(self) -> None:
        super().__init__(6051, "Wrong instruction at expected position")

    code = 6051
    name = "IncorrectInstructionInPosition"
    msg = "Wrong instruction at expected position"


class NoPriceFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6052, "No price found")

    code = 6052
    name = "NoPriceFound"
    msg = "No price found"


class InvalidTwapConfig(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6053,
            "Invalid Twap configuration: Twap is enabled but one of the enabled price doesn't have a twap",
        )

    code = 6053
    name = "InvalidTwapConfig"
    msg = "Invalid Twap configuration: Twap is enabled but one of the enabled price doesn't have a twap"


class InvalidPythPriceAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6054, "Pyth price account does not match configuration")

    code = 6054
    name = "InvalidPythPriceAccount"
    msg = "Pyth price account does not match configuration"


class InvalidSwitchboardAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6055, "Switchboard account(s) do not match configuration")

    code = 6055
    name = "InvalidSwitchboardAccount"
    msg = "Switchboard account(s) do not match configuration"


class InvalidScopePriceAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6056, "Scope price account does not match configuration")

    code = 6056
    name = "InvalidScopePriceAccount"
    msg = "Scope price account does not match configuration"


class ObligationCollateralLtvZero(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6057,
            "The obligation has one collateral with an LTV set to 0. Withdraw it before withdrawing other collaterals",
        )

    code = 6057
    name = "ObligationCollateralLtvZero"
    msg = "The obligation has one collateral with an LTV set to 0. Withdraw it before withdrawing other collaterals"


class InvalidObligationSeedsValue(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6058,
            "Seeds must be default pubkeys for tag 0, and mint addresses for tag 1 or 2",
        )

    code = 6058
    name = "InvalidObligationSeedsValue"
    msg = "Seeds must be default pubkeys for tag 0, and mint addresses for tag 1 or 2"


class InvalidObligationId(ProgramError):
    def __init__(self) -> None:
        super().__init__(6059, "Obligation id must be 0")

    code = 6059
    name = "InvalidObligationId"
    msg = "Obligation id must be 0"


class InvalidBorrowRateCurvePoint(ProgramError):
    def __init__(self) -> None:
        super().__init__(6060, "Invalid borrow rate curve point")

    code = 6060
    name = "InvalidBorrowRateCurvePoint"
    msg = "Invalid borrow rate curve point"


class InvalidUtilizationRate(ProgramError):
    def __init__(self) -> None:
        super().__init__(6061, "Invalid utilization rate")

    code = 6061
    name = "InvalidUtilizationRate"
    msg = "Invalid utilization rate"


class CannotSocializeObligationWithCollateral(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6062,
            "Obligation hasn't been fully liquidated and debt cannot be socialized.",
        )

    code = 6062
    name = "CannotSocializeObligationWithCollateral"
    msg = "Obligation hasn't been fully liquidated and debt cannot be socialized."


class ObligationEmpty(ProgramError):
    def __init__(self) -> None:
        super().__init__(6063, "Obligation has no borrows or deposits.")

    code = 6063
    name = "ObligationEmpty"
    msg = "Obligation has no borrows or deposits."


class WithdrawalCapReached(ProgramError):
    def __init__(self) -> None:
        super().__init__(6064, "Withdrawal cap is reached")

    code = 6064
    name = "WithdrawalCapReached"
    msg = "Withdrawal cap is reached"


class LastTimestampGreaterThanCurrent(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6065,
            "The last interval start timestamp is greater than the current timestamp",
        )

    code = 6065
    name = "LastTimestampGreaterThanCurrent"
    msg = "The last interval start timestamp is greater than the current timestamp"


class LiquidationSlippageError(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6066,
            "The reward amount is less than the minimum acceptable received collateral",
        )

    code = 6066
    name = "LiquidationSlippageError"
    msg = "The reward amount is less than the minimum acceptable received collateral"


class IsolatedAssetTierViolation(ProgramError):
    def __init__(self) -> None:
        super().__init__(6067, "Isolated Asset Tier Violation")

    code = 6067
    name = "IsolatedAssetTierViolation"
    msg = "Isolated Asset Tier Violation"


class InconsistentElevationGroup(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6068, "The obligation's elevation group and the reserve's are not the same"
        )

    code = 6068
    name = "InconsistentElevationGroup"
    msg = "The obligation's elevation group and the reserve's are not the same"


class InvalidElevationGroup(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6069,
            "The elevation group chosen for the reserve does not exist in the lending market",
        )

    code = 6069
    name = "InvalidElevationGroup"
    msg = "The elevation group chosen for the reserve does not exist in the lending market"


class InvalidElevationGroupConfig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6070, "The elevation group updated has wrong parameters set")

    code = 6070
    name = "InvalidElevationGroupConfig"
    msg = "The elevation group updated has wrong parameters set"


class UnhealthyElevationGroupLtv(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6071,
            "The current obligation must have most or all its debt repaid before changing the elevation group",
        )

    code = 6071
    name = "UnhealthyElevationGroupLtv"
    msg = "The current obligation must have most or all its debt repaid before changing the elevation group"


class ElevationGroupNewLoansDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6072,
            "Elevation group does not accept any new loans or any new borrows/withdrawals",
        )

    code = 6072
    name = "ElevationGroupNewLoansDisabled"
    msg = "Elevation group does not accept any new loans or any new borrows/withdrawals"


class ReserveDeprecated(ProgramError):
    def __init__(self) -> None:
        super().__init__(6073, "Reserve was deprecated, no longer usable")

    code = 6073
    name = "ReserveDeprecated"
    msg = "Reserve was deprecated, no longer usable"


class ReferrerAccountNotInitialized(ProgramError):
    def __init__(self) -> None:
        super().__init__(6074, "Referrer account not initialized")

    code = 6074
    name = "ReferrerAccountNotInitialized"
    msg = "Referrer account not initialized"


class ReferrerAccountMintMissmatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6075, "Referrer account mint does not match the operation reserve mint"
        )

    code = 6075
    name = "ReferrerAccountMintMissmatch"
    msg = "Referrer account mint does not match the operation reserve mint"


class ReferrerAccountWrongAddress(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6076, "Referrer account address is not a valid program address"
        )

    code = 6076
    name = "ReferrerAccountWrongAddress"
    msg = "Referrer account address is not a valid program address"


class ReferrerAccountReferrerMissmatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6077, "Referrer account referrer does not match the owner referrer"
        )

    code = 6077
    name = "ReferrerAccountReferrerMissmatch"
    msg = "Referrer account referrer does not match the owner referrer"


class ReferrerAccountMissing(ProgramError):
    def __init__(self) -> None:
        super().__init__(6078, "Referrer account missing for obligation with referrer")

    code = 6078
    name = "ReferrerAccountMissing"
    msg = "Referrer account missing for obligation with referrer"


class InsufficientReferralFeesToRedeem(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6079, "Insufficient referral fees to claim or no liquidity available"
        )

    code = 6079
    name = "InsufficientReferralFeesToRedeem"
    msg = "Insufficient referral fees to claim or no liquidity available"


class CpiDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6080, "CPI disabled for this instruction")

    code = 6080
    name = "CpiDisabled"
    msg = "CPI disabled for this instruction"


class ShortUrlNotAsciiAlphanumeric(ProgramError):
    def __init__(self) -> None:
        super().__init__(6081, "Referrer short_url is not ascii alphanumeric")

    code = 6081
    name = "ShortUrlNotAsciiAlphanumeric"
    msg = "Referrer short_url is not ascii alphanumeric"


class ReserveObsolete(ProgramError):
    def __init__(self) -> None:
        super().__init__(6082, "Reserve is marked as obsolete")

    code = 6082
    name = "ReserveObsolete"
    msg = "Reserve is marked as obsolete"


class ElevationGroupAlreadyActivated(ProgramError):
    def __init__(self) -> None:
        super().__init__(6083, "Obligation already part of the same elevation group")

    code = 6083
    name = "ElevationGroupAlreadyActivated"
    msg = "Obligation already part of the same elevation group"


class ObligationInDeprecatedReserve(ProgramError):
    def __init__(self) -> None:
        super().__init__(6084, "Obligation has a deposit in a deprecated reserve")

    code = 6084
    name = "ObligationInDeprecatedReserve"
    msg = "Obligation has a deposit in a deprecated reserve"


class ReferrerStateOwnerMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6085, "Referrer state owner does not match the given signer")

    code = 6085
    name = "ReferrerStateOwnerMismatch"
    msg = "Referrer state owner does not match the given signer"


class UserMetadataOwnerAlreadySet(ProgramError):
    def __init__(self) -> None:
        super().__init__(6086, "User metadata owner is already set")

    code = 6086
    name = "UserMetadataOwnerAlreadySet"
    msg = "User metadata owner is already set"


CustomError = typing.Union[
    InvalidMarketAuthority,
    InvalidMarketOwner,
    InvalidAccountOwner,
    InvalidAmount,
    InvalidConfig,
    InvalidSigner,
    InvalidAccountInput,
    MathOverflow,
    InsufficientLiquidity,
    ReserveStale,
    WithdrawTooSmall,
    WithdrawTooLarge,
    BorrowTooSmall,
    BorrowTooLarge,
    RepayTooSmall,
    LiquidationTooSmall,
    ObligationHealthy,
    ObligationStale,
    ObligationReserveLimit,
    InvalidObligationOwner,
    ObligationDepositsEmpty,
    ObligationBorrowsEmpty,
    ObligationDepositsZero,
    ObligationBorrowsZero,
    InvalidObligationCollateral,
    InvalidObligationLiquidity,
    ObligationCollateralEmpty,
    ObligationLiquidityEmpty,
    NegativeInterestRate,
    InvalidOracleConfig,
    InsufficientProtocolFeesToRedeem,
    FlashBorrowCpi,
    NoFlashRepayFound,
    InvalidFlashRepay,
    FlashRepayCpi,
    MultipleFlashBorrows,
    FlashLoansDisabled,
    SwitchboardV2Error,
    CouldNotDeserializeScope,
    PriceTooOld,
    PriceTooDivergentFromTwap,
    InvalidTwapPrice,
    GlobalEmergencyMode,
    InvalidFlag,
    PriceNotValid,
    PriceIsBiggerThanHeuristic,
    PriceIsLowerThanHeuristic,
    PriceIsZero,
    PriceConfidenceTooWide,
    IntegerOverflow,
    NoFarmForReserve,
    IncorrectInstructionInPosition,
    NoPriceFound,
    InvalidTwapConfig,
    InvalidPythPriceAccount,
    InvalidSwitchboardAccount,
    InvalidScopePriceAccount,
    ObligationCollateralLtvZero,
    InvalidObligationSeedsValue,
    InvalidObligationId,
    InvalidBorrowRateCurvePoint,
    InvalidUtilizationRate,
    CannotSocializeObligationWithCollateral,
    ObligationEmpty,
    WithdrawalCapReached,
    LastTimestampGreaterThanCurrent,
    LiquidationSlippageError,
    IsolatedAssetTierViolation,
    InconsistentElevationGroup,
    InvalidElevationGroup,
    InvalidElevationGroupConfig,
    UnhealthyElevationGroupLtv,
    ElevationGroupNewLoansDisabled,
    ReserveDeprecated,
    ReferrerAccountNotInitialized,
    ReferrerAccountMintMissmatch,
    ReferrerAccountWrongAddress,
    ReferrerAccountReferrerMissmatch,
    ReferrerAccountMissing,
    InsufficientReferralFeesToRedeem,
    CpiDisabled,
    ShortUrlNotAsciiAlphanumeric,
    ReserveObsolete,
    ElevationGroupAlreadyActivated,
    ObligationInDeprecatedReserve,
    ReferrerStateOwnerMismatch,
    UserMetadataOwnerAlreadySet,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: InvalidMarketAuthority(),
    6001: InvalidMarketOwner(),
    6002: InvalidAccountOwner(),
    6003: InvalidAmount(),
    6004: InvalidConfig(),
    6005: InvalidSigner(),
    6006: InvalidAccountInput(),
    6007: MathOverflow(),
    6008: InsufficientLiquidity(),
    6009: ReserveStale(),
    6010: WithdrawTooSmall(),
    6011: WithdrawTooLarge(),
    6012: BorrowTooSmall(),
    6013: BorrowTooLarge(),
    6014: RepayTooSmall(),
    6015: LiquidationTooSmall(),
    6016: ObligationHealthy(),
    6017: ObligationStale(),
    6018: ObligationReserveLimit(),
    6019: InvalidObligationOwner(),
    6020: ObligationDepositsEmpty(),
    6021: ObligationBorrowsEmpty(),
    6022: ObligationDepositsZero(),
    6023: ObligationBorrowsZero(),
    6024: InvalidObligationCollateral(),
    6025: InvalidObligationLiquidity(),
    6026: ObligationCollateralEmpty(),
    6027: ObligationLiquidityEmpty(),
    6028: NegativeInterestRate(),
    6029: InvalidOracleConfig(),
    6030: InsufficientProtocolFeesToRedeem(),
    6031: FlashBorrowCpi(),
    6032: NoFlashRepayFound(),
    6033: InvalidFlashRepay(),
    6034: FlashRepayCpi(),
    6035: MultipleFlashBorrows(),
    6036: FlashLoansDisabled(),
    6037: SwitchboardV2Error(),
    6038: CouldNotDeserializeScope(),
    6039: PriceTooOld(),
    6040: PriceTooDivergentFromTwap(),
    6041: InvalidTwapPrice(),
    6042: GlobalEmergencyMode(),
    6043: InvalidFlag(),
    6044: PriceNotValid(),
    6045: PriceIsBiggerThanHeuristic(),
    6046: PriceIsLowerThanHeuristic(),
    6047: PriceIsZero(),
    6048: PriceConfidenceTooWide(),
    6049: IntegerOverflow(),
    6050: NoFarmForReserve(),
    6051: IncorrectInstructionInPosition(),
    6052: NoPriceFound(),
    6053: InvalidTwapConfig(),
    6054: InvalidPythPriceAccount(),
    6055: InvalidSwitchboardAccount(),
    6056: InvalidScopePriceAccount(),
    6057: ObligationCollateralLtvZero(),
    6058: InvalidObligationSeedsValue(),
    6059: InvalidObligationId(),
    6060: InvalidBorrowRateCurvePoint(),
    6061: InvalidUtilizationRate(),
    6062: CannotSocializeObligationWithCollateral(),
    6063: ObligationEmpty(),
    6064: WithdrawalCapReached(),
    6065: LastTimestampGreaterThanCurrent(),
    6066: LiquidationSlippageError(),
    6067: IsolatedAssetTierViolation(),
    6068: InconsistentElevationGroup(),
    6069: InvalidElevationGroup(),
    6070: InvalidElevationGroupConfig(),
    6071: UnhealthyElevationGroupLtv(),
    6072: ElevationGroupNewLoansDisabled(),
    6073: ReserveDeprecated(),
    6074: ReferrerAccountNotInitialized(),
    6075: ReferrerAccountMintMissmatch(),
    6076: ReferrerAccountWrongAddress(),
    6077: ReferrerAccountReferrerMissmatch(),
    6078: ReferrerAccountMissing(),
    6079: InsufficientReferralFeesToRedeem(),
    6080: CpiDisabled(),
    6081: ShortUrlNotAsciiAlphanumeric(),
    6082: ReserveObsolete(),
    6083: ElevationGroupAlreadyActivated(),
    6084: ObligationInDeprecatedReserve(),
    6085: ReferrerStateOwnerMismatch(),
    6086: UserMetadataOwnerAlreadySet(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
