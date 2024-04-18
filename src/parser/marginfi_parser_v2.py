"""
Marginfi transaction parser.
"""
from pathlib import Path
from typing import Any, List, Tuple, Dict
import logging
import os
import re

from base58 import b58decode
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction, \
    ParsedInstruction

from db import MarginfiLendingAccountsV2, MarginfiParsedTransactionsV2, MarginfiBankV2
from src.parser.parser import TransactionDecoder, UnknownInstruction
from src.protocols.addresses import MARGINFI_ADDRESS
from src.protocols.idl_paths import MARGINFI_IDL_PATH

LOGGER = logging.getLogger(__name__)


def camel_to_snake(name):
    # This pattern identifies places where a lowercase letter is followed by an uppercase letter
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    # Replace such places with an underscore and a lowercase version of the uppercase letter
    snake_case_name = pattern.sub('_', name).lower()
    return snake_case_name


def snake_to_camel(snake_str):
    # Split the string into words based on underscores
    components = snake_str.split('_')
    # Capitalize the first letter of each component except the first one
    # and join them back into a single string
    return components[0] + ''.join(x.title() for x in components[1:])


def find_key_by_value(data, target_value):
    for key, value in data.items():
        if value == target_value:
            return key
    return None


class MarginfiTransactionParserV2(TransactionDecoder):

    def __init__(
        self,
        path_to_idl: Path = Path(MARGINFI_IDL_PATH),
        program_id: Pubkey = Pubkey.from_string(MARGINFI_ADDRESS)
    ):
        self.error = None
        super().__init__(path_to_idl, program_id)

    def _get_marginfi_instructions(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> List[Tuple[str, Any]]:
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
        # Parse instructions:
        for instruction in self.transaction.transaction.message.instructions:
            # print(instruction)
            # Check if instruction is partially decoded and belongs to the known program
            if isinstance(instruction, UiPartiallyDecodedInstruction) and instruction.program_id == self.program_id:
                instruction_index = self.transaction.transaction.message.instructions.index(instruction)
                data = instruction.data
                msg_bytes = b58decode(str.encode(str(data)))
                try:
                    parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                except:
                    continue
                self._save_marginfi_instruction(
                    instruction, snake_to_camel(parsed_instruction.name), instruction_index, parsed_instruction)
        for idx, instruction in enumerate(self.transaction.meta.inner_instructions):
            # print(instruction.instructions)
            for inner_instruction in instruction.instructions:
                if isinstance(inner_instruction, UiPartiallyDecodedInstruction) and inner_instruction.program_id == self.program_id:
                    # print(inner_instruction)
                    mf_instruction = inner_instruction
                    related_inner_instructions = instruction
                    instruction_index = idx
                    data = mf_instruction.data
                    msg_bytes = b58decode(str.encode(str(data)))
                    try:
                        parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                    except:
                        continue
                    self._save_marginfi_instruction(
                        mf_instruction,
                        snake_to_camel(parsed_instruction.name),
                        instruction_index,
                        parsed_instruction,
                        related_inner_instructions
                    )

    @staticmethod
    def _get_accounts_from_instruction(known_accounts, instruction):
        # Pairing the accounts from the instruction with their names based on their order
        paired_accounts = {}
        for i, account in enumerate(instruction.accounts):
            if i < len(known_accounts):
                paired_accounts[account.name] = str(known_accounts[i])
        return paired_accounts

    def _save_marginfi_instruction(  # pylint: disable=too-many-statements, too-many-branches
            self,
            instruction: UiPartiallyDecodedInstruction,
            instruction_name: str,
            instruction_idx: int | None,
            parsed_instruction: Any,
            inner_instructions: Any | None = None
    ) -> None:
        """
        Process Kamino instructions based on instruction name
        ['marginfiGroupInitialize',
         'marginfiGroupConfigure',
         'lendingPoolAddBank',
         'lendingPoolAddBankWithSeed',
         'lendingPoolConfigureBank',
         'lendingPoolSetupEmissions',
         'lendingPoolUpdateEmissionsParameters',
         'lendingPoolHandleBankruptcy',

         'marginfiAccountInitialize',

         'lendingAccountDeposit',
         'lendingAccountRepay',
         'lendingAccountWithdraw',
         'lendingAccountBorrow',
         'lendingAccountCloseBalance',
         'lendingAccountWithdrawEmissions',
         'lendingAccountSettleEmissions',
         'lendingAccountLiquidate',
         'lendingAccountStartFlashloan',
         'lendingAccountEndFlashloan',

         'lendingPoolAccrueBankInterest',
         'lendingPoolCollectBankFees',
         'setAccountFlag',
         'unsetAccountFlag',
         'setNewAccountAuthority
        """
        metadata = next(i for i in self.program.instruction.values() if i.idl_ix.name == instruction_name)

        if instruction_name == 'marginfiAccountInitialize':  # create account
            self._create_account(instruction, metadata)

        if instruction_name == 'lendingPoolAddBank':
            self._create_bank(instruction, metadata)

        elif instruction_name in [
            'lendingAccountDeposit',
            'lendingAccountRepay',
            'lendingAccountWithdraw',
            'lendingAccountBorrow',
            'lendingAccountCloseBalance',
            'lendingAccountWithdrawEmissions',
            'lendingAccountSettleEmissions',
            'lendingAccountLiquidate',
            'lendingAccountStartFlashloan',
            'lendingAccountEndFlashloan',
        ]:
            self._parse_inner_instruction(
                instruction, metadata, instruction_idx, instruction_name, parsed_instruction, inner_instructions)

    def _create_account(self, instruction: UiPartiallyDecodedInstruction, metadata):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        new_lending_account = MarginfiLendingAccountsV2(
            authority=str(accounts['feePayer']),
            address=str(accounts['marginfiAccount']),
            group=str(accounts['marginfiGroup'])
        )

        self._processor(new_lending_account)

    def _create_bank(self, instruction: UiPartiallyDecodedInstruction, metadata):
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Create new bank instance
        new_bank = MarginfiBankV2(
            marginfi_group=accounts.get('marginfiGroup', ''),
            admin=accounts.get('admin', ''),
            fee_payer=accounts.get('feePayer', ''),
            bank_mint=accounts.get('bankMint', ''),
            bank=accounts.get('bank', ''),
            liquidity_vault_authority=accounts.get('liquidityVaultAuthority', ''),
            liquidity_vault=accounts.get('liquidityVault', ''),
            insurance_vault_authority=accounts.get('insuranceVaultAuthority', ''),
            insurance_vault=accounts.get('insuranceVault', ''),
            fee_vault_authority=accounts.get('feeVaultAuthority', ''),
            fee_vault=accounts.get('feeVault', ''),
            rent=accounts.get('rent', '')
        )

        self._processor(new_bank)

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
                new_obligation = MarginfiLendingAccountsV2(
                    authority=str(info['source']),
                    address=str(info['newAccount']),
                    group=str(accounts['lendingMarket'])
                )
                self._processor(new_obligation)
            else:
                raise UnknownInstruction(i)

    def _parse_inner_instruction(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx,
            action: str,
            parsed_instruction: Any,
            inner_instructions: Any | None = None
    ):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        if not inner_instructions:
            inner_instructions = next((
                i for i in self.transaction.meta.inner_instructions if i.index == instruction_idx), None)

        if inner_instructions:
            for inner_instruction in inner_instructions.instructions:
                if not hasattr(inner_instruction, 'parsed'):
                    continue
                if inner_instruction.parsed['type'] == 'transfer':
                    transfer = self._parse_transfer_instruction(
                        inner_instruction, accounts, action, instruction_idx, parsed_instruction)

                    self._processor(transfer)

                elif inner_instruction.parsed['type'] == 'mintTo':
                    mint_to = self._parse_mintto_instruction(
                        inner_instruction, accounts, action, instruction_idx, parsed_instruction)

                    self._processor(mint_to)

                elif inner_instruction.parsed['type'] == 'burn':
                    burn = self._parse_burn_instruction(
                        inner_instruction, accounts, action, instruction_idx)

                    self._processor(burn)

                else:
                    LOGGER.warning(f"Unknown instruction: "
                                   f"{inner_instruction.parsed['type']} "
                                   f"for tx = `{str(self.transaction.transaction.signatures[0])}`")

    def _parse_transfer_instruction(
            self,
            inner_instruction,
            accounts,
            instruction_name: str,
            instruction_idx: int,
            parsed_instruction: Any
    ):
        """"""
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['token']) if 'token' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['source']
        source_name = find_key_by_value(accounts, source)
        destination = instruction['info']['destination']
        destination_name = find_key_by_value(accounts, destination)

        event_name = f"{instruction['type']}-{source_name}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['marginfiAccount']) if 'marginfiAccount' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['bank']) if 'bank' in accounts else None
        marginfi_group = str(accounts['marginfiGroup']) if 'marginfiGroup' in accounts else None

        if instruction_name == 'lendingAccountLiquidate':
            asset_bank = str(accounts['assetBank']) if 'assetBank' in accounts else None
            liab_bank = str(accounts['liabBank']) if 'liabBank' in accounts else None
            liquidator_marginfi_account = str(accounts['liquidatorMarginfiAccount']) \
                if 'liquidatorMarginfiAccount' in accounts else None
            liquidatee_marginfi_account = str(accounts['liquidateeMarginfiAccount']) \
                if 'liquidateeMarginfiAccount' in accounts else None
            instructed_amount = parsed_instruction.data.asset_amount
            return MarginfiParsedTransactionsV2(
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
                marginfi_group=marginfi_group,
                asset_bank=asset_bank,
                liab_bank=liab_bank,
                liquidator_marginfi_account=liquidator_marginfi_account,
                liquidatee_marginfi_account=liquidatee_marginfi_account,
                instructed_amount=instructed_amount
            )
        # Create the MangoParsedTransactions object
        return MarginfiParsedTransactionsV2(
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
            marginfi_group=marginfi_group
        )

    def _parse_mintto_instruction(
            self, inner_instruction, accounts, instruction_name: str, instruction_idx: int, parsed_instruction: Any):
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        destination = instruction['info']['account']
        destination_name = find_key_by_value(accounts, destination)

        event_name = f"{instruction['type']}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['marginfiAccount']) if 'marginfiAccount' in accounts else None
        signer = instruction['info']['mintAuthority'] if 'mintAuthority' in instruction['info'] else None
        bank = str(accounts['bank']) if 'bank' in accounts else None
        marginfi_group = str(accounts['marginfiGroup']) if 'marginfiGroup' in accounts else None

        # Create the MangoParsedTransactions object
        return MarginfiParsedTransactionsV2(
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
            marginfi_group=marginfi_group
        )

    def _parse_burn_instruction(
            self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['account']
        source_name = find_key_by_value(accounts, source)

        event_name = f"{instruction['type']}-{source_name}"
        event_number = instruction_idx

        account = str(accounts['marginfiAccount']) if 'marginfiAccount' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['bank']) if 'bank' in accounts else None
        marginfi_group = str(accounts['marginfiGroup']) if 'marginfiGroup' in accounts else None

        # Create the MangoParsedTransactions object
        return MarginfiParsedTransactionsV2(
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
            marginfi_group=marginfi_group
        )


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = MarginfiTransactionParserV2(
        Path(MARGINFI_IDL_PATH),
        Pubkey.from_string(MARGINFI_ADDRESS)
    )

    rpc_url = os.getenv("RPC_URL")

    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '2zzc14Y6QNq6tB7NYPMLs8ssb12qd6xjoDNV1x2CQdoqnSjvLueRFbiGETFC6EdKn2DA1KR8HVQgmKk2c4XnQRdL' # liq
            # '26SP3VFxhT2UiDfL9en2sB52cA9suq9A3vxjSMQkbyWUgcoKRUD8aL2VYsp1AG5HN9EbL2soqVWK874TKhsnJ9Yo'  # create bnk
            # '5WPYSVyXPWDn61gduWdz3sTkofzWKUBMH9RbM6iwxYbfe4JKMEk8f6rWBUcbDRrfLZWmAGfPBASvWm4Bgt9RmXe'  # nested mf instr
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
