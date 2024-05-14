"""
Module contains `CurrentTXCollector`, class dedicated to collection new (recently occurred) transaction data
on Solana chain for lending protocols.

    t_O - watershed block, block that we assign as divider of historical and current data.
    Takes `t_0` from db, assign `t_0` if first run.
    PPKs (protocol public key) are collected from environmental variable.
    Takes `t_0` and all PPKs as input
    1) Concurrently fetch blocks from `t_0` to `t_0`+`BATCH_SIZE` or to last finalized slot obtained with `get_slot`
     method of RPC API.
    2) Filter all transactions in fetched blocks by PPKs of all protocols (i.e. Solend, Mango etc)
     to select relevant transactions.
    3) For each relevant transaction:
        create new record in `transactions` table.
    4) replace `t_0` with last fetched block and repeat 1-3.
    If being restarted - start from the latest block saved. The last current block number is collected from db.
"""
import logging
import time
import traceback

from sqlalchemy.exc import OperationalError

import db
from src.collection.tx_data.collector import TXFromBlockCollector


LOGGER = logging.getLogger(__name__)

BATCH_SIZE = 30


class CurrentTXCollector(TXFromBlockCollector):

    @property
    def collection_stream(self) -> db.CollectionStreamTypes:
        """
        Property returning stream type.
        """
        return db.CollectionStreamTypes.CURRENT

    def _get_assigned_blocks(self) -> None:
        """
        Retrieves the earliest last collected block number among protocols.
        """
        try:
            with db.get_db_session() as session:
                # Query the database for protocols with the given public keys
                protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(
                    self.protocol_public_keys if self.protocol_public_keys else []
                ))
        except OperationalError as e:
            LOGGER.error("OperationalError occured: %s. Waiting 120 to retry."
                         "\n Exception occurred: %s", str(e), traceback.format_exc())
            time.sleep(120)
            self._get_assigned_blocks()
            return

        last_collected_block = None  # Initialize last_collected_block

        for protocol in protocols:
            # Use last_block_collected if it's not None, otherwise fallback to watershed_block
            block = protocol.last_block_collected if protocol.last_block_collected is not None \
                else protocol.watershed_block

            # Update last_collected_block if it's None or if a smaller block number is found
            if last_collected_block is None or block < last_collected_block:
                last_collected_block = block
        last_block_on_chain = self._get_latest_finalized_block_on_chain()

        self.assignment = list(  # pylint: disable=attribute-defined-outside-init
            range(last_collected_block, min(last_collected_block + BATCH_SIZE, last_block_on_chain))  # type: ignore
        )

        if 253152004 in self.assignment:
            self.assignment.remove(253152004)  # Unknown bug with block 253152004
        if 255312004 in self.assignment:
            self.assignment.remove(255312004)  # Unknown bug with block 255312004
        if 253584001 in self.assignment:
            self.assignment.remove(253584001)  # Unknown bug with block 253584001
        if 255744008 in self.assignment:
            self.assignment.remove(255744008)  # Unknown bug with block 255744008

    def _report_collection(self):
        """
        Updates `last_collected_block` for each protocol.
        :return:
        """
        try:
            with db.get_db_session() as session:
                protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(
                    self.protocol_public_keys if self.protocol_public_keys else []
                ))

                for protocol in protocols:
                    if self.assignment:
                        protocol.last_block_collected = max(self.assignment)

                session.commit()
        except OperationalError as e:
            LOGGER.error("OperationalError occured: %s. Waiting 120 to retry."
                         "\n Exception occurred: %s", str(e), traceback.format_exc())
            time.sleep(120)
            self._report_collection()
            return

        LOGGER.info(f"Assignment completed: {self.assignment}")
