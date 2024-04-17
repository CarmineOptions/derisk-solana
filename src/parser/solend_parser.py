"""
Kamino transaction parser.
"""
import struct
from typing import Any, List, Tuple, Callable, Dict
import logging
import os


import base58
from base58 import b58decode
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from src.parser.solend_config import INSTRUCTION_ACCOUNT_MAP
from db import KaminoParsedTransactions, KaminoLendingAccounts
from src.parser.parser import UnknownInstruction
from src.protocols.addresses import KAMINO_ADDRESS, SOLEND_ADDRESS

LOGGER = logging.getLogger(__name__)


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


def unpack_bytes32(input_bytes):
    if len(input_bytes) < 32:
        raise UnpackError("32 bytes cannot be unpacked: insufficient input length")

    bytes32 = input_bytes[:32]  # Slicing the first 32 bytes
    rest = input_bytes[32:]

    return bytes32, rest


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
        return SolendInstructionData(instruction_id=tag, amount=liquidity_amount, value_name="RefreshReserve")
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
    else:
        raise UnpackError(f"Unsupported tag for unpacking: {tag}")


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
        'deposit_obligation_collateral',
        'deposit_reserve_liquidity_and_obligation_collateral',
        'withdraw_obligation_collateral',
        'borrow_obligation_liquidity',
        'repay_obligation_liquidity',
        'liquidate_obligation',
        'flash_loan'
    ]

    def __init__(
        self,
        program_id: Pubkey = Pubkey.from_string(SOLEND_ADDRESS)
    ):
        print('aaa')
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
            # print(instruction)
            # Check if instruction is partially decoded and belongs to the known program
            if isinstance(instruction, UiPartiallyDecodedInstruction) and instruction.program_id == self.program_id:
                self._process_instruction(instruction)

    def _process_instruction(self, instruction: UiPartiallyDecodedInstruction) -> None:
        # process instruction data
        data = instruction.data
        parsed_data = unpack_data(data)
        # Get instruction name
        instruction_name = {v: k for k, v in self.instruction_types.items()}[parsed_data.instruction_id]
        print(instruction_name)
        if instruction_name not in self.relevant_instructions:
            return
        # get inner instructions
        instruction_index = self.transaction.transaction.message.instructions.index(instruction)  # type: ignore
        # pair present account keys with its names
        account_names = INSTRUCTION_ACCOUNT_MAP[instruction_name]
        instruction_accounts = {str(pubkey): name for pubkey, name in zip(instruction.accounts, account_names)}
        inner_instructions = next((
            i for i in self.transaction.meta.inner_instructions if i.index == instruction_index), None)
        if inner_instructions:
            for inner_instruction in inner_instructions.instructions:
                print(instruction_accounts)
                print(inner_instruction.parsed['info'])
                self._save_inner_instruction(inner_instruction, instruction_accounts, instruction_index)

    def _save_inner_instruction(self, inner_instruction, instruction_accounts, instruction_index):
        if inner_instruction.parsed['type'] == 'transfer':
            transfer = self._parse_transfer_instruction(inner_instruction, instruction_accounts, instruction_index)

            self._processor(transfer)

        if inner_instruction.parsed['type'] == 'mintTo':
            mint_to = self._parse_mintto_instruction(inner_instruction, instruction_accounts, instruction_index)

            self._processor(mint_to)

        if inner_instruction.parsed['type'] == 'burn':
            burn = self._parse_burn_instruction(inner_instruction, instruction_accounts, instruction_index)

            self._processor(burn)

    def _parse_transfer_instruction(self, inner_instruction, accounts: Dict[str, str], instruction_idx: int):
        """"""
        instruction = inner_instruction.parsed

        # Extracting data
        token = str(instruction['info']['token']) if 'token' in instruction['info'] else None
        amount = int(instruction['info']['amount'])

        source = instruction['info']['source']
        source_name = accounts[source]
        destination = instruction['info']['destination']
        destination_name = accounts[destination]

        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{source_name}-{destination_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        # Create the MangoParsedTransactions object
        return KaminoParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
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
            obligation=obligation
        )

    def _parse_mintto_instruction(self, inner_instruction, accounts, instruction_name: str, instruction_idx: int):
        instruction = inner_instruction.parsed
        # Extracting data
        token = str(instruction['info']['mint']) if 'mint' in instruction['info'] else None
        amount = int(instruction['info']['amount'])
        destination = instruction['info']['account']
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
        source_name = accounts, source
        obligation = str(accounts['obligation']) if 'obligation' in accounts else None

        event_name = f"{instruction['type']}-{source_name}"
        event_number = instruction_idx

        account = str(accounts['owner']) if 'owner' in accounts else None
        signer = instruction['info']['authority'] if 'authority' in instruction['info'] else None
        bank = str(accounts['lendingMarket']) if 'lendingMarket' in accounts else None

        # Create the MangoParsedTransactions object
        return KaminoParsedTransactions(
            transaction_id=str(self.transaction.transaction.signatures[0]),
            instruction_name=instruction_name,
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
            '3321qCkErQ2QmXLqf1ZLHzW4JxXVLoWLvV3ytDkHUfAhKK18uk8Xr6atYLw6uFUZHvHiL5xkEFY6P8BkAUHZt4sF'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.parse_transaction(transaction.value.transaction)
