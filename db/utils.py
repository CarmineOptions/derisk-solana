
def check_bigint(value: int) -> int:
    """
    Checks if the given integer value fits within the PostgreSQL bigint range.

    Args:
            value (int): The integer value to check.

    Returns:
            int: Returns -2 if the value exceeds the PostgreSQL bigint range
    """
    # Define the bigint limits in PostgreSQL
    bigint_min = -9223372036854775808
    bigint_max = 9223372036854775807

    # Check if the value is within the bigint range
    if not bigint_min <= value <= bigint_max:
        return -2  # Return -2 if the value is outside the bigint range
    return value
