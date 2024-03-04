"""
Collector of raw transaction data for historical transactions.
"""
import asyncio
import os

import db
from collection.tx_data.collector import TXFromBlockCollector


BATCH_SIZE = 100
OFFSET = os.getenv('OFFSET', 0)


class HistoricalTXCollector(TXFromBlockCollector):

    @property
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:  # pylint: disable=invalid-name
        """ Property returning stream type."""
        return db.CollectionStreamTypes.HISTORICAL

    def _get_assigned_blocks(self) -> None:
        """
        Get `BATCH_SIZE` of unique block numbers we need to fetch and get transaction data from.
        :return:
        """
        # TODO: make it more flexible. we want to be able to get assignments indirectly  # pylint: disable=W0511
        #  from db so several collectors can serve at once / or change status of tx while fetching tx_raw
        # Fetch first n blocks that contain transactions without tx_raw.
        with db.get_db_session() as session:
            distinct_slots = session.query(
                db.TransactionStatusWithSignature.slot
            ).filter(
                db.TransactionStatusWithSignature.transaction_data.is_(None)
            ).distinct().offset(int(OFFSET)).limit(BATCH_SIZE*3).subquery()

            # Outer query to order the distinct slots and limit the results
            slots = session.query(
                distinct_slots.c.slot
            ).order_by(
                distinct_slots.c.slot
            ).limit(BATCH_SIZE).all()

        self.assignment = [i.slot for i in slots]  # pylint: disable=attribute-defined-outside-init

    def _report_collection(self) -> None:
        """
        """
        # TODO: here we can check if last collected block does not  # pylint: disable=W0511
        #  exceed watershed number for historical data, if so stop collection


async def main():
    print('Start collecting old transactions from Solana chain: ...')
    tx_collector = HistoricalTXCollector()
    await tx_collector.run()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
