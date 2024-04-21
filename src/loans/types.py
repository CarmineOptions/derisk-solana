import collections
import decimal


MAX_ROUNDING_ERRORS = collections.defaultdict(
    lambda: decimal.Decimal("0"),
)


class Portfolio(collections.defaultdict):
    """A class that describes holdings of tokens."""

    # TODO: Update the values.
    MAX_ROUNDING_ERRORS: collections.defaultdict = MAX_ROUNDING_ERRORS

    def __init__(self, **kwargs) -> None:
        assert all(isinstance(x, str) for x in kwargs.keys())
        assert all(isinstance(x, decimal.Decimal) for x in kwargs.values())
        super().__init__(decimal.Decimal, **kwargs)

    # TODO: Find a better solution to fix the discrepancies.
    def round_small_value_to_zero(self, token: str):
        if self[token] < self.MAX_ROUNDING_ERRORS[token]:
            self[token] = decimal.Decimal("0")

    def increase_value(self, token: str, value: decimal.Decimal):
        self[token] += value
        self.round_small_value_to_zero(token=token)

    def set_value(self, token: str, value: decimal.Decimal):
        self[token] = value
        self.round_small_value_to_zero(token=token)
