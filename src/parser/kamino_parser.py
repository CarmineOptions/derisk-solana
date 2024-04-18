"""
Kamino transaction parser.
"""
from pathlib import Path
from typing import Any, List, Tuple
import logging
import os
import re

from base58 import b58decode
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from db import KaminoParsedTransactions, KaminoLendingAccounts
from src.parser.parser import TransactionDecoder, UnknownInstruction
from src.protocols.addresses import KAMINO_ADDRESS
from src.protocols.idl_paths import KAMINO_IDL_PATH

LOGGER = logging.getLogger(__name__)


def camel_to_snake(name):
    # This pattern identifies places where a lowercase letter is followed by an uppercase letter
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    # Replace such places with an underscore and a lowercase version of the uppercase letter
    snake_case_name = pattern.sub('_', name).lower()
    return snake_case_name


def find_key_by_value(data, target_value):
    for key, value in data.items():
        if value == target_value:
            return key
    return None


class KaminoTransactionParser(TransactionDecoder):

    def __init__(
        self,
        path_to_idl: Path = Path(KAMINO_IDL_PATH),
        program_id: Pubkey = Pubkey.from_string(KAMINO_ADDRESS)
    ):
        self.error = None
        super().__init__(path_to_idl, program_id)

    def _get_kamino_instructions(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> List[Tuple[str, Any]]:
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
                    # If the instruction name matches any known instruction from the program, handle the event
                    # Don't save failed instructions
                except (StreamError, KeyError):
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
            instruction_index = self.transaction.transaction.message.instructions.index(parsed_instruction)
            # Don't save failed instructions
            if self.error and instruction_index == self.error:
                return
            # If the instruction name matches any known instruction from the program, handle the event
            if instruction_name in [i.idl_ix.name for i in self.program.instruction.values()]:
                self._save_kamino_instruction(parsed_instruction, instruction_name, instruction_index)

    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> None:
        """
        Decodes transaction instructions and correlates with log messages.

        Args:
            transaction_with_meta (EncodedTransactionWithStatusMeta): The transaction data with metadata.

        This method processes a given transaction, attempting to parse its instructions if they
        are encoded and match a known program ID. It also associates these instructions with
        corresponding log messages, and handles specific events accordingly.
        """
        # Storing the transaction for later use
        self.transaction = transaction_with_meta
        if not self.transaction.meta:
            return

        if self.transaction.meta.err:
            return
        # Get Kamino transactions
        parsed_instructions = self._get_kamino_instructions(transaction_with_meta)

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
                paired_accounts[account.name] = str(known_accounts[i])
        return paired_accounts

    def _save_kamino_instruction(  # pylint: disable=too-many-statements, too-many-branches
            self,
            instruction: UiPartiallyDecodedInstruction,
            instruction_name: str,
            instruction_idx: int
    ) -> None:
        """
        Process Kamino instructions based on instruction name
        """
        metadata = next(i for i in self.program.instruction.values() if i.idl_ix.name == instruction_name)

        if instruction_name == 'initUserMetadata':  # create account
            self._create_account(instruction, metadata)
        elif instruction_name == 'initObligation':  # initializes a borrowing obligation
            self._init_obligation(instruction, metadata, instruction_idx)
        elif instruction_name == 'initObligationFarmsForReserve':
            pass
        elif instruction_name == 'refreshObligation':
            self._refresh_obligation()
        elif instruction_name == 'refreshReserve':
            self._refresh_reserve()
        elif instruction_name == 'refreshObligationFarmsForReserve':
            self._refresh_obligation_farms_for_reserve()
        elif instruction_name == 'requestElevationGroup':
            self._request_elevation_group()

        elif instruction_name in [
            'depositObligationCollateral',
            'withdrawObligationCollateral',
            'depositReserveLiquidity',
            'redeemReserveCollateral',
            'borrowObligationLiquidity',
            'repayObligationLiquidity',
            'depositReserveLiquidityAndObligationCollateral',
            'withdrawObligationCollateralAndRedeemReserveCollateral',
            'liquidateObligationAndRedeemReserveCollateral',
            'flashRepayReserveLiquidity',
            'flashBorrowReserveLiquidity'
        ]:
            self._parse_inner_instruction(instruction, metadata, instruction_idx, instruction_name)

        elif instruction_name == 'redeemFees':
            self._redeem_fees(instruction, metadata)
        elif instruction_name == 'socializeLoss':
            self._socialize_loss(instruction, metadata)
        elif instruction_name == 'initReferrerTokenState':
            self._init_referrer_token_state(instruction, metadata)
        elif instruction_name == 'updateUserMetadataOwner':
            self._update_user_metadata_owner(instruction, metadata)
        elif instruction_name == 'withdrawReferrerFees':
            self._withdraw_referrer_fees(instruction, metadata)
        elif instruction_name == 'withdrawProtocolFee':
            self._withdraw_protocol_fee(instruction, metadata)
        elif instruction_name == 'initReferrerStateAndShortUrl':
            self._init_referrer_state_and_short_url(instruction, metadata)
        elif instruction_name == 'deleteReferrerStateAndShortUrl':
            self._delete_referrer_state_and_short_url(instruction, metadata)

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

    def _create_account(self, instruction: UiPartiallyDecodedInstruction, metadata):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        new_lending_account = KaminoLendingAccounts(
            authority=str(accounts['feePayer']),
            address=str(accounts['owner']),
            group=None
        )

        self._processor(new_lending_account)

    def _refresh_reserve(self):
        pass

    def _refresh_obligation_farms_for_reserve(self):
        pass

    def _refresh_obligation(self):
        pass

    def _request_elevation_group(self):
        pass

    def _init_obligation(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.transaction.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return
        # Create account record from inner instruction.
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == "createAccount":
                new_obligation = KaminoLendingAccounts(
                    authority=str(info['source']),
                    address=str(info['newAccount']),
                    group=str(accounts['lendingMarket'])
                )
                self._processor(new_obligation)
            else:
                raise UnknownInstruction(i)

    def _parse_inner_instruction(
            self, instruction: UiPartiallyDecodedInstruction, metadata: Any, instruction_idx, action: str):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((
            i for i in self.transaction.meta.inner_instructions if i.index == instruction_idx), None)
        if inner_instructions:
            for inner_instruction in inner_instructions.instructions:
                if inner_instruction.parsed['type'] == 'transfer':
                    transfer = self._parse_transfer_instruction(inner_instruction, accounts, action, instruction_idx)

                    self._processor(transfer)

                if inner_instruction.parsed['type'] == 'mintTo':
                    mint_to = self._parse_mintto_instruction(inner_instruction, accounts, action, instruction_idx)

                    self._processor(mint_to)

                if inner_instruction.parsed['type'] == 'burn':
                    burn = self._parse_burn_instruction(inner_instruction, accounts, action, instruction_idx)

                    self._processor(burn)

    def _parse_transfer_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        """"""
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['token']) if 'token' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['source']
        source_name = find_key_by_value(accounts, source)
        destination = instruction['info']['destination']
        destination_name = find_key_by_value(accounts, destination)
        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{source_name}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        # Create the MangoParsedTransactions object
        return KaminoParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            source=source,
            destination=destination,
            account=account,
            signer=signer,
            bank=bank,
            obligation=obligation
        )

    def _parse_mintto_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        destination = instruction['info']['account']
        destination_name = find_key_by_value(accounts, destination)
        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['mintAuthority'] if 'mintAuthority' in instruction['info'] else None
        bank = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        # Create the MangoParsedTransactions object
        return KaminoParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            destination=destination,
            account=account,
            signer=signer,
            bank=bank,
            obligation=obligation
        )

    def _parse_burn_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['account']
        source_name = find_key_by_value(accounts, source)
        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{source_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        # Create the MangoParsedTransactions object
        return KaminoParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            source=source,
            account=account,
            signer=signer,
            bank=bank,
            obligation=obligation
        )

    def _redeem_fees(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _socialize_loss(self, instruction: UiPartiallyDecodedInstruction, metadata):  # Never happened before
        raise NotImplementedError('Implement me!')

    def _init_referrer_token_state(self, instruction: UiPartiallyDecodedInstruction, metadata):
        pass

    def _init_user_metadata(self, instruction: UiPartiallyDecodedInstruction,
                            metadata):  # Note: Example method provided earlier
        pass

    def _withdraw_referrer_fees(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _withdraw_protocol_fee(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _init_referrer_state_and_short_url(self, instruction: UiPartiallyDecodedInstruction, metadata):
        pass

    def _delete_referrer_state_and_short_url(self, instruction: UiPartiallyDecodedInstruction, metadata):
        pass

    def _update_user_metadata_owner(self, instruction: UiPartiallyDecodedInstruction, metadata):
        pass


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = KaminoTransactionParser(
        Path('src/protocols/idls/kamino_idl.json'),
        Pubkey.from_string("KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD")
    )

    rpc_url = os.getenv("RPC_URL")

    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '5hirYUZUd43y4pZkGbMBekPLL4sad6b1f2bnFLak6YkWQq9xtswqAQmHkyH3mxkFp8jCpu28hJgsXTCvZqPFm8t'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
