import logging
import os
import sys

import psycopg2


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

PG_CONNECTION_STRING = f"dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD} host={POSTGRES_HOST}"

if PG_CONNECTION_STRING is None:
    raise ValueError("No PG connection string, aborting.")


def establish_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST
    )