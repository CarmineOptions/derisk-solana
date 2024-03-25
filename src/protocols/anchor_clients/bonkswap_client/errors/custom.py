import typing
from anchorpy.error import ProgramError


class DeltaTooBig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6000, "Delta greater than provider's tokens")

    code = 6000
    name = "DeltaTooBig"
    msg = "Delta greater than provider's tokens"


class TokenUnderflow(ProgramError):
    def __init__(self) -> None:
        super().__init__(6001, "Token amount underflow")

    code = 6001
    name = "TokenUnderflow"
    msg = "Token amount underflow"


class WrongRatio(ProgramError):
    def __init__(self) -> None:
        super().__init__(6002, "Wrong tokens ratio")

    code = 6002
    name = "WrongRatio"
    msg = "Wrong tokens ratio"


class TooMuchShares(ProgramError):
    def __init__(self) -> None:
        super().__init__(6003, "Too much shares provided")

    code = 6003
    name = "TooMuchShares"
    msg = "Too much shares provided"


class SwapToBig(ProgramError):
    def __init__(self) -> None:
        super().__init__(6004, "Swap too big")

    code = 6004
    name = "SwapToBig"
    msg = "Swap too big"


class FeeExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6005, "Fee exceeded 100%")

    code = 6005
    name = "FeeExceeded"
    msg = "Fee exceeded 100%"


class ScalesNotEqual(ProgramError):
    def __init__(self) -> None:
        super().__init__(6007, "Scales have to be equal")

    code = 6007
    name = "ScalesNotEqual"
    msg = "Scales have to be equal"


class FeeExceededDeltaOut(ProgramError):
    def __init__(self) -> None:
        super().__init__(6008, "Fees exceeded delta_out")

    code = 6008
    name = "FeeExceededDeltaOut"
    msg = "Fees exceeded delta_out"


class PriceLimitExceeded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6009, "Price limit exceeded")

    code = 6009
    name = "PriceLimitExceeded"
    msg = "Price limit exceeded"


class MintMismatch(ProgramError):
    def __init__(self) -> None:
        super().__init__(6010, "Mint mismatch")

    code = 6010
    name = "MintMismatch"
    msg = "Mint mismatch"


class TokensAreTheSame(ProgramError):
    def __init__(self) -> None:
        super().__init__(6011, "Tokens are the same")

    code = 6011
    name = "TokensAreTheSame"
    msg = "Tokens are the same"


class WrongFarm(ProgramError):
    def __init__(self) -> None:
        super().__init__(6012, "Cannot add supply to wrong farm")

    code = 6012
    name = "WrongFarm"
    msg = "Cannot add supply to wrong farm"


class RewardsExceedingSupply(ProgramError):
    def __init__(self) -> None:
        super().__init__(6013, "Cannot withdraw rewards exceeding supply left")

    code = 6013
    name = "RewardsExceedingSupply"
    msg = "Cannot withdraw rewards exceeding supply left"


class FarmNotEnded(ProgramError):
    def __init__(self) -> None:
        super().__init__(6014, "Farm has not ended, cannot add additional rewards")

    code = 6014
    name = "FarmNotEnded"
    msg = "Farm has not ended, cannot add additional rewards"


class ZeroAmount(ProgramError):
    def __init__(self) -> None:
        super().__init__(6015, "Must provide a nonzero amount")

    code = 6015
    name = "ZeroAmount"
    msg = "Must provide a nonzero amount"


class InvariantDecreased(ProgramError):
    def __init__(self) -> None:
        super().__init__(6016, "Invariant has changed")

    code = 6016
    name = "InvariantDecreased"
    msg = "Invariant has changed"


CustomError = typing.Union[
    DeltaTooBig,
    TokenUnderflow,
    WrongRatio,
    TooMuchShares,
    SwapToBig,
    FeeExceeded,
    ScalesNotEqual,
    FeeExceededDeltaOut,
    PriceLimitExceeded,
    MintMismatch,
    TokensAreTheSame,
    WrongFarm,
    RewardsExceedingSupply,
    FarmNotEnded,
    ZeroAmount,
    InvariantDecreased,
]
CUSTOM_ERROR_MAP: dict[int, CustomError] = {
    6000: DeltaTooBig(),
    6001: TokenUnderflow(),
    6002: WrongRatio(),
    6003: TooMuchShares(),
    6004: SwapToBig(),
    6005: FeeExceeded(),
    6007: ScalesNotEqual(),
    6008: FeeExceededDeltaOut(),
    6009: PriceLimitExceeded(),
    6010: MintMismatch(),
    6011: TokensAreTheSame(),
    6012: WrongFarm(),
    6013: RewardsExceedingSupply(),
    6014: FarmNotEnded(),
    6015: ZeroAmount(),
    6016: InvariantDecreased(),
}


def from_code(code: int) -> typing.Optional[CustomError]:
    maybe_err = CUSTOM_ERROR_MAP.get(code)
    if maybe_err is None:
        return None
    return maybe_err
