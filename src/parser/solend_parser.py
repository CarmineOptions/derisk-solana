"""
Solend transaction parser.
"""
from typing import Callable, Dict
import struct
import logging
import os

import base58
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from db import SolendParsedTransactions, SolendObligations, SolendReserves
from src.parser.solend_config import INSTRUCTION_ACCOUNT_MAP
from src.parser.parser import UnknownInstruction
from src.protocols.addresses import SOLEND_ADDRESS

LOGGER = logging.getLogger(__name__)


def snake_to_camel(snake_str):
    # Split the string into words based on underscores
    components = snake_str.split('_')
    # Capitalize the first letter of each component except the first one
    # and join them back into a single string
    return components[0] + ''.join(x.title() for x in components[1:])


class UnpackError(Exception):
    pass


class SolendInstructionData:
    def __init__(self, instruction_id: int, amount: int | None = None, value_name= str | None):
        self.instruction_id = instruction_id
        self.amount = amount
        self.value_name = value_name

    def __repr__(self):
        return (f"SolendInstructionData(instruction_id={self.instruction_id}, amount={self.amount}, "
                f"value_name={self.value_name})")


def unpack_u64(input_bytes):
    if len(input_bytes) < 8:
        raise UnpackError("u64 cannot be unpacked: insufficient input length")

    value = struct.unpack_from('<Q', input_bytes)[0]  # '<Q' specifies little-endian unsigned long long
    rest = input_bytes[8:]

    return value, rest


def unpack_u8(input_bytes):
    if not input_bytes:
        raise UnpackError("u8 cannot be unpacked: no input")

    value = struct.unpack_from('B', input_bytes)[0]  # 'B' specifies an unsigned char
    rest = input_bytes[1:]

    return value, rest



def unpack_pubkey(input_bytes, pubkey_bytes: int = 8):
    if len(input_bytes) < pubkey_bytes:
        raise UnpackError("Pubkey cannot be unpacked: insufficient input length")

    pubkey = input_bytes[:pubkey_bytes]  # Assuming `pubkey_bytes` is the length of a public key
    rest = input_bytes[pubkey_bytes:]

    return pubkey, rest


def unpack_data(data: str):
    """
    Unpack instruction data
    """
    # get bytes
    input_bytes = base58.b58decode(data)
    # split into tag (instruction type identifier) and content
    tag, rest = input_bytes[0], input_bytes[1:]
    # Return instruction with type
    if tag == 0:
        owner, rest = unpack_pubkey(rest)
        return SolendInstructionData(instruction_id=tag, amount=owner, value_name="InitLendingMarket")
    elif tag == 1:
        new_owner, rest = unpack_pubkey(rest)
        return SolendInstructionData(instruction_id=tag, amount=new_owner, value_name="SetLendingMarketOwner")
    elif tag == 2:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="InitReserve")
    elif tag == 3:
        return SolendInstructionData(instruction_id=tag, value_name="RefreshReserve")
    elif tag == 4:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="DepositReserveLiquidity")
    elif tag == 5:
        collateral_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=collateral_amount, value_name="RedeemReserveCollateral")

    elif tag == 6:
        return SolendInstructionData(instruction_id=tag, value_name="InitObligation")
    elif tag == 7:
        return SolendInstructionData(instruction_id=tag, value_name="RefreshObligation")
    elif tag == 8:
        collateral_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag,
                                     amount=collateral_amount, value_name="DepositObligationCollateral")
    elif tag == 9:
        collateral_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag,
                                     amount=collateral_amount, value_name="WithdrawObligationCollateral")
    elif tag == 10:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="BorrowObligationLiquidity")
    elif tag == 11:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="RepayObligationLiquidity")
    elif tag == 12:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="LiquidateObligation")
    elif tag == 13:
        amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag, amount=amount, value_name="FlashLoan")
    elif tag == 14:
        liquidity_amount, rest = unpack_u64(rest)
        return SolendInstructionData(instruction_id=tag,
                                     amount=liquidity_amount,
                                     value_name="DepositReserveLiquidityAndObligationCollateral")
    elif tag == 15:
        collateral_amount, rest = unpack_u64(rest)
        return SolendInstructionData(
            instruction_id=tag,
            amount=collateral_amount,
            value_name="WithdrawObligationCollateralAndRedeemReserveCollateral"
        )
    return



