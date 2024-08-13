import os
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


def get_db_connection_string() -> str:
    user = os.environ.get("POSTGRES_USER")
    if user is None:
        raise ValueError("no POSTGRES_USER env var")
    password = os.environ.get("POSTGRES_PASSWORD")
    if password is None:
        # if password not provided check for password file
        POSTGRES_PASSWORD_FILE = os.environ.get("POSTGRES_PASSWORD_FILE")
        if POSTGRES_PASSWORD_FILE is None:
            raise ValueError("no POSTGRES_PASSWORD env var")
        with open(POSTGRES_PASSWORD_FILE, "r") as secret_file:
            password = secret_file.read().strip()
    host = os.environ.get("POSTGRES_HOST")
    if host is None:
        raise ValueError("no POSTGRES_HOST env var")
    db = os.environ.get("POSTGRES_DB")
    if db is None:
        raise ValueError("no POSTGRES_DB env var")

    connection_string = f"postgresql://{user}:{password}@{host}/{db}"

    return connection_string
