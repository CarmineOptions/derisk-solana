"""
Class for collection of transaction data from Solana chain
"""
import asyncio
from abc import abstractmethod
from typing import List, Tuple
import logging
import os
import time

from solana.exceptions import SolanaRpcException
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.core import RPCException
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiConfirmedBlock
from sqlalchemy.exc import IntegrityError

from collection.shared.generic_collector import GenericSolanaConnector, SolanaTransaction
import db


LOG = logging.getLogger(__name__)


class TXFromBlockCollector(GenericSolanaConnector):
    """
    Class to collect transaction data from Solana blocks.
    """
    protocol_public_keys: List[str] | None = None

    def __init__(self):
        super().__init__()
        self.async_solana_client = AsyncClient(self.authenticated_rpc_url)

    async def _async_rate_limit_calls(self) -> None:
        """
        This method implements a rate-limiting mechanism to control the frequency of API calls asynchronously.
        It ensures that the number of API calls does not exceed a predefined limit per second.
        If the limit is reached, it will pause the execution momentarily before allowing further API calls.
        """
        # Check if the number of calls made in the last second exceeds the maximum limit.
        while len(self._call_timestamps) >= self.rate_limit:
            # Calculate the time passed since the first call in the timestamp list.
            time_passed = time.time() - self._call_timestamps[0]

            if time_passed > 1:
                # More than a second has passed since the first call, remove it from the list.
                self._call_timestamps.pop(0)
            else:
                # Wait for the remainder of the second before allowing more calls, asynchronously.
                await asyncio.sleep(1 - time_passed)

        # Record the timestamp of the current call.
        self._call_timestamps.append(time.time())

    async def run(self):
        """
        Main method to process all necessary operations to collect and write data.
        """
        k = 0
        start_time = time.time()
        while not self._collection_completed:
            if k % 10000 == 0:
                LOG.info(f"Iterations completed: {k}, in {time.time() - start_time:.1f} seconds.")
            self._get_assignment()
            await self._get_data()
            self._write_tx_data()
            k += 1
        LOG.info(f"Collection completed for {self.__class__.__name__}.")

    @property
    @abstractmethod
    def COLLECTION_STREAM(self) -> db.CollectionStreamTypes:  # pylint: disable=invalid-name
        """Implement in subclasses to define the constant value"""
        raise NotImplementedError("Implement me!")

    async def _get_data(self) -> None:
        """
        Collect transactions from blocks. Collected transactions are stored in `rel_transactions` attribute.
        """
        self.rel_transactions.clear()
        # Use asyncio.gather to fetch blocks concurrently
        blocks = await asyncio.gather(
            *(self._async_fetch_block(block_number) for block_number in self.assignment)
        )
        for block, block_number in blocks:
            if not block:
                continue
            self._select_relevant_tx_from_block(block, block_number)

    async def _async_fetch_block(self, block_number: int) -> Tuple[UiConfirmedBlock | None, int]:
        """
        Use solana client to fetch block with provided number.
        """
        await self._async_rate_limit_calls()
        # Fetch block data.
        try:
            block = await self.async_solana_client.get_block(
                slot=block_number,
                encoding='jsonParsed',
                max_supported_transaction_version=0,
            )
        except SolanaRpcException as e:
            LOG.error(f"SolanaRpcException while fetching {block_number}: {e}")
            await asyncio.sleep(0.5)
            return await self._async_fetch_block(block_number)
        except RPCException as e:
            LOG.error(f"RpcException while fetching {block_number}: {e}")
            return None, block_number

        return block.value, block_number

    def _select_relevant_tx_from_block(self, block: UiConfirmedBlock, block_number: int) -> None:
        """
        Select only relevant transactions based on public keys involved.
        """
        if block.transactions:
            relevant_transactions = [tx for tx in block.transactions if self._is_transaction_relevant(tx)]
            # Store raw transaction data with block metadata as `SolanaTransaction` objects.
            relevant_solana_transaction = [
                SolanaTransaction(
                    block_number=block_number,
                    block_time=block.block_time if block.block_time else -1,
                    tx_body=tx
                ) for tx in relevant_transactions  # type: ignore
            ]
            self.rel_transactions.extend(relevant_solana_transaction)

    def _get_assignment(self) -> None:
        """
        Obtain assignment for data collection.
        """
        # Update for relevant PPKs
        self._get_protocol_public_keys()
        # receive block numbers ready for collection
        self._get_assigned_blocks()
        LOG.info(f"Blocks for collection: {self.assignment}")

    @abstractmethod
    def _get_assigned_blocks(self) -> None:
        """
        Obtains block numbers to fetch.
        """
        raise NotImplementedError("Implement me!")

    def _get_protocol_public_keys(self) -> None:
        """
        Get list of public keys for relevant protocol from env variables.
        :return:
        """
        if not self.protocol_public_keys:
            self.protocol_public_keys = list()
        # get list of public keys from env variables.
        keys = os.getenv("PROTOCOL_PUBLIC_KEYS", "").split(',')

        # check if new keys are added
        new_keys = set(keys) - set(self.protocol_public_keys)
        if new_keys:
            watershed_block = self._get_latest_finalized_block_on_chain()
            for new_key in new_keys:
                self._add_new_protocol(new_key, watershed_block)
            LOG.warning(f"New protocol(s) added to collection: {new_keys}")
        self.protocol_public_keys = keys

    @staticmethod
    def _add_new_protocol(public_key: str, watershed_block_number: int) -> None:
        """
        Adds new protocol to 'protocols' table, with last finalized block on chain serving as watershed block.
        """
        with db.get_db_session() as session:
            try:
                new_protocol = db.Protocols(
                    public_key=public_key,
                    watershed_block=watershed_block_number
                )

                # Add the new record to the session and commit it
                session.add(new_protocol)
                session.commit()
            except IntegrityError:
                session.rollback()  # roll back the session to a clean state
                LOG.error(f"A protocol with the public key `{public_key}` already exists in the database.")

    def _get_latest_finalized_block_on_chain(self) -> int:
        """
        Fetches number of the last finalized block.
        """
        try:
            return self.solana_client.get_slot(commitment=Commitment('finalized')).value
        except SolanaRpcException as e:
            LOG.error(f"SolanaRpcException while fetching the last finalized block on chain: {e}")
            time.sleep(0.5)
            return self._get_latest_finalized_block_on_chain()

    def _write_tx_data(self) -> None:
        """
        Write raw tx data to database.
        """
        # if relevant transactions were not found in current iteration, do nothing.
        if not self.rel_transactions:
            return
        with db.get_db_session() as session:
            for transaction in self.rel_transactions:
                sources = transaction.sources(self.protocol_public_keys if self.protocol_public_keys else [])
                signature = transaction.signature
                # Same transaction has to be recorded once per each relevant protocol
                for source in sources:
                    record = session.query(db.TransactionStatusWithSignature).filter_by(
                        signature=str(signature),
                        source=source
                    ).first()

                    # Check if the record exists.
                    if record:
                        # Update transaction data.
                        record.transaction_data = transaction.tx_body.to_json()
                    else:
                        new_record = db.TransactionStatusWithSignature(
                            source=source,
                            slot=transaction.block_number,
                            signature=str(signature),
                            block_time=transaction.block_time,
                            transaction_data=transaction.tx_body.to_json(),
                            collection_stream=self.COLLECTION_STREAM
                        )
                        session.add(new_record)

            # Commit the changes.
            session.commit()
        self._report_collection()

    @abstractmethod
    def _report_collection(self):
        """
        Report collected blocks.
        :return:
        """
        raise NotImplementedError("Implement me!")

    def _is_transaction_relevant(
            self,
            transaction: EncodedTransactionWithStatusMeta
    ) -> bool:
        """
        Determines if the transaction involves any of the specified public keys.

        This method checks if any of the public keys provided in the 'ppks' list
        are present in the transaction's account keys. It is used to filter transactions
        based on the involvement of specific protocols identified by their public keys.
        """
        relevant_pubkeys = [
            i for i in transaction.transaction.message.account_keys  # type: ignore
            if str(i.pubkey) in self.protocol_public_keys  # type: ignore
        ]
        return bool(relevant_pubkeys)
