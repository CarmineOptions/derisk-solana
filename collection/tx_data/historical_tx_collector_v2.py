"""
Module for transaction collection using `get_transaction()` instead of `get_block()`.
"""
import asyncio
import logging
import os
import time
import traceback

from solana.exceptions import SolanaRpcException
from solana.rpc.core import RPCException
from solders.errors import SerdeJSONError
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Index
)

import db
from src.collection.shared.generic_collector import log_performance_time
from src.collection.tx_data.historical_data_collector import HistoricalTXCollector

LOG = logging.getLogger(__name__)
BATCH_SIZE = 500
OFFSET = os.getenv("OFFSET", "0")


class MfTemp(db.Base):
    __tablename__ = 'mf_tmp'

    id = Column(Integer, primary_key=True)
    signature = Column(String, nullable=False)
    is_collected = Column(Boolean, default=False)

    __table_args__ = (
        Index("ix_mf_signature", "signature"),
        {"schema": db.SCHEMA},
    )

class SolTemp(db.Base):
    __tablename__ = 'sol_tmp'

    id = Column(Integer, primary_key=True)
    signature = Column(String, nullable=False)
    is_collected = Column(Boolean, default=False)

    __table_args__ = (
        Index("ix_mf_signature", "signature"),
        {"schema": db.SCHEMA},
    )


class QuickHistoricalTXCollector(HistoricalTXCollector):

    @log_performance_time(LOG)
    def _get_assignment(self) -> None:
        """
        Obtain assignment for data collection.
        """
        # receive block numbers ready for collection
        self._get_assigned_transactions()
        LOG.info(f"Transactions for collection: {len(self.assignment)}")

    def _get_assigned_transactions(self):
        """

        :return:
        """
        with db.get_db_session() as session:
            signatures = session.query(
                MfTemp.signature
            ).filter(
                MfTemp.is_collected.is_(None)
            ).limit(BATCH_SIZE).all()

        self.assignment = [i.signature for i in signatures]

    async def _async_get_data(self):
        """
        Concurrently collect transactions from blocks.
        Collected transactions are stored in `rel_transactions` attribute.
        """
        self.rel_transactions.clear()
        # Use asyncio.gather to fetch blocks concurrently
        transactions = await asyncio.gather(
            *(self._async_fetch_transaction(tx_sign) for tx_sign in self.assignment)
        )
        self.rel_transactions = transactions

    async def _async_fetch_transaction(self, tx_signature: str) -> EncodedTransactionWithStatusMeta:
        """
        Use solana client to fetch block with provided number.
        """
        await self._async_rate_limit_calls()
        # Fetch block data.
        try:
            transaction = await self.async_solana_client.get_transaction(
                Signature.from_string(tx_signature),
                encoding='jsonParsed',
                max_supported_transaction_version=0,
            )
        except SolanaRpcException as e:
            LOG.error(f"SolanaRpcException while fetching {tx_signature}: {e}")
            await asyncio.sleep(0.2)
            return await self._async_fetch_transaction(tx_signature)

        if not transaction.value:
            LOG.error(f"No transaction in received response. Transaction signature: {tx_signature}")
            return await self._async_fetch_transaction(tx_signature)
    
        return transaction.value.transaction

    @log_performance_time(LOG)
    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        # if relevant transactions were not found in current iteration, do nothing.
        if not self.rel_transactions:
            return
        with db.get_db_session() as session:
            for transaction in self.rel_transactions:
                signature = transaction.transaction.signatures[0]  # type: ignore
                records = session.query(db.TransactionStatusWithSignature).filter_by(
                    signature=str(signature)
                ).all()

                # Check if the record exists.
                if records:
                    # Iterate over each record and update transaction data.
                    for record in records:
                        record.transaction_data = transaction.to_json()

            # Commit the changes.
            session.commit()
        self._report_collection()

    def _report_collection(self) -> None:
        """
        """
        with db.get_db_session() as session:
            session.query(MfTemp).filter(MfTemp.signature.in_(self.assignment)).update(
                {"is_collected": True}, synchronize_session=False
            )
        LOG.info(f"Data for {len(self.relevant_transactions)} have been stored to the database.")

async def main():
    print('Start collecting old transactions from Solana chain: ...')
    tx_collector = QuickHistoricalTXCollector()
    await tx_collector.async_run()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
