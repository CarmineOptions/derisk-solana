"""
Kamino transaction parser.
"""
from pathlib import Path
from typing import Any, List, Tuple
import inspect
import logging
import os
import re

from anchorpy.program.common import Event
from base58 import b58decode
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction
import construct.core

from db import MangoParsedTransactions, MangoLendingAccounts
from src.parser.parser import TransactionDecoder, UnknownInstruction
from src.protocols.addresses import MANGO_ADDRESS
from src.protocols.idl_paths import MANGO_IDL_PATH

LOGGER = logging.getLogger(__name__)


# moke function to avoid StreamError while parsing mango event `UpdateIndexLog`
def stream_read_muted(stream, length, path):
    if length < 0:
        raise construct.core.StreamError("length must be non-negative, found %s" % length, path=path)
    try:
        data = stream.read(length)
    except Exception:
        raise construct.core.StreamError("stream.read() failed, requested %s bytes" % (length,), path=path)
    # if len(data) != length:
    #     raise construct.core.StreamError("stream read less than specified amount, expected %d, found %d" % (length, len(data)), path=path)
    return data


construct.core.stream_read = stream_read_muted


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
        self.event_counter: int | None = None
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
                    # Store the parsed instruction name along with the instruction object
                    parsed_instructions.append((parsed_instruction.name, instruction))
                except construct.core.StreamError:
                    # If parsing fails, simply ignore and continue
                    # Here we assume that relevant instructions do not fail.
                    pass
        return parsed_instructions

    def _handle_log(self, msg):
        if msg.startswith("Program data:"):
            if 'vx89Qqxin' in msg or 'dZKDSrOa2' in msg:  # do not parse 'PerpUpdateFundingLog' and 'PerpUpdateFundingLogV2'
                return
            self.event_parser.parse_logs(
                ['Program 4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg invoke [1]', msg],
                self.save_event
            )

    def save_event(self, event: Event) -> None:
        """
        Save event.
        """
        if event.name in [
            'FlashLoanLog',
            'FlashLoanLogV2',
            'FlashLoanLogV3',
            'WithdrawLog',
            'DepositLog',
            'FillLog',
            'FillLogV2',
            'FillLogV3',
            'TokenLiqWithTokenLog',
            'TokenLiqWithTokenLogV2',
            'TokenCollateralFeeLog',
            'ForceWithdrawLog',
            'WithdrawLoanOriginationFeeLog',
            'WithdrawLoanLog',
            'TokenLiqBankruptcyLog',
            'PerpLiqBankruptcyLog',
            'TokenBalanceLog',
            'UpdateRateLog',
            'UpdateRateLogV2',
            'DeactivateTokenPositionLog',
            'DeactivatePerpPositionLog',
            'UpdateIndexLog'
        ]:
            flat_event = self._flatten_event_data(event.data)
            mango_event = MangoParsedTransactions(
                transaction_id=str(self.last_tx.transaction.signatures[0]),
                event_name=event.name,
                event_number=self.event_counter,
                **{camel_to_snake(k): v for k, v in flat_event.items()}
            )
            self._processor(mango_event)
            self.event_counter += 1

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
        # self.last_tx = transaction_with_meta
        # self.error = transaction_with_meta.meta.err.index if transaction_with_meta.meta.err else None
        # self.event_counter = 0
        # # Get Kamino transactions
        # parsed_instructions = self._get_mango_instructions(transaction_with_meta)

        # Get log messages from transaction metadata
        log_msgs = transaction_with_meta.meta.log_messages
        # self.event_parser.parse_logs(log_msgs, self.save_event)
        # Process each log message related to program instructions
        for msg in log_msgs:
            self._handle_log(msg)

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

        if instruction_name == 'accountCreate':  # create account
            self._account_status_change(instruction, metadata, instruction_name)

        if instruction_name == 'accountClose':  # close account
            self._account_status_change(instruction, metadata, instruction_name)

        if instruction_name == 'tokenLiqWithToken':  # handled with event
            pass
        # collect rare event to parse later.
        if instruction_name in [
            'liqTokenWithToken',
            'liqTokenBankruptcy',
            'tokenForceCloseBorrowsWithToken',
            'tokenLiqBankruptcy',
            'tokenDepositIntoExisting',
        ]:
            LOGGER.warning(f"Instruction `{instruction_name} found in `{str(self.last_tx.transaction.signatures[0])}`.")

        # instructions handled through program data log messages.
        # expected instructions are
        #     'tokenDeposit',
        #     'tokenWithdraw',
        #     'flashLoanBegin',
        #     'flashLoanSwapBegin',
        #     'flashLoanEnd',
        #     'flashLoanEndV2'
        # but all other instructions are parsed if there is a transfer inner instruction in it.
        self._token_transfer(instruction, metadata, instruction_idx, instruction_name)

    def _account_status_change(self, instruction: UiPartiallyDecodedInstruction, metadata: Any, action: str):
        """ """
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        new_lending_account = MangoLendingAccounts(
            authority=str(accounts['owner']),
            address=str(accounts['account']),
            group=str(accounts['group']),
            action=action
        )

        self._processor(new_lending_account)

    def _token_transfer(self, instruction: UiPartiallyDecodedInstruction, metadata: Any, instruction_idx, action: str):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        if inner_instructions:
            for inner_instruction in inner_instructions.instructions:
                if inner_instruction.parsed['type'] == 'transfer':
                    transfer = self._parse_transfer_instruction(inner_instruction, accounts, action, instruction_idx)

                    self._processor(transfer)

                else:
                    raise UnknownInstruction(inner_instruction)

    def _liquidation(self, event: Event):
        """"""
        data = event.data
        asset_transfer_from_liqee = MangoParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name=event.name,
            event_name='asset_transfer_from_liqee',
            event_number=self.event_counter,

            position='asset',
            token=data.asset_token_index,
            amount=data.asset_transfer_from_liqee,
            source=str(data.liqee),
            destination=None,
            group=str(data.mango_group)
        )

        asset_transfer_to_liqor = MangoParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name=event.name,
            event_name='asset_transfer_to_liqor',
            event_number=self.event_counter,

            position='asset',
            token=data.asset_token_index,
            amount=data.asset_transfer_to_liqor,
            source= None,
            destination=str(data.liqor),
            group=str(data.mango_group)
        )

        asset_liquidation_fee = MangoParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name=event.name,
            event_name='asset_liquidation_fee',
            event_number=self.event_counter,

            position='asset',
            token=data.asset_token_index,
            amount=data.asset_liquidation_fee,
            source= None,
            destination=None,
            group=str(data.mango_group)
        )

        liab_transfer = MangoParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name=event.name,
            event_name='liab_transfer',
            event_number=self.event_counter,

            position='liability',
            token=data.liab_token_index,
            amount=data.liab_transfer,
            source= str(data.liqee),
            destination=str(data.liqor),
            group=str(data.mango_group)
        )

        self._processor(asset_transfer_to_liqor)
        self._processor(asset_transfer_from_liqee)
        self._processor(asset_liquidation_fee)
        self._processor(liab_transfer)

        self.event_counter += 1

    def _parse_transfer_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        instruction = inner_instruction.parsed

        # Extracting data
        token = str(accounts['tokenAccount']) if 'tokenAccount' in accounts else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['source']
        destination = instruction['info']['destination']
        event_name = instruction['type']
        event_number = instruction_idx

        # Matching keys in accounts dictionary
        account = str(accounts['account']) if 'account' in accounts else None
        signer = str(accounts['owner']) if 'owner' in accounts else None
        bank = str(accounts['bank']) if 'bank' in accounts else None
        group = str(accounts['group']) if 'group' in accounts else None

        # Create the MangoParsedTransactions object
        return MangoParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name=instruction_name,
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            source=source,
            destination=destination,
            account=account,
            signer=signer,
            bank=bank,
            group=group
        )

    @staticmethod
    def _flatten_event_data(obj) -> dict:
        attributes = {}
        # Get all attributes of the object, including inherited ones
        for attr in dir(obj):
            if not attr.startswith("__") and not attr.startswith("_"):
                attribute = getattr(obj, attr)
                if type(attribute).__name__ == 'ListContainer':
                    fields_in_list = {}
                    for idx, value in enumerate(attribute):
                        fields_in_list[idx] = value.__dict__
                    fields_flat = {
                            f"{key}_{i+1}": value
                            for i, v in fields_in_list.items()
                            for key, value in v.items()
                        }
                    attributes.update(fields_flat)
                    continue
                # Add attribute to dictionary if it's not a method
                if not inspect.ismethod(attribute) and attr not in [
                    'flash_loan_type', 'loan_origination_fee_instruction'
                ]:
                    attributes[attr] = attribute if not isinstance(attribute, Pubkey) else str(attribute)
        return attributes


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = MangoTransactionParser()
    rpc_url = os.getenv("RPC_URL")
    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet
    transaction = solana_client.get_transaction(
        Signature.from_string(
            # '3QBx7uhgy4PBGWY93qpKgxv9WDS2BS7aWXNgDwHq4tgUXmNvvd6sUQUGzpoJCqwVx5w9MzPL3rzqX2yiwW9R75kD'  # liq
            '3a2S23GbLxunNUTCyriULoPn9m5AFjcYE7gAySF4pXkxVx6RzDq7BtWunEmkoE6xsWjEALg4HeouE6BH3FiQtxkB'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
