import os

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Index


Base = declarative_base()

DB_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")

SCHEMA = 'public'
DRIVERS = "postgresql+psycopg2://"
CONN_STRING = DRIVERS + f"{DB_CONNECTION_STRING.replace('postgres://', '')}"


def get_db_session() -> Session:
    """
    Initializes a session -> it must be closed manually!

    Returns:
        Returns a database session object that can be used to interact with the database.
    """
    session = sessionmaker(bind=create_engine(CONN_STRING))
    return session()


class TransactionStatusWithSignature(Base):
    __tablename__ = 'tx_signatures'

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    signature = Column(String, nullable=False)
    slot = Column(BigInteger, nullable=False)
    block_time = Column(BigInteger, nullable=False)
    tx_raw = Column(String, nullable=True)  # column to store json with transaction's data

    __table_args__ = (
        Index('ix_transactions_slot', 'slot'),
        Index('ix_transactions_block_time', 'block_time'),
        Index('ix_transactions_signature', 'signature'),
        Index('ix_transactions_source', 'source'),
        {'schema': SCHEMA}
    )

    def __repr__(self):
        return f"<TransactionStatusWithSignature(signature='{self.signature}'," \
               f" slot={self.slot}, block_time={self.block_time} )>"


class TransactionStatusError(Base):
    __tablename__ = 'tx_status_errors'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    error_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA}.tx_signatures.id'), nullable=False)


class TransactionStatusMemo(Base):
    __tablename__ = 'tx_status_memo'
    __table_args__ = {'schema': SCHEMA}

    id = Column(Integer, primary_key=True)
    memo_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA}.tx_signatures.id'), nullable=False)


class TransactionsProcessed(Base):
    __tablename__ = 'tx_processed'

    id = Column(Integer, primary_key=True)
    slot = Column(BigInteger, nullable=False)
    block_time = Column(BigInteger, nullable=False)
    program_id = Column(String, nullable=False)
    event_name = Column(Text, nullable=False)
    event_data = Column(JSONB, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey(f'{SCHEMA}.tx_signatures.id'), nullable=False)

    __table_args__ = (
        Index('ix_processed_slot', 'slot'),
        Index('ix_processed_block_time', 'block_time'),
        Index('ix_processed_event_name', 'event_name'),
        Index('ix_processed_program_id', 'program_id'),
        {'schema': SCHEMA}
    )


# # TODO add columns
# class ProcessedData(Base):
#     __tablename__ = 'processed_data'
#     id = Column(Integer, primary_key=True)


if __name__ == "__main__":
    # create the database engine
    ENGINE = create_engine(CONN_STRING)
    # create schema
    connection = ENGINE.raw_connection()
    cursor = connection.cursor()
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};")
    connection.commit()
    cursor.close()
    connection.close()

    Base.metadata.create_all(ENGINE)
