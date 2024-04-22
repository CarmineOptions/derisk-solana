import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


POSTGRES_USER = os.environ.get("POSTGRES_USER")
if POSTGRES_USER is None:
    raise ValueError("no POSTGRES_USER env var")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
if POSTGRES_PASSWORD is None:
    raise ValueError("no POSTGRES_PASSWORD env var")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
if POSTGRES_HOST is None:
    raise ValueError("no POSTGRES_HOST env var")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
if POSTGRES_DB is None:
    raise ValueError("no POSTGRES_DB env var")

CONN_STRING = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

# TODO: raise these limits
# currently using very small numbers
# to prevent DB performance issues
POOL_SIZE = 1
POOL_OVERFLOW = 5

engine = create_engine(CONN_STRING, pool_size=POOL_SIZE, max_overflow=POOL_OVERFLOW)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
