"""
Kamino transaction parser.
"""
import os
import re
from pathlib import Path
from typing import Any, List, Tuple

from base58 import b58decode
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction
from construct.core import StreamError

from src.parser.parser import TransactionDecoder, UnknownInstruction
from db import KaminoParsedTransactions, KaminoLendingAccounts


def camel_to_snake(name):
    # This pattern identifies places where a lowercase letter is followed by an uppercase letter
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    # Replace such places with an underscore and a lowercase version of the uppercase letter
    snake_case_name = pattern.sub('_', name).lower()
    return snake_case_name


class KaminoTransactionParser(TransactionDecoder):

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
                self._save_kamino_instruction(parsed_instruction, instruction_name, instruction_index)

    def decode_tx(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> None:
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
                paired_accounts[account.name] = known_accounts[i]
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
            self._init_obligation_farms_for_reserve(instruction, metadata, instruction_idx)

        # refresh banks TODO do we need it?
        elif instruction_name == 'refreshObligation':
            self._refresh_obligation()
        elif instruction_name == 'refreshReserve':
            self._refresh_reserve()
        elif instruction_name == 'refreshObligationFarmsForReserve':
            self._refresh_obligation_farms_for_reserve()
        elif instruction_name == 'requestElevationGroup':
            self._request_elevation_group()

        elif instruction_name == 'depositObligationCollateral':  # TODO never happened
            self._deposit_obligation_collateral(instruction, metadata)
        elif instruction_name == 'withdrawObligationCollateral':  # TODO never happened
            self._withdraw_obligation_collateral(instruction, metadata)
        elif instruction_name == 'depositReserveLiquidity':  # TODO never happened
            self._deposit_reserve_liquidity(instruction, metadata, instruction_idx)
        elif instruction_name == 'redeemReserveCollateral':  # TODO never happened
            self._redeem_reserve_collateral(instruction, metadata, instruction_idx)

        elif instruction_name == 'borrowObligationLiquidity':
            self._borrow_obligation_liquidity(instruction, metadata, instruction_idx)

        elif instruction_name == 'repayObligationLiquidity':
            self._repay_obligation_liquidity(instruction, metadata, instruction_idx)

        elif instruction_name == 'depositReserveLiquidityAndObligationCollateral':
            self._deposit_reserve_liquidity_and_obligation_collateral(instruction, metadata, instruction_idx)

        elif instruction_name == 'withdrawObligationCollateralAndRedeemReserveCollateral':
            self._withdraw_obligation_collateral_and_redeem_reserve_collateral(instruction, metadata, instruction_idx)

        elif instruction_name == 'liquidateObligationAndRedeemReserveCollateral':
            self._liquidate_obligation_and_redeem_reserve_collateral(instruction, metadata, instruction_idx)

        elif instruction_name == 'flashRepayReserveLiquidity':
            self._flash_repay_reserve_liquidity(instruction, metadata, instruction_idx)

        elif instruction_name == 'flashBorrowReserveLiquidity':
            self._flash_borrow_reserve_liquidity(instruction, metadata, instruction_idx)

        elif instruction_name == 'redeemFees':  # TODO no transactions found
            self._redeem_fees(instruction, metadata)
        elif instruction_name == 'socializeLoss':  # TODO no transactions found
            self._socialize_loss(instruction, metadata)
        elif instruction_name == 'initReferrerTokenState':  # TODO no transactions found
            self._init_referrer_token_state(instruction, metadata)
        elif instruction_name == 'updateUserMetadataOwner':  # TODO no transactions found
            self._update_user_metadata_owner(instruction, metadata)
        elif instruction_name == 'withdrawReferrerFees':  # TODO no transactions found
            self._withdraw_referrer_fees(instruction, metadata)
        elif instruction_name == 'withdrawProtocolFee':  # TODO no transactions found
            self._withdraw_protocol_fee(instruction, metadata)
        elif instruction_name == 'initReferrerStateAndShortUrl':  # TODO no transactions found
            self._init_referrer_state_and_short_url(instruction, metadata)
        elif instruction_name == 'deleteReferrerStateAndShortUrl':  # TODO no transactions found
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

    def _deposit_obligation_collateral(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _withdraw_obligation_collateral(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _deposit_reserve_liquidity(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        raise NotImplementedError('Implement me!')

    def _redeem_reserve_collateral(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        raise NotImplementedError('Implement me!')

    def _init_obligation(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
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

    def _init_obligation_farms_for_reserve(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return
        # Create account record from inner instruction.
        for i in inner_instructions.instructions:
            # skip irrelevant transactions
            if isinstance(i, UiPartiallyDecodedInstruction):
                continue
            info = i.parsed['info']
            if i.parsed['type'] == "createAccount":
                new_obligation_farm = KaminoLendingAccounts(
                    authority=str(info['source']),
                    address=str(info['newAccount']),
                    group=str(accounts['farmsProgram'])
                )
                self._processor(new_obligation_farm)
            else:
                raise UnknownInstruction(i)

    def _borrow_obligation_liquidity(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return

        # Process each inner instruction based on its type and relevant account roles
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                if info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['reserveSourceLiquidity']) \
                        and info['destination'] == str(accounts['userDestinationLiquidity']):
                    repay_liquidity = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='borrow_obligation_liquidity',
                        event_name='transfer-reserveSourceLiquidity-userDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),


                        account=str(accounts['owner']),
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(repay_liquidity)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _repay_obligation_liquidity(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return

        # Process each inner instruction based on its type and relevant account roles
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                if info['authority'] == str(accounts['owner']) \
                        and info['source'] == str(accounts['userSourceLiquidity']) \
                        and info['destination'] == str(accounts['reserveDestinationLiquidity']):
                    repay_liquidity = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='repay_obligation_liquidity',
                        event_name='transfer-userSourceLiquidity-reserveDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),


                        account=str(accounts['owner']),
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(repay_liquidity)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _deposit_reserve_liquidity_and_obligation_collateral(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                # deposit reserve
                if info['authority'] == str(accounts['owner']) \
                        and info['source'] == str(accounts['userSourceLiquidity']) \
                        and info['destination'] == str(accounts['reserveLiquiditySupply']):
                    deposit_reserve = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='deposit_reserve_liquidity_and_obligation_collateral',
                        event_name='transfer-userSourceLiquidity-reserveLiquiditySupply',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=str(accounts['owner']),
                        signer=str(accounts['owner']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(deposit_reserve)
                # deposit collateral
                elif info['authority'] == str(accounts['owner']) \
                        and info['source'] == str(accounts['userDestinationCollateral']) \
                        and info['destination'] == str(accounts['reserveDestinationDepositCollateral']):
                    deposit_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='deposit_reserve_liquidity_and_obligation_collateral',
                        event_name='transfer-userDestinationCollateral-reserveDestinationDepositCollateral',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=info['source'],
                        destination=info['destination'],

                        account=str(accounts['owner']),
                        signer=str(accounts['owner']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(deposit_collateral)

                else:
                    raise UnknownInstruction(i)

            elif i.parsed['type'] == 'mintTo':
                if info['mintAuthority'] == str(accounts['lendingMarketAuthority']) \
                        and info['account'] == str(accounts['userDestinationCollateral']) \
                        and info['mint'] == str(accounts['reserveCollateralMint']):
                    mint_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='deposit_reserve_liquidity_and_obligation_collateral',
                        event_name='mintTo-userDestinationCollateral',
                        event_number=instruction_idx,

                        token=info['mint'],
                        amount=int(info['amount']),
                        destination=str(info['account']),

                        account=str(accounts['owner']),
                        signer=str(accounts['owner']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(mint_collateral)

                elif info['mintAuthority'] == str(accounts['lendingMarketAuthority']) \
                        and info['account'] == str(accounts['reserveDestinationDepositCollateral']) \
                        and info['mint'] == str(accounts['reserveCollateralMint']):
                    mint_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='deposit_reserve_liquidity_and_obligation_collateral',
                        event_name='mintTo-reserveDestinationDepositCollateral',
                        event_number=instruction_idx,

                        token=info['mint'],
                        amount=int(info['amount']),
                        destination=str(info['account']),

                        account=str(accounts['owner']),
                        signer=str(accounts['lendingMarketAuthority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(mint_collateral)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _withdraw_obligation_collateral_and_redeem_reserve_collateral(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return

        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                # withdraw obligation collateral
                if info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['reserveSourceCollateral']) \
                        and info['destination'] == str(accounts['userDestinationCollateral']):
                    deposit_reserve = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='withdraw_obligation_collateral_and_redeem_reserve_collateral',
                        event_name='transfer-reserveSourceCollateral-userDestinationCollateral',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=str(accounts['owner']),
                        signer=info['authority'],
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(deposit_reserve)
                # redeem collateral
                elif info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['reserveLiquiditySupply']) \
                        and info['destination'] == str(accounts['userDestinationLiquidity']):
                    redeem_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='withdraw_obligation_collateral_and_redeem_reserve_collateral',
                        event_name='transfer-reserveLiquiditySupply-userDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=info['source'],
                        destination=info['destination'],

                        account=str(accounts['owner']),
                        signer=str(accounts['lendingMarketAuthority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(redeem_collateral)
                else:
                    raise UnknownInstruction(i)

            elif i.parsed['type'] == 'burn':
                if info['authority'] == str(accounts['owner']) \
                        and info['account'] == str(accounts['userDestinationCollateral']) \
                        and info['mint'] == str(accounts['reserveCollateralMint']):
                    burn_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='withdraw_obligation_collateral_and_redeem_reserve_collateral',
                        event_name='burn-userDestinationCollateral',
                        event_number=instruction_idx,

                        token=info['mint'],
                        amount=int(info['amount']),
                        source=info['account'],

                        account=str(accounts['owner']),
                        signer=info['authority'],
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(burn_collateral)

                elif info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['account'] == str(accounts['reserveSourceCollateral']) \
                        and info['mint'] == str(accounts['reserveCollateralMint']):
                    burn_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='withdraw_obligation_collateral_and_redeem_reserve_collateral',
                        event_name='burn-reserveSourceCollateral',
                        event_number=instruction_idx,

                        token=info['mint'],
                        amount=int(info['amount']),
                        source=info['account'],

                        account=str(accounts['owner']),
                        signer=info['authority'],
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(burn_collateral)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _liquidate_obligation_and_redeem_reserve_collateral(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        """
        Processes the liquidation of an obligation and redeems reserve collateral according to parsed instructions.

        Args:
            instruction (UiPartiallyDecodedInstruction): The instruction that initiates this action.
            metadata (Any): Metadata associated with the instruction, used to extract necessary account references.
            instruction_idx (int): Index of the instruction in the transaction, used to match with inner instructions.

        This method interprets and acts on the inner instructions involved in a liquidation process, such as burning
        collateral, transferring assets, and managing fees associated with the liquidation events.
        """
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return
        # Extract key accounts involved in the transaction
        liquidatee = str(accounts['obligation'])  # obligation
        liquidator = str(accounts['liquidator'])  # liquidator
        # Process each inner instruction based on its type and relevant account roles
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'burn':
                # burn collateral
                if info['authority'] == liquidator and info['account'] == str(accounts['userDestinationCollateral']):
                    burn_collateral = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='liquidate_obligation_and_redeem_reserve_collateral',
                        event_name='burn-userDestinationCollateral',
                        event_number=instruction_idx,

                        token=info['mint'],
                        amount=int(info['amount']),
                        source=info['account'],

                        account=liquidator,
                        signer=info['authority'],
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(burn_collateral)
                else:
                    raise UnknownInstruction(i)

            elif i.parsed['type'] == 'transfer':

                if info['authority'] == liquidator \
                        and info['source'] == str(accounts['userSourceLiquidity']) \
                        and info['destination'] == str(accounts['repayReserveLiquiditySupply']):
                    repay = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='liquidate_obligation_and_redeem_reserve_collateral',
                        event_name='transfer-userSourceLiquidity-repayReserveLiquiditySupply',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=liquidatee,
                        signer=liquidator,
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(repay)

                elif info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['withdrawReserveCollateralSupply']) \
                        and info['destination'] == str(accounts['userDestinationCollateral']):
                    collateral_withdraw = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='liquidate_obligation_and_redeem_reserve_collateral',
                        event_name='transfer-withdrawReserveCollateralSupply-userDestinationCollateral',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=liquidator,
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(collateral_withdraw)

                # move removed collateral + fee
                elif info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['withdrawReserveLiquiditySupply']) \
                        and info['destination'] == str(accounts['userDestinationLiquidity']):
                    received_collateral_and_fee = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='liquidate_obligation_and_redeem_reserve_collateral',
                        event_name='transfer-withdrawReserveLiquiditySupply-userDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=liquidator,
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(received_collateral_and_fee)
                # move liquidators fee
                elif info['authority'] == liquidator \
                        and info['source'] == str(accounts['userDestinationLiquidity']) \
                        and info['destination'] == str(accounts['withdrawReserveLiquidityFeeReceiver']):
                    move_fee = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='liquidate_obligation_and_redeem_reserve_collateral',
                        event_name='transfer-userDestinationLiquidity-withdrawReserveLiquidityFeeReceiver',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=liquidator,
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket']),
                        obligation=str(accounts['obligation'])
                    )
                    self._processor(move_fee)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _flash_repay_reserve_liquidity(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return

        # Process each inner instruction based on its type and relevant account roles
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                if info['authority'] == str(accounts['userTransferAuthority']) \
                        and info['source'] == str(accounts['userSourceLiquidity']) \
                        and info['destination'] == str(accounts['reserveDestinationLiquidity']):
                    repay_liquidity = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='flash_repay_reserve_liquidity',
                        event_name='transfer-userSourceLiquidity-reserveDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=str(accounts['reserve']),
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket'])
                    )
                    self._processor(repay_liquidity)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _flash_borrow_reserve_liquidity(
            self,
            instruction: UiPartiallyDecodedInstruction,
            metadata: Any,
            instruction_idx: int
    ):
        # Extract relevant account addresses from the instruction using metadata definitions
        accounts = self._get_accounts_from_instruction(instruction.accounts, metadata.idl_ix)
        # Locate inner instructions related to the primary instruction by index
        inner_instructions = next((i for i in self.last_tx.meta.inner_instructions if i.index == instruction_idx), None)
        # failed instructions do not have inner instructions.
        if not inner_instructions:
            return

        # Process each inner instruction based on its type and relevant account roles
        for i in inner_instructions.instructions:
            info = i.parsed['info']
            if i.parsed['type'] == 'transfer':
                if info['authority'] == str(accounts['lendingMarketAuthority']) \
                        and info['source'] == str(accounts['reserveSourceLiquidity']) \
                        and info['destination'] == str(accounts['userDestinationLiquidity']):
                    borrow_liquidity = KaminoParsedTransactions(
                        transaction_id=str(self.last_tx.transaction.signatures[0]),
                        instruction_name='flash_borrow_reserve_liquidity',
                        event_name='transfer-reserveSourceLiquidity-userDestinationLiquidity',
                        event_number=instruction_idx,

                        token=None,
                        amount=int(info['amount']),
                        source=str(info['source']),
                        destination=str(info['destination']),

                        account=str(accounts['reserve']),
                        signer=str(info['authority']),
                        bank=str(accounts['lendingMarket'])
                    )
                    self._processor(borrow_liquidity)
                else:
                    raise UnknownInstruction(i)
            else:
                raise UnknownInstruction(i)

    def _redeem_fees(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _socialize_loss(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _init_referrer_token_state(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _init_user_metadata(self, instruction: UiPartiallyDecodedInstruction,
                            metadata):  # Note: Example method provided earlier
        raise NotImplementedError('Implement me!')

    def _withdraw_referrer_fees(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _withdraw_protocol_fee(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _init_referrer_state_and_short_url(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _delete_referrer_state_and_short_url(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')

    def _update_user_metadata_owner(self, instruction: UiPartiallyDecodedInstruction, metadata):
        raise NotImplementedError('Implement me!')


if __name__ == "__main__":
    from solana.rpc.api import Pubkey, Client

    tx_decoder = KaminoTransactionParser(
        Path('src/protocols/idls/kamino_idl.json'),
        Pubkey.from_string("KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD")
    )

    token = os.getenv("RPC_URL")

    solana_client = Client(
        token)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            # 'ay18WdCWdWRpRfzQ7qmuoJPSQSFb9YfXLrSjJxbjYoU1Gf8Yz5HdTaY6n4U6wkCgrySV8fBw4YMQzyJ7VtCbbZe'
            # "5WRh1c3i77AR1hWckayWvd1uoJhybqmer3srwJeHQbgpJr332X23THwz3ea5TxeedYhkdeh4zUAvCiEP3j43w1Pb",
            # "5CULYy1GS9qV8ioHr6UoQgNTEHZRR8ovD1Dm482GuN84wdv2jVaqGeX4MoFEJjt5BVPVamRpucX8BH3RkeQJxxGU"
            # 'KSyQcxRgE6pcYrGto1sANfRPTrwtJ6m7S8xjrdUG4wwKLXYNnxSfFxy1a3yqxR6aMtr6GAKs41bJRfaHSxQkx7j'
            # "5RDTyfcw1Z5wkwPs7p5atnYbNAjqUqpTfNNdDGFR8xdgHKGtNhe1PctNfTFLUjTspwpiGDJAUgQaQMLJvD4Vv7SP"
            '5hirYUZUd43y4pZkGbMBekPLL4sad6b1f2bnFLak6YkWQq9xtswqAQmHkyH3mxkFp8jCpu28hJgsXTCvZqPFm8t'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.decode_tx(transaction.value.transaction)
