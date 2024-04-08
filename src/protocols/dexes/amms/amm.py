from abc import ABC, abstractmethod
from typing import Any


class Amm(ABC):
    pools: list[Any]
    timestamp: int

    def __init__(self):
        pass

    @abstractmethod
    async def get_pools(self):
        """
        Fetch pools data.
        """
        raise NotImplementedError("Implement me!")

    def store_pools(self):
        """
        Save pools data to database.
        """
        for pool in self.pools:
            self.store_pool(pool)

    @abstractmethod
    def store_pool(self, pool: Any) -> None:
        """
        Save pool data to database.
        """
        raise NotImplementedError("Implement me!")

    @staticmethod
    def convert_to_big_integer_and_decimals(
        amount_str: str | None,
    ) -> tuple[int | None, int | None]:
        """
        Convert string containing numerical value into integer and number of decimals.
        """
        if amount_str is None:
            return None, None
        # Check if there is a decimal point in the amount_str
        if "." in amount_str:
            # Split the string into whole and fractional parts
            whole_part, fractional_part = amount_str.split(".")
            # Calculate the number of decimals as the length of the fractional part
            decimals = len(fractional_part)
            # Remove the decimal point and convert the remaining string to an integer
            amount_big_integer = int(whole_part + fractional_part)

            return amount_big_integer, decimals

        return int(amount_str), 0
