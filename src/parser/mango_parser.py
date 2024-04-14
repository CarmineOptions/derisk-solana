"""
Kamino transaction parser.
"""
from pathlib import Path
from typing import Any, List, Tuple
import logging
import os
import re

from anchorpy.program.common import Event
from base58 import b58decode
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from db import MangoParsedTransactions, MangoLendingAccounts
from src.parser.parser import TransactionDecoder, UnknownInstruction
from src.protocols.addresses import MANGO_ADDRESS
from src.protocols.idl_paths import MANGO_IDL_PATH

LOGGER = logging.getLogger(__name__)


def camel_to_snake(name):
    # This pattern identifies places where a lowercase letter is followed by an uppercase letter
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    # Replace such places with an underscore and a lowercase version of the uppercase letter
    snake_case_name = pattern.sub('_', name).lower()
    return snake_case_name


class MangoTransactionParser(TransactionDecoder):

    def __init__(
        self,
        path_to_idl: Path = Path(MANGO_IDL_PATH),
        program_id: Pubkey = Pubkey.from_string(MANGO_ADDRESS)
    ):
        super().__init__(path_to_idl, program_id)

    def _get_mango_instructions(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> List[Tuple[str, Any]]:
        """Parse instructions from the transaction that match the known program ID."""
        # Initialize a list to store parsed instructions
        parsed_instructions: List[Tuple[str, Any]] = []
        # Processing each instruction in the transaction
        for instruction in transaction_with_meta.transaction.message.instructions:
            # Check if instruction is partially decoded and belongs to the known program
            if isinstance(instruction, UiPartiallyDecodedInstruction) and instruction.program_id == self.program_id:
                data = instruction.data
                msg_bytes = b58decode(str.encode(str(data)))
                try:
                    # Attempt to parse the decoded bytes into an instruction object
                    parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                    print('parsed inst', parsed_instruction)
                    # Store the parsed instruction name along with the instruction object
                    parsed_instructions.append((parsed_instruction.name, instruction))
                except StreamError:
                    # If parsing fails, simply ignore and continue
                    # Here we assume that relevant instructions do not fail.
                    pass
        return parsed_instructions

    def _handle_log(self, msg, parsed_instructions):
        if msg.startswith("Program log: Instruction:"):
            # Extract and format the instruction name from the log message
            instruction_name = msg.split(' ')[3]
            instruction_name = instruction_name[0].lower() + instruction_name[1:]

            # Find the relevant parsed instruction by name
            instruction = next(
                (pi for pi in parsed_instructions if pi[0] == camel_to_snake(instruction_name)),
                None
            )
            # If no matching instruction is found, continue to the next message
            if not instruction:
                return
            # Remove the matched instruction from the list, so the same instruction is not used twice.
            parsed_instructions.remove(instruction)
            parsed_instruction = instruction[1]
            # Find the index of the instruction in the original transaction
            instruction_index = self.last_tx.transaction.message.instructions.index(parsed_instruction)

            # If the instruction name matches any known instruction from the program, handle the event
            if instruction_name in [i.idl_ix.name for i in self.program.instruction.values()]:
                self._save_mango_instruction(parsed_instruction, instruction_name, instruction_index)
            return
        if msg.startswith("Program data:"):
            self.event_parser.parse_logs([msg], self.save_event)

    def save_event(self, event: Event) -> None:
        """
        Save event based on its name.
        """
        print(event)
        if event.name == "MarginfiAccountCreateEvent":
            self._create_lending_account(event)

    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> None:
        """
        Decodes transaction instructions and correlates with log messages.

        Args:
            transaction_with_meta (EncodedTransactionWithStatusMeta): The transaction data with metadata.

        This method processes a given transaction, attempting to parse its instructions if they
        are encoded and match a known program ID. It also associates these instructions with
        corresponding log messages, and handles specific events accordingly.
        """
        # Storing the transaction for potential later use
        self.last_tx = transaction_with_meta
        # Get Kamino transactions
        parsed_instructions = self._get_mango_instructions(transaction_with_meta)

        # Get log messages from transaction metadata
        log_msgs = transaction_with_meta.meta.log_messages

        # Process each log message related to program instructions
        for msg in log_msgs:
            self._handle_log(msg, parsed_instructions)

    @staticmethod
    def _get_accounts_from_instruction(known_accounts, instruction):
        # Pairing the accounts from the instruction with their names based on their order
        paired_accounts = {}
        for i, account in enumerate(instruction.accounts):
            if i < len(known_accounts):
                paired_accounts[account.name] = known_accounts[i]
        return paired_accounts

    def _save_mango_instruction(  # pylint: disable=too-many-statements, too-many-branches
            self,
            instruction: UiPartiallyDecodedInstruction,
            instruction_name: str,
            instruction_idx: int
    ) -> None:
        """
        Process Kamino instructions based on instruction name
        """
        metadata = next(i for i in self.program.instruction.values() if i.idl_ix.name == instruction_name)
        print('in', instruction_name)

        if instruction_name == 'accountCreate':  # create account
            self.account_status_change(instruction, metadata, instruction_name)

        if instruction_name == 'accountClose':  # close account
            self.account_status_change(instruction, metadata, instruction_name)

        # instructions handled through program data log messages.
        if instruction_name == 'tokenDeposit':
            pass
            # self.deposit(instruction, metadata, instruction_name)


        elif instruction_name == 'initLendingMarket':
            pass
        elif instruction_name == 'updateLendingMarket':
            pass
        elif instruction_name == 'updateLendingMarketOwner':
            pass
        elif instruction_name == 'initReserve':
            pass
        elif instruction_name == 'initFarmsForReserve':
            pass
        elif instruction_name == 'updateSingleReserveConfig':
            pass
        elif instruction_name == 'updateEntireReserveConfig':
            pass

    def account_status_change(self, instruction: UiPartiallyDecodedInstruction, metadata: Any, action: str):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        print(instruction.accounts)
        print(accounts)
        print(instruction)
        new_lending_account = MangoLendingAccounts(
            authority=str(accounts['owner']),
            address=str(accounts['account']),
            group=str(accounts['group']),
            action=action
        )

        self._processor(new_lending_account)

    def deposit(self, instruction: UiPartiallyDecodedInstruction, metadata: Any, instruction_idx, action: str):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        print(instruction.accounts)
        print(accounts)
        print(instruction)
        new_lending_account = MangoLendingAccounts(
            authority=str(accounts['owner']),
            address=str(accounts['account']),
            group=str(accounts['group']),
            action=action
        )

        self._processor(new_lending_account)

    def _update_user_metadata_owner(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')


if __name__ == "__main__":
    from solana.rpc.api import Pubkey, Client

    tx_decoder = MangoTransactionParser()

    token = os.getenv("RPC_URL")

    solana_client = Client(
        token)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '29DRukEKm8NMVM6QNKUm6Q2wvtR8mZ8LCdtXNUVeivwvyu3XSemdco9p6n1rp4WhFQgrnCiDLAw3275Vuk4a655U'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
