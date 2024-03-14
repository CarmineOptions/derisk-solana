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
    If being restarted - start from last block parsed. The last current block number is collected from db.
"""
import asyncio
import logging

import db
from src.collection.tx_data.collector import TXFromBlockCollector


LOG = logging.getLogger(__name__)

BATCH_SIZE = 30


class CurrentTXCollector(TXFromBlockCollector):

    @property
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:  # pylint: disable=invalid-name
        """
        Property returning stream type.
        """
        return db.CollectionStreamTypes.CURRENT

    def _get_assigned_blocks(self) -> None:
        """
        Retrieves the earliest last collected block number among protocols.
        """
        with db.get_db_session() as session:
            # Query the database for protocols with the given public keys
            protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(
                self.protocol_public_keys if self.protocol_public_keys else []
            ))

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

    def _report_collection(self):
        """
        Updates `last_collected_block` for each protocol.
        :return:
        """
        with db.get_db_session() as session:
            protocols = session.query(db.Protocols).filter(db.Protocols.public_key.in_(
                self.protocol_public_keys if self.protocol_public_keys else []
            ))

            for protocol in protocols:
                protocol.last_block_collected = max(self.assignment) if self.assignment else None

            session.commit()
        LOG.info(f"Assignment completed: {self.assignment}")


async def main():
    print('Start collecting new transactions from Solana chain: ...')
    tx_collector = CurrentTXCollector()
    await tx_collector.async_run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    asyncio.run(main())
