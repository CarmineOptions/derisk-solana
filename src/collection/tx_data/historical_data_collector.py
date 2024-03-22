"""
Collector of raw transaction data for historical transactions.
Dependent on `transactions` db table as its source of blocks to fetch. All PPKs should be known.


Fetch all transactions from this block, filter by PPKs of all protocols (i.e., Solend, Mango, etc).

1. Obtains several (`BATCH_SIZE`) oldest slot numbers where there are relevant transactions
 that do not have transaction data stored in database.
2. Concurrently fetch blocks from these slots.
3. Filter all transactions in fetched blocks by PPKs of all lending protocols to select relevant transactions.
4. For each relevant transaction:
    - create new record in transactions table if not yet exists.
    - assign transaction data to existing records.
5. Repeat 1-4 indefinitely.

If being restarted - nothing changes.
"""
import asyncio
import logging
import os

import db
from src.collection.tx_data.collector import TXFromBlockCollector

LOG = logging.getLogger(__name__)
BATCH_SIZE = 10
# Defines offset of `HistoricalTXCollector._get_assigned_blocks method.
# In case when several historical data collector are run simultaneously, different offsets will ensure
# that these collectors don't get same block numbers in assignment.
OFFSET = os.getenv("OFFSET", "0")


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
            # Step 1: Select the first 100 slots that are not processed and lock them for update
            slots_to_update = session.query(db.SlotTable) \
                .filter(db.SlotTable.is_processed == False) \
                .limit(BATCH_SIZE) \
                .with_for_update() \
                .all()

            # Step 2: Extract slot numbers and mark them as processed
            slot_numbers = []
            for slot in slots_to_update:
                slot_numbers.append(slot.slot)
                slot.is_processed = True  # Mark as processed

            # Commit the transaction to save changes
            session.commit()

            # Print or return the slot numbers
            self.assignment = slot_numbers  # pylint: disable=attribute-defined-outside-init

    def _report_collection(self) -> None:
        """
        """
        # TODO: here we can check if last collected block does not  # pylint: disable=W0511
        #  exceed watershed number for historical data, if so stop collection
        LOG.info(f"Data for {len(self.relevant_transactions)} have been stored to the database.")


async def main():
    print('Start collecting old transactions from Solana chain: ...')
    tx_collector = HistoricalTXCollector()
    await tx_collector.async_run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
