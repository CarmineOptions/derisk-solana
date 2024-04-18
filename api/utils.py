def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
