"""
Module containing functionality related to Postgres DB used throughout the repo.
"""
import os
from enum import Enum

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    ForeignKey,
    Text,
    Boolean,
    PrimaryKeyConstraint,
    Float,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

Base = declarative_base()

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

CONN_STRING = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"


SCHEMA = "public"

def get_db_session() -> Session:
    """
    Initializes a session -> it must be closed manually!

    Returns:
        Returns a database session object that can be used to interact with the database.
    """
    session = sessionmaker(bind=create_engine(CONN_STRING))
    return session()


class CollectionStreamTypes(Enum):
    HISTORICAL = 'historical'
    CURRENT = 'current'


class TransactionStatusWithSignature(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    slot = Column(BigInteger, nullable=False)
    block_time = Column(BigInteger, nullable=False)
    tx_raw = Column(String, nullable=True)  # column to store json with transaction's data
    collection_stream = Column(SQLEnum(CollectionStreamTypes, name='collection_stream_types'), nullable=True)

    __table_args__ = (
        Index("ix_transactions_slot", "slot"),
        Index("ix_transactions_block_time", "block_time"),
        Index("ix_transactions_signature", "signature"),
        Index("ix_transactions_source", "source"),
        {"schema": SCHEMA},
    )

    def __repr__(self):
        return (
            f"<TransactionStatusWithSignature(signature='{self.signature}',"
            f" slot={self.slot}, block_time={self.block_time} )>"
        )


class TransactionStatusError(Base):
    __tablename__ = "tx_status_errors"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True)
    error_body = Column(String, nullable=False)
    tx_signatures_id = Column(
        Integer, ForeignKey(f"{SCHEMA}.tx_signatures.id"), nullable=False
    )


class TransactionStatusMemo(Base):
    __tablename__ = "tx_status_memo"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True)
    memo_body = Column(String, nullable=False)
    tx_signatures_id = Column(
        Integer, ForeignKey(f"{SCHEMA}.tx_signatures.id"), nullable=False
    )


class CLOBLiqudity(Base):
    __tablename__ = "orderbook_liquidity"
    __table_args__ = (
        PrimaryKeyConstraint("dex", "pair", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger, nullable=False)
    dex = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    market_address = Column(String, nullable=False)
    bids = Column(PG_ARRAY(Float), nullable=False)
    asks = Column(PG_ARRAY(Float), nullable=False)

    def __repr__(self):
        return (
            "CLOBLiqudity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"pair={self.pair},"
            f"market_address={self.market_address},"
            f"bids={self.bids},"
            f"asks={self.asks})"
        )


class AmmLiquidity(Base):
    __tablename__ = 'amm_liquidity'
    __table_args__ = (
        PrimaryKeyConstraint("dex", "pair", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger)
    dex = Column(String, nullable=False)
    pair = Column(String, nullable=False)
    market_address = Column(String)
    token_x = Column(BigInteger, default=-1)
    token_y = Column(BigInteger, default=-1)
    token_x_decimals = Column(Integer, default=-1)
    token_y_decimals = Column(Integer, default=-1)
    additional_info = Column(String)


if __name__ == "__main__":
    # create the database engine
    ENGINE = create_engine(CONN_STRING)
    # create schema
    connection = ENGINE.raw_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")

    Base.metadata.create_all(ENGINE)
