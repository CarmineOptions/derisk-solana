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
    Boolean
)
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
SCHEMA = 'lenders'


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


class ParsedTransactions(Base):
    __abstract__ = True
    __tablename__ = "parsed_transactions"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String, nullable=True)
    instruction_name = Column(String, nullable=True)
    event_name = Column(String, nullable=True)
    event_number = Column(String, nullable=True)

    position = Column(SQLEnum('asset', 'liability', name='sqlenum', schema=SCHEMA), nullable=True)
    token = Column(String, nullable=True)
    amount = Column(BigInteger, nullable=True)
    amount_decimal = Column(Integer, nullable=True)

    bank = Column(String, nullable=True)
    account = Column(String, nullable=True)
    signer = Column(String, nullable=True)

    context = Column(String, nullable=True)

    block = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<ParsedTransactions(\n   id={self.id}, \n   transaction_id='{self.transaction_id}',\n" \
               f"\n   instruction_name='{self.instruction_name}', \n   event_name='{self.event_name}',\n " \
               f"\n   position='{self.position}', \n   token='{self.token}'," \
               f"\n   amount={self.amount}, \n   amount_decimal={self.amount_decimal}, \n   account='{self.account}', " \
               f"\n   signer='{self.signer}', \n   created_at={self.created_at}"


class LendingAccounts(Base):
    __abstract__ = True
    __tablename__ = "lending_accounts"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, autoincrement=True)
    authority = Column(String, nullable=True)
    address = Column(String, nullable=True)
    group = Column(String, nullable=True)
    block = Column(BigInteger, nullable=True)
    created_at = Column(BigInteger, nullable=False)

    def __repr__(self):
        return f"<LendingAccounts(\n   id={self.id}, \n   authority='{self.authority}', " \
               f"\n   address='{self.address}', \n   group='{self.group}',\n   created_at={self.created_at})>"


class MarginfiParsedTransactions(ParsedTransactions):
    __tablename__ = "marginfi_parsed_transactions"

    __table_args__ = (
        Index("ix_marginfi_parsed_transactions_transaction_id", "transaction_id"),
        Index("ix_marginfi_parsed_transactions_instruction_name", "instruction_name"),
        Index("ix_marginfi_parsed_transactions_event_name", "event_name"),
        Index("ix_marginfi_parsed_transactions_account", "account"),
        Index("ix_marginfi_parsed_transactions_token", "token"),
        {"schema": SCHEMA},
    )


class MarginfiLendingAccounts(LendingAccounts):
    __tablename__ = "marginfi_lending_accounts"
    __table_args__ = (
        Index("ix_marginfi_lending_accounts_address", "address"),
        Index("ix_marginfi_lending_accounts_group", "group"),
        Index("ix_marginfi_lending_accounts_authority", "authority"),
        {"schema": SCHEMA}
    )


class KaminoParsedTransactions(ParsedTransactions):
    __tablename__ = "kamino_parsed_transactions"
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)
    obligation = Column(String, nullable=True)
    __table_args__ = (
        Index("ix_kamino_parsed_transactions_transaction_id", "transaction_id"),
        Index("ix_kamino_parsed_transactions_instruction_name", "instruction_name"),
        Index("ix_kamino_parsed_transactions_event_name", "event_name"),
        Index("ix_kamino_parsed_transactions_account", "account"),
        Index("ix_kamino_parsed_transactions_token", "token"),
        {"schema": SCHEMA},
    )

    def __repr__(self):
        return f"<ParsedTransactions(\n   id={self.id}, \n   transaction_id='{self.transaction_id}'," \
               f"\n   instruction_name='{self.instruction_name}', \n   event_name='{self.event_name}', " \
               f"\n   event_num = {self.event_number}" \
               f"\n   position='{self.position}', \n   token='{self.token}'," \
               f"\n   source='{self.source}', \n   destination='{self.destination}'," \
               f"\n   amount={self.amount}, \n   amount_decimal={self.amount_decimal}, \n   account='{self.account}', " \
               f"\n   signer='{self.signer}', \n   created_at={self.created_at}, \n   obligation={self.obligation}"


class KaminoLendingAccounts(LendingAccounts):
    __tablename__ = "kamino_lending_accounts"
    __table_args__ = (
        Index("ix_kamino_lending_accounts_address", "address"),
        Index("ix_kamino_lending_accounts_group", "group"),
        Index("ix_kamino_lending_accounts_authority", "authority"),
        {"schema": SCHEMA}
    )


class TransactionsList(Base):
    __abstract__ = True
    __tablename__ = 'hist_transaction_list'
    __table_args__ = {"schema": SCHEMA}

    signature = Column(String, primary_key=True)
    block_time = Column(BigInteger)
    is_parsed = Column(Boolean, default=False)


class MarginfiTransactionsList(TransactionsList):
    __tablename__ = 'marginfi_hist_transaction_list'
    __table_args__ = (
        Index('idx_marginfi_transaction_list_signature', 'signature'),
        {"schema": SCHEMA},
    )


class KaminoTransactionsList(TransactionsList):
    __tablename__ = 'kamino_hist_transaction_list'
    __table_args__ = (
        Index('idx_kamino_transaction_list_signature', 'signature'),
        {"schema": SCHEMA},
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
