"""
Marginfi transaction parser.
"""
from pathlib import Path
from typing import Any, List, Tuple, Dict
import logging
import os
import re

from base58 import b58decode

from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction, \
    ParsedInstruction

from db import KaminoObligationV2, KaminoParsedTransactionsV2, KaminoReserveV2
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


class InnerInstructionContainer:
    """ Class for storing inner instructions. """
    def __init__(self, inner_instructions):
        self.instructions = inner_instructions


class KaminoTransactionParserV2(TransactionDecoder):

    def __init__(
        self,
        path_to_idl: Path = Path(KAMINO_IDL_PATH),
        program_id: Pubkey = Pubkey.from_string(KAMINO_ADDRESS)
    ):
        self.error = None
        super().__init__(path_to_idl, program_id)

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
        for instruction_index, instruction in enumerate(self.transaction.transaction.message.instructions):
            # Check if instruction is partially decoded and belongs to the known program
            if isinstance(instruction, UiPartiallyDecodedInstruction) and instruction.program_id == self.program_id:
                # instruction_index = self.transaction.transaction.message.instructions.index(instruction)
                data = instruction.data
                msg_bytes = b58decode(str.encode(str(data)))
                try:
                    parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                except:
                    LOGGER.warning(f"Fail to read instruction: {msg_bytes} "
                                   f"in `{str(self.transaction.transaction.signatures[0])}`")
                    continue
                self._save_kamino_instruction(
                    instruction, snake_to_camel(parsed_instruction.name), instruction_index, parsed_instruction)
        #
        for instruction in self.transaction.meta.inner_instructions:
            instruction_index = instruction.index
            for idx, inner_instruction in enumerate(instruction.instructions):
                if isinstance(inner_instruction, UiPartiallyDecodedInstruction) and inner_instruction.program_id == self.program_id:
                    kl_instruction = inner_instruction

                    related_inner_instructions = []
                    if idx + 1 < len(instruction.instructions):
                        for following_instruction in instruction.instructions[idx + 1:]:
                            if isinstance(following_instruction, ParsedInstruction):
                                related_inner_instructions.append(following_instruction)
                            else:
                                break

                    if related_inner_instructions:
                        contained_inner_instructions = InnerInstructionContainer(related_inner_instructions)
                    else:
                        contained_inner_instructions = InnerInstructionContainer(None)

                    data = kl_instruction.data
                    msg_bytes = b58decode(str.encode(str(data)))
                    try:
                        parsed_instruction = self.program.coder.instruction.parse(msg_bytes)
                    except:
                        LOGGER.warning(f"Fail to read instruction: {msg_bytes} "
                                       f"in `{str(self.transaction.transaction.signatures[0])}`")
                        continue
                    self._save_kamino_instruction(
                        kl_instruction,
                        snake_to_camel(parsed_instruction.name),
                        instruction_index,
                        parsed_instruction,
                        contained_inner_instructions
                    )

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
            instruction_idx: int | None,
            parsed_instruction: Any,
            inner_instructions: Any | None = None
    ) -> None:
        """
        Process Kamino instructions based on instruction name
        """
        metadata = next(i for i in self.program.instruction.values() if i.idl_ix.name == instruction_name)

        if instruction_name == 'initObligation':  # create account
            self._create_obligation(instruction, metadata)

        if instruction_name == 'initReserve':
            self._create_reserve(instruction, metadata)

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
            self._parse_inner_instruction(
                instruction, metadata, instruction_idx, instruction_name, parsed_instruction, inner_instructions)

    def _create_obligation(self, instruction: UiPartiallyDecodedInstruction, metadata):
        """"""
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        new_lending_account = KaminoObligationV2(
            authority=str(accounts['obligationOwner']),
            address=str(accounts['obligation']),
            group=str(accounts['lendingMarket'])
        )

        self._processor(new_lending_account)

    def _create_reserve(self, instruction: UiPartiallyDecodedInstruction, metadata):
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Create new reserve instance
        new_bank = KaminoReserveV2(
            lending_market=accounts.get('lending_market', ''),
            lending_market_owner=accounts.get('lending_market_owner', ''),
            reserve=accounts.get('reserve', ''),
            reserve_liquidity_mint=accounts.get('reserve_liquidity_mint', ''),
            reserve_liquidity_supply=accounts.get('reserve_liquidity_supply', ''),
            fee_receiver=accounts.get('fee_receiver', ''),
            reserve_collateral_mint=accounts.get('reserve_collateral_mint', ''),
            reserve_collateral_supply=accounts.get('reserve_collateral_supply', ''),
            rent=accounts.get('rent', '')
        )

        self._processor(new_bank)

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
        # Locate inner instructions related            # print(instruction) to the primary instruction by index
        if not inner_instructions:
            inner_instructions = next((
                i for i in self.transaction.meta.inner_instructions if i.index == instruction_idx), None)

        if inner_instructions and inner_instructions.instructions:
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
                        inner_instruction, accounts, action, instruction_idx, parsed_instruction)

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
        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{source_name}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['reserve']) if 'reserve' in accounts else None
        lending_market = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        if instruction_name == 'liquidateObligationAndRedeemReserveCollateral':
            liquidator = str(accounts['liquidator']) if 'liquidator' in accounts else None
            instructed_amount = parsed_instruction.data.liquidity_amount
            withdraw_reserve = str(accounts['withdrawReserve']) if 'withdrawReserve' in accounts else None
            repay_reserve = str(accounts['repayReserve']) if 'repayReserve' in accounts else None

            return KaminoParsedTransactionsV2(
                transaction_id=str(self.transaction.transaction.signatures[0]),
                instruction_name=camel_to_snake(instruction_name),
                event_name=event_name,
                event_number=event_number,
                obligation=obligation,
                token=token,
                amount=amount,
                source=source,
                destination=destination,
                account=account,
                signer=signer,
                bank=bank,
                lending_market=lending_market,
                liquidator=liquidator,
                withdraw_reserve=withdraw_reserve,
                repay_reserve=repay_reserve,
                liquidity_amount=instructed_amount
            )
        # Create the MangoParsedTransactions object
        return KaminoParsedTransactionsV2(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            obligation=obligation,
            token=token,
            amount=amount,
            source=source,
            destination=destination,
            account=account,
            signer=signer,
            bank=bank,
            lending_market=lending_market
        )

    def _parse_mintto_instruction(
            self, inner_instruction, accounts, instruction_name: str, instruction_idx: int, parsed_instruction: Any):
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
        bank = str(accounts['reserve']) if 'reserve' in accounts else None
        lending_market = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None
        if instruction_name == 'liquidateObligationAndRedeemReserveCollateral':
            liquidator = str(accounts['liquidator']) if 'liquidator' in accounts else None
            instructed_amount = parsed_instruction.data.liquidity_amount
            withdraw_reserve = str(accounts['withdrawReserve']) if 'withdrawReserve' in accounts else None
            repay_reserve = str(accounts['repayReserve']) if 'repayReserve' in accounts else None

            return KaminoParsedTransactionsV2(
                transaction_id=str(self.transaction.transaction.signatures[0]),
                instruction_name=camel_to_snake(instruction_name),
                event_name=event_name,
                event_number=event_number,
                obligation=obligation,
                token=token,
                amount=amount,
                destination=destination,
                account=account,
                signer=signer,
                bank=bank,
                lending_market=lending_market,
                liquidator=liquidator,
                withdraw_reserve=withdraw_reserve,
                repay_reserve=repay_reserve,
                liquidity_amount=instructed_amount
            )
        # Create the KaminoParsedTransactions object
        return KaminoParsedTransactionsV2(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            obligation=obligation,
            token=token,
            amount=amount,
            destination=destination,
            account=account,
            signer=signer,
            bank=bank,
            lending_market=lending_market
        )

    def _parse_burn_instruction(
            self, inner_instruction, accounts, instruction_name: str, instruction_idx: int, parsed_instruction: Any):
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
        signer = instruction['info']['mintAuthority'] if 'mintAuthority' in instruction['info'] else None
        bank = str(accounts['reserve']) if 'reserve' in accounts else None
        lending_market = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None
        if instruction_name == 'liquidateObligationAndRedeemReserveCollateral':
            liquidator = str(accounts['liquidator']) if 'liquidator' in accounts else None
            instructed_amount = parsed_instruction.data.liquidity_amount
            withdraw_reserve = str(accounts['withdrawReserve']) if 'withdrawReserve' in accounts else None
            repay_reserve = str(accounts['repayReserve']) if 'repayReserve' in accounts else None

            return KaminoParsedTransactionsV2(
                transaction_id=str(self.transaction.transaction.signatures[0]),
                instruction_name=camel_to_snake(instruction_name),
                event_name=event_name,
                event_number=event_number,
                obligation=obligation,
                token=token,
                amount=amount,
                source=source,
                account=account,
                signer=signer,
                bank=bank,
                lending_market=lending_market,
                liquidator=liquidator,
                withdraw_reserve=withdraw_reserve,
                repay_reserve=repay_reserve,
                liquidity_amount=instructed_amount
            )
        # Create the KaminoParsedTransactions object
        return KaminoParsedTransactionsV2(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=camel_to_snake(instruction_name),
            event_name=event_name,
            event_number=event_number,
            obligation=obligation,
            token=token,
            amount=amount,
            source=source,
            account=account,
            signer=signer,
            bank=bank,
            lending_market=lending_market
        )


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = KaminoTransactionParserV2()

    rpc_url = os.getenv("RPC_URL")

    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '3bZHnoSaN1fPPmsVMnfjyfeU76wRXWxKKH4mBZ51sJiiryahu3tJZRk3YSi92fnRqT5wNZanUv6in4WFo7HKNvS9'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
