import logging
import os

import psycopg2



PG_CONNECTION_STRING = os.environ.get("PG_CONNECTION_STRING")
if PG_CONNECTION_STRING is None:
    logging.info("No PG connection string, aborting.")
    exit(1)



def establish_connection() -> psycopg2.extensions.connection:
    return psycopg2.connect(PG_CONNECTION_STRING)