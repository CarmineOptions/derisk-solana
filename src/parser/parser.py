from abc import ABC, abstractmethod
from pathlib import Path
import json

from anchorpy import Program, Idl
from anchorpy.program.event import EventParser
from anchorpy.provider import Provider, Wallet, Keypair
from anchorpy.program.common import Event
from solana.rpc.async_api import AsyncClient, Pubkey
from solders.transaction_status import EncodedTransactionWithStatusMeta

from db import ParsedTransactions, Session


PROGRAM_LOG = "Program log: "
PROGRAM_DATA = "Program data: "
PROGRAM_LOG_START_INDEX = len(PROGRAM_LOG)
PROGRAM_DATA_START_INDEX = len(PROGRAM_DATA)


def is_namedtuple(obj):
    """Check if an object is an instance of a named tuple."""
    return isinstance(obj, tuple) and hasattr(obj, '_fields')


class UnknownInstruction(Exception):
    def __init__(self, unknown_instruction):
        super().__init__(f"Unknown instruction = {unknown_instruction}")


class TransactionDecoder(ABC):

    def __init__(self, path_to_idl: Path, program_id: Pubkey):
        self.program_id = program_id
        # read idl from file
        with open(path_to_idl, 'r', encoding='utf-8') as fp:
            dict_data = json.load(fp)
            json_str = json.dumps(dict_data)
            idl = Idl.from_json(json_str)
        # intitialize main program
        self.program = Program(idl, program_id, Provider(AsyncClient(), Wallet(Keypair())))
        self.event_parser = EventParser(program_id, self.program.coder)
        self._processor = self.print_event_to_console

        self.events = list()  # temporary storage for parsed events.
        self.transaction: EncodedTransactionWithStatusMeta | None = None
        self.last_tx: EncodedTransactionWithStatusMeta | None = None
        self.error: int = None  # error index for failed transactions


    @abstractmethod
    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta):
        raise NotImplementedError('Implement me!')

    def _create_lending_account(self, event: Event):
        raise NotImplementedError('Implement me!')

    def print_event_to_console(self, event_record: ParsedTransactions):
        """
        Print event to console.
        """
        print(event_record)

    def save_event_to_database(
            self,
            event_record: ParsedTransactions,
            timestamp: int,
            block_number: int,
            session: Session
    ):
        """
        Assign timestamp and block number to event. Add record to db session.
        """
        event_record.created_at = timestamp
        event_record.block = block_number
        session.add(event_record)



def match_token_balances(list1, list2):
    matched = []
    unmatched_list1 = list1.copy()
    unmatched_list2 = list2.copy()

    for item1 in list1:
        match_found = False
        for item2 in unmatched_list2:
            if item1.mint == item2.mint and item1.program_id == item2.program_id and item1.owner == item2.owner:
                matched.append((item1, item2))
                unmatched_list2.remove(item2)
                unmatched_list1.remove(item1)
                match_found = True
                break
        if not match_found:
            matched.append((item1, None))

    # Add remaining unmatched items from list2
    for item2 in unmatched_list2:
        matched.append((None, item2))

    return matched


def get_token_balance(transaction_with_meta:  EncodedTransactionWithStatusMeta):
    meta = transaction_with_meta.meta

    balances = list()
    paired_balances = match_token_balances(meta.pre_token_balances, meta.post_token_balances)
    # print(paired_balances)
    for pre, post in paired_balances:
        owner = post.owner if post else pre.owner
        mint = post.mint if post else pre.mint
        program_id = post.program_id if post else pre.program_id

        initial_balance = int(pre.ui_token_amount.amount) if pre else 0
        final_balance = int(post.ui_token_amount.amount) if post else 0
        balances.append(f"Owner: {owner}, mint: {mint}, "
                        f"balance: {initial_balance:,} -> {final_balance:,}, "
                        f"change = {final_balance - initial_balance:,},  Program: {program_id}")
    return balances


def get_account_balances(transaction_with_meta:  EncodedTransactionWithStatusMeta):
    meta = transaction_with_meta.meta
    transaction = transaction_with_meta.transaction

    balance_changes = []

    for i, ac in enumerate(
            [str(key.pubkey) for key in transaction.message.account_keys]
    ):
        pre = meta.pre_balances[i]
        post = meta.post_balances[i]
        msg = f"acc.key: {ac}, balance {pre:,} -> {post:,} "
        if pre != post:
            msg += f"  ! change: {post - pre:,}"
        balance_changes.append(msg)
    return balance_changes
