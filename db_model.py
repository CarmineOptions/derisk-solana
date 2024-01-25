import os

from sqlalchemy import create_engine, Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import Index


Base = declarative_base()

DB_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING")

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

    __table_args__ = (
        Index('ix_transactions_slot', 'slot'),
        Index('ix_transactions_block_time', 'block_time'),
    )

    def __repr__(self):
        return f"<TransactionStatusWithSignature(signature='{self.signature}'," \
               f" slot={self.slot}, block_time={self.block_time} )>"


class TransactionStatusError(Base):
    __tablename__ = 'tx_status_errors'

    id = Column(Integer, primary_key=True)
    error_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey('tx_signatures.id'), nullable=False)


class TransactionStatusMemo(Base):
    __tablename__ = 'tx_status_memo'

    id = Column(Integer, primary_key=True)
    memo_body = Column(String, nullable=False)
    tx_signatures_id = Column(Integer, ForeignKey('tx_signatures.id'), nullable=False)


if __name__ == "__main__":
    # create the database engine
    ENGINE = create_engine(CONN_STRING)
    
    Base.metadata.create_all(ENGINE)
