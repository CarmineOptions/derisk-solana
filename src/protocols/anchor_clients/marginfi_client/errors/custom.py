import typing
from anchorpy.error import ProgramError


class MathError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Math error")

    code = 6000
    name = "MathError"
    msg = "Math error"


class BankNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Invalid bank index")

    code = 6001
    name = "BankNotFound"
    msg = "Invalid bank index"


class LendingAccountBalanceNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Lending account balance not found")

    code = 6002
    name = "LendingAccountBalanceNotFound"
    msg = "Lending account balance not found"


class BankAssetCapacityExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Bank deposit capacity exceeded")

    code = 6003
    name = "BankAssetCapacityExceeded"
    msg = "Bank deposit capacity exceeded"


class InvalidTransfer(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Invalid transfer")

    code = 6004
    name = "InvalidTransfer"
    msg = "Invalid transfer"


class MissingPythOrBankAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Missing Pyth or Bank account")

    code = 6005
    name = "MissingPythOrBankAccount"
    msg = "Missing Pyth or Bank account"


class MissingPythAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6006, "Missing Pyth account")

    code = 6006
    name = "MissingPythAccount"
    msg = "Missing Pyth account"


class InvalidOracleAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Invalid Pyth account")

    code = 6007
    name = "InvalidOracleAccount"
    msg = "Invalid Pyth account"


class MissingBankAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Missing Bank account")

    code = 6008
    name = "MissingBankAccount"
    msg = "Missing Bank account"


class InvalidBankAccount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Invalid Bank account")

    code = 6009
    name = "InvalidBankAccount"
    msg = "Invalid Bank account"