class SolendTransactionParser:
    instruction_types = {
        "init_lending_market": 0,
        "set_lending_market_owner_and_config": 1,
        "init_reserve": 2,
        "refresh_reserve": 3,
        "deposit_reserve_liquidity": 4,
        "redeem_reserve_collateral": 5,
        "init_obligation": 6,
        "refresh_obligation": 7,
        "deposit_obligation_collateral": 8,
        "withdraw_obligation_collateral": 9,
        "borrow_obligation_liquidity": 10,
        "repay_obligation_liquidity": 11,
        "liquidate_obligation": 12,
        "flash_loan": 13,
        "deposit_reserve_liquidity_and_obligation_collateral": 14,
        "withdraw_obligation_collateral_and_redeem_reserve_liquidity": 15,
        "update_reserve_config": 16,
        "flash_borrow_reserve_liquidity": 19,
        "flash_repay_reserve_liquidity": 20,
        "forgive_debt": 21,
        "update_metadata": 22,
    }
    relevant_instructions = [
        'deposit_reserve_liquidity',
        'redeem_reserve_collateral',
        'init_obligation',
        'init_reserve',
        'deposit_obligation_collateral',
        'deposit_reserve_liquidity_and_obligation_collateral',
        'withdraw_obligation_collateral_and_redeem_reserve_liquidity',
        'withdraw_obligation_collateral',
        'borrow_obligation_liquidity',
        'repay_obligation_liquidity',
        'liquidate_obligation',
        'liquidate_obligation_and_redeem_reserve_collateral',
        'redeem_fees',
        'flash_borrow_reserve_liquidity',
        'flash_repay_reserve_liquidity',
        'forgive_debt',
        # 'flash_loan'
    ]

    def __init__(
        self,
        program_id: Pubkey = Pubkey.from_string(SOLEND_ADDRESS)
    ):
        self.program_id = program_id
        self.transaction: EncodedTransactionWithStatusMeta | None = None
        self._processor: Callable = self.print_event_to_console

    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta) -> None:
        """
        Decodes transaction instructions

        Args:
            transaction_with_meta (EncodedTransactionWithStatusMeta): The transaction data with metadata.

        """
        # Storing the transaction for later use
        self.transaction = transaction_with_meta
        if not self.transaction.meta:
            return

        if self.transaction.meta.err:
            return
        # Parse instructions:
        for instruction in self.transaction.transaction.message.instructions:
            # Check if instruction is partially decoded and belongs to the known program
            if isinstance(instruction, UiPartiallyDecodedInstruction) and instruction.program_id == self.program_id:
                self._process_instruction(instruction)

        # parse inner instructions:
        for instruction in self.transaction.meta.inner_instructions:
            for idx, inner_instruction in enumerate(instruction.instructions):
                if isinstance(inner_instruction,
                              UiPartiallyDecodedInstruction) and inner_instruction.program_id == self.program_id:
                    self._process_instruction(inner_instruction)

    def _process_instruction(self, instruction: UiPartiallyDecodedInstruction) -> None:
        # process instruction data
        data = instruction.data
        parsed_data = unpack_data(data)
        if parsed_data.instruction_id == 12:
            print(parsed_data.instruction_id, self.transaction.meta.err)
            print(str(self.transaction.transaction.signatures[0]))
        if not parsed_data:
            return
        # Get instruction name
        # instruction_name = {v: k for k, v in self.instruction_types.items()}[parsed_data.instruction_id]
        #
        # if instruction_name not in self.relevant_instructions:
        #     return
        # # get inner instructions
        # instruction_index = self.transaction.transaction.message.instructions.index(instruction)  # type: ignore
        # # pair present account keys with its names
        # account_names = INSTRUCTION_ACCOUNT_MAP[instruction_name]
        #
        # instruction_accounts = dict()
        # for pubkey, name in zip(instruction.accounts, account_names):
        #     if str(pubkey) not in instruction_accounts:
        #         instruction_accounts[str(pubkey)] = name
        # # parse `init_obligation` event
        # if instruction_name == 'init_obligation':
        #     self._init_obligation(instruction_accounts)
        #     return
        # if instruction_name == 'init_reserve':
        #     self._init_reserve(instruction_accounts)
        #     return
        # inner_instructions = next((
        #     i for i in self.transaction.meta.inner_instructions if i.index == instruction_index), None)
        # if inner_instructions:
        #     for inner_instruction in inner_instructions.instructions:
        #         self._save_inner_instruction(
        #             inner_instruction,
        #             instruction_accounts,
        #             instruction_name,
        #             instruction_index
        #         )

    def _save_inner_instruction(
            self,
            inner_instruction,
            instruction_accounts,
            instruction_name: str,
            instruction_index: int
    ):
        if inner_instruction.parsed['type'] == 'transfer':
            transfer = self._parse_transfer_instruction(
                inner_instruction, instruction_accounts, instruction_name, instruction_index)

            self._processor(transfer)

        elif inner_instruction.parsed['type'] == 'mintTo':
            mint_to = self._parse_mintto_instruction(
                inner_instruction, instruction_accounts, instruction_name, instruction_index)

            self._processor(mint_to)

        elif inner_instruction.parsed['type'] == 'burn':
            burn = self._parse_burn_instruction(
                inner_instruction, instruction_accounts, instruction_name, instruction_index)

            self._processor(burn)
        else:
            raise UnknownInstruction(inner_instruction)

    def _parse_transfer_instruction(self, inner_instruction, accounts: Dict[str, str], instruction_name: str, instruction_idx: int):
        """"""
        instruction = inner_instruction.parsed

        # Extracting data
        token = str(instruction['info']['token']) if 'token' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['source']
        source_name = accounts[source]
        destination = instruction['info']['destination']
        destination_name = accounts[destination]

        obligation = next((k for k, v in accounts.items() if v == 'obligation_pubkey'), None)

        event_name = f"{instruction['type']}-{snake_to_camel(source_name)}-{snake_to_camel(destination_name)}"
        event_number = instruction_idx

        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = next((k for k, v in accounts.items() if v == 'lending_market_pubkey'), None)
        authority = next((k for k, v in accounts.items() if v == 'user_transfer_authority_pubkey'), None)

        # Create the MangoParsedTransactions object
        return SolendParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=instruction_name,
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            source=source,
            destination=destination,
            signer=signer,
            bank=bank,
            obligation=obligation,
            authority=authority
        )

    def _parse_mintto_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        """"""
        instruction = inner_instruction.parsed

        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        destination = instruction['info']['account']
        destination_name = accounts[destination]
        obligation = next((k for k, v in accounts.items() if v == 'obligation_pubkey'), None)

        event_name = f"{instruction['type']}-{snake_to_camel(destination_name)}"
        event_number = instruction_idx

        signer = instruction['info']['mintAuthority'] if 'mintAuthority' in instruction['info'] else None
        bank = next((k for k, v in accounts.items() if v == 'lending_market_pubkey'), None)
        authority = next((k for k, v in accounts.items() if v == 'user_transfer_authority_pubkey'), None)

        return SolendParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=instruction_name,
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            destination=destination,
            signer=signer,
            bank=bank,
            obligation=obligation,
            authority=authority
        )

    def _parse_burn_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        """"""
        instruction = inner_instruction.parsed
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        source = instruction['info']['account']
        source_name = accounts[source]

        obligation = next((k for k, v in accounts.items() if v == 'obligation_pubkey'), None)

        event_name = f"{instruction['type']}-{snake_to_camel(source_name)}"
        event_number = instruction_idx

        signer = instruction['info']['mintAuthority'] if 'mintAuthority' in instruction['info'] else None
        bank = next((k for k, v in accounts.items() if v == 'lending_market_pubkey'), None)
        authority = next((k for k, v in accounts.items() if v == 'user_transfer_authority_pubkey'), None)

        # Create the MangoParsedTransactions object
        return SolendParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=instruction_name,
            event_name=event_name,
            event_number=event_number,
            token=token,
            amount=amount,
            signer=signer,
            bank=bank,
            obligation=obligation,
            authority=authority
        )

    def _init_reserve(self, accounts: Dict[str, str]):
        """"""
        # Extract relevant keys from the accounts dictionary
        source_liquidity_pubkey = next((k for k, v in accounts.items() if v == 'source_liquidity_pubkey'), None)
        destination_collateral_pubkey = next((
            k for k, v in accounts.items() if v == 'destination_collateral_pubkey'), None)
        reserve_pubkey = next((k for k, v in accounts.items() if v == 'reserve_pubkey'), None)
        reserve_liquidity_mint_pubkey = next((
            k for k, v in accounts.items() if v == 'reserve_liquidity_mint_pubkey'), None)
        reserve_liquidity_supply_pubkey = next((
            k for k, v in accounts.items() if v == 'reserve_liquidity_supply_pubkey'), None)
        config_fee_receiver = next((k for k, v in accounts.items() if v == 'config.fee_receiver'), None)
        reserve_collateral_mint_pubkey = next((
            k for k, v in accounts.items() if v == 'reserve_collateral_mint_pubkey'), None)
        reserve_collateral_supply_pubkey = next((
            k for k, v in accounts.items() if v == 'reserve_collateral_supply_pubkey'), None)
        pyth_product_pubkey = next((k for k, v in accounts.items() if v == 'pyth_product_pubkey'), None)
        pyth_price_pubkey = next((k for k, v in accounts.items() if v == 'pyth_price_pubkey'), None)
        switchboard_feed_pubkey = next((k for k, v in accounts.items() if v == 'switchboard_feed_pubkey'), None)
        lending_market_pubkey = next((k for k, v in accounts.items() if v == 'lending_market_pubkey'), None)
        lending_market_authority_pubkey = next((
            k for k, v in accounts.items() if v == 'lending_market_authority_pubkey'), None)
        lending_market_owner_pubkey = next((
            k for k, v in accounts.items() if v == 'lending_market_owner_pubkey'), None)
        user_transfer_authority_pubkey = next((
            k for k, v in accounts.items() if v == 'user_transfer_authority_pubkey'), None)

        # Create new reserve instance
        new_reserve = SolendReserves(
            source_liquidity_pubkey=source_liquidity_pubkey,
            destination_collateral_pubkey=destination_collateral_pubkey,
            reserve_pubkey=reserve_pubkey,
            reserve_liquidity_mint_pubkey=reserve_liquidity_mint_pubkey,
            reserve_liquidity_supply_pubkey=reserve_liquidity_supply_pubkey,
            config_fee_receiver=config_fee_receiver,
            reserve_collateral_mint_pubkey=reserve_collateral_mint_pubkey,
            reserve_collateral_supply_pubkey=reserve_collateral_supply_pubkey,
            pyth_product_pubkey=pyth_product_pubkey,
            pyth_price_pubkey=pyth_price_pubkey,
            switchboard_feed_pubkey=switchboard_feed_pubkey,
            lending_market_pubkey=lending_market_pubkey,
            lending_market_authority_pubkey=lending_market_authority_pubkey,
            lending_market_owner_pubkey=lending_market_owner_pubkey,
            user_transfer_authority_pubkey=user_transfer_authority_pubkey
        )

        # Assuming a method _processor to handle the new Reserve
        self._processor(new_reserve)

    def _init_obligation(
            self,
            accounts: Dict[str, str]
    ):
        # create obligation
        obligation = next((k for k, v in accounts.items() if v == 'obligation_pubkey'), None)
        lending_market = next((k for k, v in accounts.items() if v == 'lending_market_pubkey'), None)
        authority = next((k for k, v in accounts.items() if v == 'obligation_owner_pubkey'), None)

        new_obligation = SolendObligations(
            authority=authority,
            address=obligation,
            group=lending_market
        )
        self._processor(new_obligation)

    def print_event_to_console(self, event_record):
        """
        Print event to console.
        """
        print(event_record)

    def save_event_to_database(
            self,
            event_record,
            timestamp: int,
            block_number: int,
            session
    ):
        """
        Assign timestamp and block number to event. Add record to db session.
        """
        event_record.created_at = timestamp
        event_record.block = block_number
        session.add(event_record)


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = SolendTransactionParser()

    rpc_url = os.getenv("RPC_URL")

    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '5dDKbA4DHkVmigpQGerwpgbFJDEaTMfyo4jkJf9NjBLNRGkznxeTyQsHZSpsLSmcZ4PsnqMpr4Uvfa2yALLKrqQq'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
