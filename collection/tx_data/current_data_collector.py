"""

"""
import logging

import db
from collection.tx_data.collector import TXFromBlockCollector


LOG = logging.getLogger(__name__)

BATCH_SIZE = 20


class CurrentTXCollector(TXFromBlockCollector):

    @property
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:
        return db.CollectionStreamTypes.CURRENT

    def _get_assigned_blocks(self) -> None:
        """
        Retrieves the earliest last collected block number among protocols.
        """
        with db.get_db_session() as session:
            # Query the database for protocols with the given public keys
            protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(self.protocol_public_keys))

        last_collected_block = None  # Initialize last_collected_block

        for protocol in protocols:
            # Use last_block_collected if it's not None, otherwise fallback to watershed_block
            block = protocol.last_block_collected if protocol.last_block_collected is not None \
                else protocol.watershed_block

            # Update last_collected_block if it's None or if a smaller block number is found
            if last_collected_block is None or block < last_collected_block:
                last_collected_block = block

        self.assignment = [i for i in range(last_collected_block, last_collected_block + BATCH_SIZE)]

    def _report_collection(self):
        """
        Updates `last_collected_block` for each protocol.
        :return:
        """
        with db.get_db_session() as session:
            protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(self.protocol_public_keys))

            for protocol in protocols:
                protocol.last_block_collected = max(self.assignment) if self.assignment else None

            session.commit()