class BadAccountHealth(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Bad account health")

    code = 6010
    name = "BadAccountHealth"
    msg = "Bad account health"


class LendingAccountBalanceSlotsFull(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Lending account balance slots are full")

    code = 6011
    name = "LendingAccountBalanceSlotsFull"
    msg = "Lending account balance slots are full"


class BankAlreadyExists(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Bank already exists")

    code = 6012
    name = "BankAlreadyExists"
    msg = "Bank already exists"


class IllegalLiquidation(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "Illegal liquidation")

    code = 6013
    name = "IllegalLiquidation"
    msg = "Illegal liquidation"


class AccountNotBankrupt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Account is not bankrupt")

    code = 6014
    name = "AccountNotBankrupt"
    msg = "Account is not bankrupt"


class BalanceNotBadDebt(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Account balance is not bad debt")

    code = 6015
    name = "BalanceNotBadDebt"
    msg = "Account balance is not bad debt"


class InvalidConfig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Invalid group config")

    code = 6016
    name = "InvalidConfig"
    msg = "Invalid group config"


class StaleOracle(ProgramError):
    def __init__(self) -> None:
        super().__init__(6017, "Stale oracle data")

    code = 6017
    name = "StaleOracle"
    msg = "Stale oracle data"


class BankPaused(ProgramError):
    def __init__(self) -> None:
        super().__init__(6018, "Bank paused")

    code = 6018
    name = "BankPaused"
    msg = "Bank paused"


class BankReduceOnly(ProgramError):
    def __init__(self) -> None:
        super().__init__(6019, "Bank is ReduceOnly mode")

    code = 6019
    name = "BankReduceOnly"
    msg = "Bank is ReduceOnly mode"


class BankAccoutNotFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6020, "Bank is missing")

    code = 6020
    name = "BankAccoutNotFound"
    msg = "Bank is missing"


class OperationDepositOnly(ProgramError):
    def __init__(self) -> None:
        super().__init__(6021, "Operation is deposit-only")

    code = 6021
    name = "OperationDepositOnly"
    msg = "Operation is deposit-only"


class OperationWithdrawOnly(ProgramError):
    def __init__(self) -> None:
        super().__init__(6022, "Operation is withdraw-only")

    code = 6022
    name = "OperationWithdrawOnly"
    msg = "Operation is withdraw-only"


class OperationBorrowOnly(ProgramError):
    def __init__(self) -> None:
        super().__init__(6023, "Operation is borrow-only")

    code = 6023
    name = "OperationBorrowOnly"
    msg = "Operation is borrow-only"


class OperationRepayOnly(ProgramError):
    def __init__(self) -> None:
        super().__init__(6024, "Operation is repay-only")

    code = 6024
    name = "OperationRepayOnly"
    msg = "Operation is repay-only"


class NoAssetFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6025, "No asset found")

    code = 6025
    name = "NoAssetFound"
    msg = "No asset found"


class NoLiabilityFound(ProgramError):
    def __init__(self) -> None:
        super().__init__(6026, "No liability found")

    code = 6026
    name = "NoLiabilityFound"
    msg = "No liability found"


class InvalidOracleSetup(ProgramError):
    def __init__(self) -> None:
        super().__init__(6027, "Invalid oracle setup")

    code = 6027
    name = "InvalidOracleSetup"
    msg = "Invalid oracle setup"


class IllegalUtilizationRatio(ProgramError):
    def __init__(self) -> None:
        super().__init__(6028, "Invalid bank utilization ratio")

    code = 6028
    name = "IllegalUtilizationRatio"
    msg = "Invalid bank utilization ratio"


class BankLiabilityCapacityExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6029, "Bank borrow cap exceeded")

    code = 6029
    name = "BankLiabilityCapacityExceeded"
    msg = "Bank borrow cap exceeded"


class InvalidPrice(ProgramError):
    def __init__(self) -> None:
        super().__init__(6030, "Invalid Price")

    code = 6030
    name = "InvalidPrice"
    msg = "Invalid Price"


class IsolatedAccountIllegalState(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6031,
            "Account can have only one liablity when account is under isolated risk",
        )

    code = 6031
    name = "IsolatedAccountIllegalState"
    msg = "Account can have only one liablity when account is under isolated risk"


class EmissionsAlreadySetup(ProgramError):
    def __init__(self) -> None:
        super().__init__(6032, "Emissions already setup")

    code = 6032
    name = "EmissionsAlreadySetup"
    msg = "Emissions already setup"


class OracleNotSetup(ProgramError):
    def __init__(self) -> None:
        super().__init__(6033, "Oracle is not set")

    code = 6033
    name = "OracleNotSetup"
    msg = "Oracle is not set"


class InvalidSwitchboardDecimalConversion(ProgramError):
    def __init__(self) -> None:
        super().__init__(6034, "Invalid swithcboard decimal conversion")

    code = 6034
    name = "InvalidSwitchboardDecimalConversion"
    msg = "Invalid swithcboard decimal conversion"


class CannotCloseOutstandingEmissions(ProgramError):
    def __init__(self) -> None:
        super().__init__(6035, "Cannot close balance because of outstanding emissions")

    code = 6035
    name = "CannotCloseOutstandingEmissions"
    msg = "Cannot close balance because of outstanding emissions"


class EmissionsUpdateError(ProgramError):
    def __init__(self) -> None:
        super().__init__(6036, "Update emissions error")

    code = 6036
    name = "EmissionsUpdateError"
    msg = "Update emissions error"


class AccountDisabled(ProgramError):
    def __init__(self) -> None:
        super().__init__(6037, "Account disabled")

    code = 6037
    name = "AccountDisabled"
    msg = "Account disabled"


class AccountTempActiveBalanceLimitExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(
            6038,
            "Account can't temporarily open 3 balances, please close a balance first",
        )

    code = 6038
    name = "AccountTempActiveBalanceLimitExceeded"
    msg = "Account can't temporarily open 3 balances, please close a balance first"


class AccountInFlashloan(ProgramError):
    def __init__(self) -> None:
        super().__init__(6039, "Illegal action during flashloan")

    code = 6039
    name = "AccountInFlashloan"
    msg = "Illegal action during flashloan"


class IllegalFlashloan(ProgramError):
    def __init__(self) -> None:
        super().__init__(6040, "Illegal flashloan")

    code = 6040
    name = "IllegalFlashloan"
    msg = "Illegal flashloan"


class IllegalFlag(ProgramError):
    def __init__(self) -> None:
        super().__init__(6041, "Illegal flag")

    code = 6041
    name = "IllegalFlag"
    msg = "Illegal flag"


class IllegalBalanceState(ProgramError):
    def __init__(self) -> None:
        super().__init__(6042, "Illegal balance state")

    code = 6042
    name = "IllegalBalanceState"
    msg = "Illegal balance state"


class IllegalAccountAuthorityTransfer(ProgramError):
    def __init__(self) -> None:
        super().__init__(6043, "Illegal account authority transfer")

    code = 6043
    name = "IllegalAccountAuthorityTransfer"
    msg = "Illegal account authority transfer"


CustomError = typing.Union[
    MathError,
    BankNotFound,
    LendingAccountBalanceNotFound,
    BankAssetCapacityExceeded,
    InvalidTransfer,
    MissingPythOrBankAccount,
    MissingPythAccount,
    InvalidOracleAccount,
    MissingBankAccount,
    InvalidBankAccount,
    BadAccountHealth,
    LendingAccountBalanceSlotsFull,
    BankAlreadyExists,
    IllegalLiquidation,
    AccountNotBankrupt,
    BalanceNotBadDebt,
    InvalidConfig,
    StaleOracle,
    BankPaused,
    BankReduceOnly,
    BankAccoutNotFound,
    OperationDepositOnly,
    OperationWithdrawOnly,
    OperationBorrowOnly,
    OperationRepayOnly,
    NoAssetFound,
    NoLiabilityFound,
    InvalidOracleSetup,
    IllegalUtilizationRatio,
    BankLiabilityCapacityExceeded,
    InvalidPrice,
    IsolatedAccountIllegalState,
    EmissionsAlreadySetup,
    OracleNotSetup,
    InvalidSwitchboardDecimalConversion,
    CannotCloseOutstandingEmissions,
    EmissionsUpdateError,
    AccountDisabled,
    AccountTempActiveBalanceLimitExceeded,
    AccountInFlashloan,
    IllegalFlashloan,
    IllegalFlag,
    IllegalBalanceState,
    IllegalAccountAuthorityTransfer,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: MathError(),
    6001: BankNotFound(),
    6002: LendingAccountBalanceNotFound(),
    6003: BankAssetCapacityExceeded(),
    6004: InvalidTransfer(),
    6005: MissingPythOrBankAccount(),
    6006: MissingPythAccount(),
    6007: InvalidOracleAccount(),
    6008: MissingBankAccount(),
    6009: InvalidBankAccount(),
    6010: BadAccountHealth(),
    6011: LendingAccountBalanceSlotsFull(),
    6012: BankAlreadyExists(),
    6013: IllegalLiquidation(),
    6014: AccountNotBankrupt(),
    6015: BalanceNotBadDebt(),
    6016: InvalidConfig(),
    6017: StaleOracle(),
    6018: BankPaused(),
    6019: BankReduceOnly(),
    6020: BankAccoutNotFound(),
    6021: OperationDepositOnly(),
    6022: OperationWithdrawOnly(),
    6023: OperationBorrowOnly(),
    6024: OperationRepayOnly(),
    6025: NoAssetFound(),
    6026: NoLiabilityFound(),
    6027: InvalidOracleSetup(),
    6028: IllegalUtilizationRatio(),
    6029: BankLiabilityCapacityExceeded(),
    6030: InvalidPrice(),
    6031: IsolatedAccountIllegalState(),
    6032: EmissionsAlreadySetup(),
    6033: OracleNotSetup(),
    6034: InvalidSwitchboardDecimalConversion(),
    6035: CannotCloseOutstandingEmissions(),
    6036: EmissionsUpdateError(),
    6037: AccountDisabled(),
    6038: AccountTempActiveBalanceLimitExceeded(),
    6039: AccountInFlashloan(),
    6040: IllegalFlashloan(),
    6041: IllegalFlag(),
    6042: IllegalBalanceState(),
    6043: IllegalAccountAuthorityTransfer(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
