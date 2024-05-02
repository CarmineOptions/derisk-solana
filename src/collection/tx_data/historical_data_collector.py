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
import logging
import os
import time
import traceback

from psycopg2 import OperationalError

import db
from src.collection.tx_data.collector import TXFromBlockCollector

LOGGER = logging.getLogger(__name__)
BATCH_SIZE = 100
# Defines offset of `HistoricalTXCollector._get_assigned_blocks method.
# In case when several historical data collector are run simultaneously, different offsets will ensure
# that these collectors don't get same block numbers in assignment.
OFFSET = os.getenv("OFFSET", "0")


class HistoricalTXCollector(TXFromBlockCollector):

    @property
    def collection_stream(self) -> db.CollectionStreamTypes:
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
        try:
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
        except OperationalError as e:
            LOGGER.error("OperationalError occured: %s. Waiting 120 to retry."
                         "\n Exception occurred: %s", str(e), traceback.format_exc())
            time.sleep(120)
            self._get_assigned_blocks()
            return

        self.assignment = [i.slot for i in slots]  # pylint: disable=attribute-defined-outside-init

    def _report_collection(self) -> None:
        """
        """
        # TODO: here we can check if last collected block does not  # pylint: disable=W0511
        #  exceed watershed number for historical data, if so stop collection
        LOGGER.info(f"Data for {len(self.relevant_transactions)} have been stored to the database.")
