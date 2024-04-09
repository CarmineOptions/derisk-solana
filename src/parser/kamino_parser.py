"""
"""
import os
from pathlib import Path
import math

from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta, UiPartiallyDecodedInstruction

from src.parser.parser import TransactionDecoder
from db import KaminoParsedTransactions, KaminoLendingAccounts, get_db_session


class KaminoTransactionParser(TransactionDecoder):
    def decode_tx(self, transaction_with_meta: EncodedTransactionWithStatusMeta):
        self.last_tx = transaction_with_meta
        self.instructions = [
            i for i in transaction.value.transaction.transaction.message.instructions
            if str(i.program_id) == str(self.program_id)
        ]

        log_msgs = transaction_with_meta.meta.log_messages
        kamino_program_invoked = False

        instruction_counter = 0
        for msg in log_msgs:
            if msg.startswith(f"Program {str(self.program_id)} invoke"):
                kamino_program_invoked = True

            if kamino_program_invoked and msg.startswith("Program log: Instruction:"):  # InitUserMetadata
                instruction_name = msg.split(' ')[3]
                instruction_name = instruction_name[0].lower() + instruction_name[1:]
                if instruction_name in [i.idl_ix.name for i in self.program.instruction.values()]:
                    instruction = self.instructions[instruction_counter]
                    instruction_counter += 1
                    self.save_kamino_event(instruction, instruction_name)

        assert instruction_counter == len(self.instructions)

    def save_kamino_event(self, instruction: UiPartiallyDecodedInstruction, instruction_name: str) -> None:
        """
        """
        if instruction_name == 'initUserMetadata':
            self._create_lending_account(instruction, instruction_name)

    def _create_lending_account(self, instruction: UiPartiallyDecodedInstruction):
        """"""
        new_lending_account = KaminoLendingAccounts()
        self._processor(new_lending_account)



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
            'ay18WdCWdWRpRfzQ7qmuoJPSQSFb9YfXLrSjJxbjYoU1Gf8Yz5HdTaY6n4U6wkCgrySV8fBw4YMQzyJ7VtCbbZe'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.decode_tx(transaction.value.transaction)
