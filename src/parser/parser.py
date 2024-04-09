from abc import ABC, abstractmethod
import binascii
import os
from pathlib import Path

from anchorpy import Program, Idl
import json

from based58 import based58
from solana.rpc.async_api import AsyncClient, Pubkey
from solana.rpc.api import Client
from solders.signature import Signature
import base64
from construct.core import StreamError
from anchorpy.program.event import EventParser

from anchorpy.provider import Provider, Wallet, Keypair
from anchorpy.program.common import Event
from solders.transaction_status import EncodedTransactionWithStatusMeta, ParsedInstruction, \
    UiPartiallyDecodedInstruction
from dataclasses import is_dataclass, asdict

import collections.abc

from db import get_db_session, ParsedTransactions


def is_namedtuple(obj):
    """Check if an object is an instance of a named tuple."""
    return isinstance(obj, tuple) and hasattr(obj, '_fields')


def serialize(obj):
    """
    Recursively serialize data class or named tuple instances into a dictionary,
    including nested instances.
    """
    if is_dataclass(obj):
        return {key: serialize(value) for key, value in asdict(obj).items()}
    elif is_namedtuple(obj):
        return {key: serialize(getattr(obj, key)) for key in obj._fields}
    elif isinstance(obj, collections.abc.Mapping):
        return {key: serialize(value) for key, value in obj.items()}
    elif isinstance(obj, collections.abc.Iterable) and not isinstance(obj, str):
        return [serialize(item) for item in obj]
    else:
        return obj


PROGRAM_LOG = "Program log: "
PROGRAM_DATA = "Program data: "
PROGRAM_LOG_START_INDEX = len(PROGRAM_LOG)
PROGRAM_DATA_START_INDEX = len(PROGRAM_DATA)


class TransactionDecoder(ABC):

    def __init__(self, path_to_idl: Path, program_id: Pubkey):
        self.program_id = program_id
        # read idl from file
        with open(path_to_idl, 'r') as fp:
            dict_data = json.load(fp)
            json_str = json.dumps(dict_data)
            idl = Idl.from_json(json_str)
        # intitialize main program
        self.program = Program(idl, program_id, Provider(AsyncClient(), Wallet(Keypair())))
        self.event_parser = EventParser(program_id, self.program.coder)
        self._processor = self.print_event_to_console

        self.events = list()  # temporary storage for parsed events.
        self.last_tx: EncodedTransactionWithStatusMeta | None = None

    @abstractmethod
    def _create_lending_account(self, event: Event):

        raise NotImplementedError('Implement me!')

    def save_event(self, event: Event) -> None:  # TODO replace when decided how to store events.
        """"""
        self.events.append(event)

    def print_event_to_console(self, event_record: ParsedTransactions):
        """

        :param event_record:
        :return:
        """
        print(event_record)

    def save_event_to_database(self, event_record: ParsedTransactions):
        """

        :param event_record:
        :return:
        """
        with get_db_session() as session:
            session.add(event_record)
            session.commit()

    def decode_marginfi_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta, block_number: int = -1):
        """

        :return:
        """
        log_msgs = transaction_with_meta.meta.log_messages

        self.event_parser.parse_logs(
            log_msgs, lambda x: self.save_event(x)
        )

    def decode_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta):
        """

        :param transaction_with_meta:
        :return:
        """
        self.last_tx = transaction_with_meta
        meta = transaction_with_meta.meta
        transaction = transaction_with_meta.transaction
        program_log = meta.log_messages

        # collect and parse instructions
        instructions = transaction.message.instructions
        parsed_instructions = list()
        for instruction in instructions:
            # if Encoded and master program is known - parse
            if isinstance(instruction, UiPartiallyDecodedInstruction):
                if instruction.program_id == self.program_id:
                    data = instruction.data
                    # print(data)
                    msg_bytes = based58.b58decode(str.encode(str(data)))
                    parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                    parsed_instructions.append((str(instruction.program_id), repr(parsed_instruction)))

            # simple collection
            if isinstance(instruction, ParsedInstruction):
                parsed_instructions.append((str(instruction.program_id), repr(instruction)))

        # add inner instructions
        for inner_instruction in meta.inner_instructions:
            for parsed_inner_instruction in inner_instruction.instructions:
                parsed_instructions.append((str(parsed_inner_instruction.program_id), repr(parsed_inner_instruction)))

        invoke_msg = f"Program {str(self.program_id)} invoke"
        core_program = False

        logs_parsed = dict()
        for log in program_log:
            log_start = log.split(":")[0]
            splitted = log_start.split(" ")

            if len(splitted) == 3 and splitted[0] == "Program" and splitted[2] == "success":
                # here program log ends, reset program type flag
                logs_parsed[log] = 'Program is finished'
                if str(self.program_id) in log:
                    logs_parsed[log] = 'Master program is finished'
                    core_program = False
            if log_start.startswith(invoke_msg):
                # here start program that we can decode.
                core_program = True

            if core_program:
                if log.startswith(PROGRAM_LOG) or log.startswith(PROGRAM_DATA):
                    log_str = (
                        log[PROGRAM_LOG_START_INDEX:]
                        if log.startswith(PROGRAM_LOG)
                        else log[PROGRAM_DATA_START_INDEX:]
                    )
                    # print(f"Log str: {log_str}")
                    try:
                        decoded_msg = base64.b64decode(log_str)
                    except binascii.Error:
                        logs_parsed[log] = 'see parsed instructions'
                        continue
                    try:
                        event = self.program.coder.events.parse(decoded_msg)
                    except StreamError:
                        print('stream error')

                        logs_parsed[log] = 'Mango specific stream error'
                        continue
                    if not event:
                        logs_parsed[log] = None
                    else:
                        logs_parsed[log] = repr(event)
                else:
                    logs_parsed[log] = 'Nothing to parse.'
            else:
                logs_parsed[log] = 'Foreign program/Nothing to parse'

        return parsed_instructions, logs_parsed, get_account_balances(transaction_with_meta), get_token_balance(transaction_with_meta)


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
    for pre, post in paired_balances:
        owner = post.owner if post else pre.owner
        mint = post.mint if post else pre.mint
        program_id = post.program_id if post else post.program_id

        initial_balance = int(pre.ui_token_amount.amount) if pre else 0
        final_balance = int(post.ui_token_amount.amount)
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


if __name__ == "__main__":
    tx_decoder = TransactionDecoder(
        Path('../../marginfi_idl2.json'),
        Pubkey.from_string("MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA")
    )

    token = os.getenv("RPC_URL")
    solana_client = Client(token)
    transaction = solana_client.get_transaction(
        Signature.from_string(
            # "4if5hzfKbJSxbA13ReBca2sY6kbAias7FseHG1QdUCHqSjhG4eNbGoz96TbBSNmCGoSQfKWx5gMtDVgxNb1iUV2M"
            "3i5dY25SoDE3zkoQQCBiVYfkh83SFr3rXc7LekE5Ks47SEUT9NGRqeAxuC2zH3HM4PcrebTLvmebCQJ26BbYA3KP"
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )
    instructions, logs, acc_balance, tokens = tx_decoder.decode_transaction(transaction.value.transaction)

    print(f'=============INSTRUCTIONS================')
    for instruction_id, instruction in instructions:
        print(f"{instruction_id}: \n   {instruction}")
    print(f'\n=================LOGS================')
    for k, v in logs.items():
        print(f"{k}\n     {v}")

    print(f'\n================BALANCE================')
    for i in acc_balance:
        print(i)

    print(f'\n=================TOKENS================')
    for t in tokens:
        print(t)
