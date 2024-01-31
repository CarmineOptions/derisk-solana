import os
import logging
import time

import solana.rpc.api
from solana.exceptions import SolanaRpcException
from solders.rpc.responses import RpcConfirmedTransactionStatusWithSignature
from solders.signature import Signature
from solders.transaction_status import EncodedConfirmedTransactionWithStatusMeta, EncodedTransactionWithStatusMeta

import db
import src.protocols.addresses



LOGGER = logging.getLogger(__name__)

TX_BATCH_SIZE = 1000



class TransactionCollector:

    def __init__(
        self, 
        addresses: dict[str, str], 
        start_signatures: dict[str, Signature | None],
        rpc_token: str | None = None,
        rate_limit: int = 5, 
    ):
        self.addresses = addresses
        # Signature older then `start_signatures` will not be stored.
        self.start_signatures = start_signatures
        self.rpc_token = rpc_token if rpc_token else os.getenv("QUICKNODE_TOKEN")
        # Rate limit set in terms of maximum number of calls per second.
        self.rate_limit = rate_limit

        self.solana_client: solana.rpc.api.Client = solana.rpc.api.Client(self.rpc_token)
        self._call_timestamps: list[int] = []
        self._oldest_signatures: dict[str, Signature | None] = {address: None for address in self.addresses.values()}
        self._signatures_completed: dict[str, bool] = {address: False for address in self.addresses.values()}
        self._oldest_completed_slots: dict[str, int] = {address: 0 for address in self.addresses.values()}
        self._transactions_completed: dict[str, bool] = {address: False for address in self.addresses.values()}
        self.newest_signatures: dict[str, Signature | None] = {address: None for address in self.addresses.values()}

    def _rate_limit_calls(self) -> None:
        """
        This method implements a rate-limiting mechanism to control the frequency of API calls.
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
                # Wait for the remainder of the second before allowing more calls.
                time.sleep(1 - time_passed)

        # Record the timestamp of the current call.
        self._call_timestamps.append(time.time())

    def _fetch_signatures(
        self, 
        protocol: str, 
        address: Signature,
    ) -> list[RpcConfirmedTransactionStatusWithSignature]:
        """
        Fetch transaction signatures.
        Fetch only signatures that occured before `self._oldest_signatures` for the given protocol. If 
        `self._oldest_signatures[address]` is None, fetch signatures starting from the latest one.
        :return: list of signatures.
        """
        self._rate_limit_calls()

        try:
            response = self.solana_client.get_signatures_for_address(
                solana.rpc.api.Pubkey.from_string(address),
                limit=TX_BATCH_SIZE,
                before=self._oldest_signatures[address],
                until=self.start_signatures[address],
            )
            signatures = response.value
        except SolanaRpcException as e:  # Most likely to catch 503 here. If something else - we stuck in loop TODO fix
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(2)
            return self._fetch_transaction_signatures()

        if len(signatures) < TX_BATCH_SIZE:
            self._signatures_completed[address] = True

        # Get oldest slot for which it is certaion that we fetched all signatures.
        unique_slots = sorted(set([i.slot for i in signatures]))
        if len(unique_slots) < 2:
            LOGGER.warning(
                "Last batch for protocol = {} contains only signatures from a single slot = {}.".format(
                    protocol,
                    unique_slots[0],
                )
            )
            self._oldest_completed_slots[address] = unique_slots[0]
        else:
            second_oldest_slot = unique_slots[1]
            self._oldest_completed_slots[address] = second_oldest_slot

        # Save the signature from the newest slot for which it is certaion that we fetched all signatures.
        if self.newest_signatures[address] is None:
            if len(unique_slots) < 2:
                newest_completed_slot = unique_slots[0]
            else:
                newest_completed_slot = unique_slots[-2]
            newest_completed_slot_signatures = [i.signature for i in signatures if i.slot == newest_completed_slot]
            self.newest_signatures[address] = newest_completed_slot_signatures[0]
        return signatures

    def set_oldest_signatures_recorded(self) -> None:
        """ Obtain the oldest signature recorded for each protocol. """
        with db.get_db_session() as session:
            for protocol, address in self.addresses.items():
                LOGGER.info("Getting the oldest stored signature for protocol = {}.".format(protocol))
                oldest_transaction = session.query(db.TransactionStatusWithSignature.signature) \
                    .filter(db.TransactionStatusWithSignature.source == address) \
                    .order_by(db.TransactionStatusWithSignature.id.desc()) \
                    .first()
                if not oldest_transaction:
                    LOGGER.warning(
                        "No signatures found for protocol = {}. Signatures will be collected from the newest at the "
                        "moment.".format(protocol)
                    )
                    return
                oldest_signature = oldest_transaction[0]
                LOGGER.info("The oldest stored signature = {} for protocol = {}.".format(oldest_signature, protocol))
                self._oldest_signatures[address] = Signature.from_string(oldest_signature)

    def _add_signatures_to_db(
        self, 
        transactions: list[RpcConfirmedTransactionStatusWithSignature],
        address: str,
    ) -> None:
        """
        Write transaction signatures to db.
        :param transactions: fetched transactions
        """
        with db.get_db_session() as session:
            for transaction in transactions:
                # store only transactions from slot with complete transaction history fetched.
                if transaction.slot < self._oldest_completed_slots[address]:
                    break

                tx_status_record = db.TransactionStatusWithSignature(
                    signature=str(transaction.signature),
                    source=address,
                    slot=transaction.slot,
                    block_time=transaction.block_time
                )
                session.add(tx_status_record)
                session.flush()  # Flush here to get the ID
                # store errors and/or memos to db if any
                if transaction.err:
                    tx_error_record = db.TransactionStatusError(
                        error_body=transaction.err.to_json(),
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_error_record)
                if transaction.memo:
                    tx_memo_record = db.TransactionStatusMemo(
                        memo_body=transaction.memo,
                        tx_signatures_id=tx_status_record.id,
                    )
                    session.add(tx_memo_record)

            self._oldest_signatures[address] = transaction.signature
            session.commit()

    def collect_signatures(self) -> Signature:
        """
        Fetch signatures between `self._oldest_signatures[address]` and `self._newest_signatures[address]`.
        """
        for protocol, address in self.addresses.items():
            LOGGER.info("Started collecting signatures for protocol = {}.".format(protocol))
            while not self._signatures_completed[address]:
                transactions = self._fetch_signatures(protocol=protocol, address=address)
                if not transactions:
                    break
                self._add_signatures_to_db(transactions=transactions, address=address)
            LOGGER.info(
                "All available signatures for protocol = {} are collected. The oldest signature = {}.".format(
                    protocol,
                    str(self._oldest_signatures[address]),
                )
            )

    def _fetch_transactions_from_block(self, slot: int) -> list[EncodedConfirmedTransactionWithStatusMeta]:
        self._rate_limit_calls()

        # Fetch block data.
        try:
            block = self.solana_client.get_block(
                slot=slot,
                encoding='jsonParsed',
                max_supported_transaction_version=0,
            )
        except SolanaRpcException as e:
            LOGGER.error(f"SolanaRpcException: {e}")
            time.sleep(1)
            return self._fetch_transactions_from_block(slot)

        # Keep only transactions with protocol (program) public key involved.
        transactions = [tx for tx in block.value.transactions if self._is_transaction_relevant(tx)]
        return transactions

    def collect_transactions(self) -> None:
        """
        Fill transaction data to `tx_signatures.tx_raw` column if missing.
        """
        block_counter = 0
        start_time = time.time()
        with db.get_db_session() as session:
            for protocol, address in self.addresses.items():
                while not self._transactions_completed[address]:
                    # Retrieve 200 transactions where tx_raw is NULL and source matches the address.
                    slots = session.query(
                        db.TransactionStatusWithSignature.id,
                        db.TransactionStatusWithSignature.slot,
                    ).filter(
                        db.TransactionStatusWithSignature.tx_raw.is_(None),
                        db.TransactionStatusWithSignature.source == address,
                    ).limit(200).all()

                    if not slots:
                        self._transactions_completed[address] = True

                    # Fetch each slot one by one.
                    for slot in {slot for _, slot in slots}:
                        transactions = self._fetch_transactions_from_block(slot)

                        for transaction in transactions:
                            # Update `tx_raw` column for each transaction.
                            signature = transaction.transaction.signatures[0]
                            self._update_tx_raw(
                                signature=signature,
                                address=address,
                                new_tx_raw=transaction.to_json(),
                            )

                        block_counter += 1

                    # Log every 10,000 slots
                    if block_counter % 10_000 == 0:
                        elapsed_time = time.time() - start_time
                        LOGGER.info(f"Processed {block_counter} slots in {elapsed_time:.2f} seconds")

    def _update_tx_raw(self, signature: Signature, address: str, new_tx_raw: str) -> None:
        """
        Update tx_signature (tx_raw) for given signature, if tx_raw is null, otherwise does nothing.
        :param signature: Signature
        :param new_tx_raw: jsonfyed transaction data
        """
        with db.get_db_session() as session:
            # Query for the record with the given signature and source
            record = session.query(db.TransactionStatusWithSignature).filter(
                db.TransactionStatusWithSignature.tx_raw.is_(None)
            ).filter_by(signature=str(signature), source=address).first()

            # Check if the record exists.
            if record:
                # Update the tx_raw field.
                record.tx_raw = new_tx_raw

                # Commit the changes.
                session.commit()

    def _is_transaction_relevant(
        self,
        transaction: EncodedTransactionWithStatusMeta | EncodedConfirmedTransactionWithStatusMeta,
    ) -> bool:
        """
        Decide if transaction is relevant based on the presence of relevant address between transactions account keys.
        """
        relevant_pubkeys = [
            i for i in transaction.transaction.message.account_keys if str(i.pubkey) in self.addresses.values()
        ]
        return bool(relevant_pubkeys)


def collect_signatures_and_transactions(
    start_signatures: dict[str, Signature | None],
    rpc_token: str, 
    rate: int, 
) -> None:
    # Collect signatures for each lending protocol.
    logging.info('Started collecting signatures.')
    signatures_collector = TransactionCollector(
        addresses=src.protocols.addresses.ALL_ADDRESSES,
        start_signatures=start_signatures,
        rpc_token=rpc_token,
        rate_limit=rate if rate else 5,
    )
    signatures_collector.set_oldest_signatures_recorded()
    signatures_collector.collect_signatures()

    # Collect transactions for each lending protocol. Create a new instance of `TransactionCollector` to 
    # reset internal counters.
    logging.info('Start collecting transactions.')
    transactions_collector = TransactionCollector(
        addresses=src.protocols.addresses.ALL_ADDRESSES,
        start_signatures=start_signatures,
        rpc_token=rpc_token,
        rate_limit=rate if rate else 5,
    )
    transactions_collector.collect_transactions()

    # Repeat the process to collect newly produced signatures and transactions.
    collect_signatures_and_transactions(
        rpc_token=rpc_token, 
        rate=rate, 
        start_signatures=signatures_collector.newest_signatures,
    )