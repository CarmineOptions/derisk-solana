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
    PrimaryKeyConstraint,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import Enum as SQLEnum
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY

from db.utils import check_bigint

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
SCHEMA = 'public'


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
    SIGNATURE = 'signature'


class TransactionStatusWithSignature(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    source = Column(String, ForeignKey(f'{SCHEMA}.protocols.public_key'), nullable=False)
    signature = Column(String, nullable=False)
    slot = Column(BigInteger, nullable=False)
    block_time = Column(BigInteger, nullable=False)
    transaction_data = Column(String, nullable=True)  # column to store json with transaction's data
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
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA}.transactions.id'), nullable=False)


class TransactionStatusMemo(Base):
    __tablename__ = "tx_status_memo"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True)
    memo_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA}.transactions.id'), nullable=False)


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
        PrimaryKeyConstraint("dex", "token_x_address", "token_y_address", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger)
    dex = Column(String, nullable=False)
    market_address = Column(String)
    token_x_amount = Column(BigInteger, default=-1)
    token_y_amount = Column(BigInteger, default=-1)
    token_x_address = Column(String)
    token_y_address = Column(String)
    additional_info = Column(String)

    def __repr__(self):
        return (
            "AmmLiqudity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"market_address={self.market_address},"
            f"token_x_amount={self.token_x_amount },"
            f"token_y_amount={self.token_y_amount },"
            f"token_x_address={self.token_x_address},"
            f"token_y_address={self.token_y_address},"
            f"additional_info={self.additional_info},)"
        )


class DexNormalizedLiquidity(Base):
    __tablename__ = 'dex_normalized_liquidity'
    __table_args__ = (
        PrimaryKeyConstraint("dex", "token_x_address", "token_y_address", "market_address", "timestamp"),
        {"schema": SCHEMA},
    )

    timestamp = Column(BigInteger, nullable=False)
    dex = Column(String, nullable=False)
    market_address = Column(String, nullable=False)
    token_x_address = Column(String, nullable=False)
    token_y_address = Column(String, nullable=False)
    bids = Column(PG_ARRAY(Float), nullable=False)
    asks = Column(PG_ARRAY(Float), nullable=False)

    def __repr__(self):
        return (
            "DexNormalizedLiquidity("
            f"timestamp={self.timestamp},"
            f"dex={self.dex},"
            f"market_address={self.market_address},"
            f"token_x_address={self.token_x_address},"
            f"token_y_address={self.token_y_address},"
            f"bids={self.bids},"
            f"asks={self.asks})"
        )



class Protocols(Base):
    __tablename__ = 'protocols'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    public_key = Column(String, unique=True, nullable=False)
    # watershed block, block that we assign as divider of historical and current data,
    # to define what collection stream to use for their collection.
    watershed_block = Column(Integer, nullable=False)
    last_block_collected = Column(Integer, nullable=True)


if __name__ == "__main__":
    # create the database engine
    ENGINE = create_engine(CONN_STRING)
    # create schema
    connection = ENGINE.raw_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")

    Base.metadata.create_all(ENGINE)
