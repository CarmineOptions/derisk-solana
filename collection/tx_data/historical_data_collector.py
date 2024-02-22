"""

"""
import logging
from typing import List

from solders.transaction_status import UiConfirmedBlock, EncodedConfirmedTransactionWithStatusMeta, \
    EncodedTransactionWithStatusMeta

import db
from collection.tx_data.collector import TXFromBlockCollector


LOG = logging.getLogger(__name__)

BATCH_SIZE = 100


class HistoricalTXCollector(TXFromBlockCollector):

    @property
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:
        return db.CollectionStreamTypes.HISTORICAL

    def _get_assigned_blocks(self) -> None:
        """

        :return:
        """
        self.assignment = list()
        # TODO: make it more flexible. we want to be able to get assignments indirectly
        #  from db so several collectors can serve at once / or change status of tx while fetching tx_raw
        # Fetch first n blocks that contain transactions without tx_raw.
        with db.get_db_session() as session:
            distinct_slots = session.query(
                db.TransactionStatusWithSignature.slot
            ).filter(
                db.TransactionStatusWithSignature.tx_raw.is_(None)
            ).distinct().subquery()

            # Outer query to order the distinct slots and limit the results
            slots = session.query(
                distinct_slots.c.slot
            ).order_by(
                distinct_slots.c.slot
            ).limit(BATCH_SIZE).all()

        self.assignment = [i.slot for i in slots]
