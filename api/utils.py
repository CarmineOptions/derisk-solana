from sqlalchemy.inspection import inspect


def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def to_dict(instance):
    """
    Convert an SQLAlchemy model instance into a dictionary.
    """
    return {
        c.key: getattr(instance, c.key) for c in inspect(instance).mapper.column_attrs
    }
