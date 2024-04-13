"""
Module contains transaction parser for Marginfi lending protocol.
"""
from pathlib import Path
import math
import os
import logging

from anchorpy.program.common import Event
from construct.core import StreamError
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta

from db import MarginfiParsedTransactions, MarginfiLendingAccounts
from src.parser.parser import TransactionDecoder
from src.protocols.addresses import MARGINFI_ADDRESS
from src.protocols.idl_paths import MARGINFI_IDL_PATH


LOGGER = logging.getLogger(__name__)


class MarginfiTransactionParser(TransactionDecoder):

    def __init__(
            self,
            path_to_idl: Path = Path(MARGINFI_IDL_PATH),
            program_id: Pubkey = Pubkey.from_string(MARGINFI_ADDRESS)
    ):
        super().__init__(path_to_idl, program_id)

    def _create_lending_account(self, event: Event):
        """"""
        new_lending_account = MarginfiLendingAccounts(
            authority=str(event.data.header.signer),
            address=str(event.data.header.marginfi_account),
            group=str(event.data.header.marginfi_group)
        )
        self._processor(new_lending_account)

    def _change_account_authority(self, event: Event):
        """"""
        new_lending_account = MarginfiLendingAccounts(
            authority=str(event.data.new_account_authority),
            address=str(event.data.header.marginfi_account),
            group=str(event.data.header.marginfi_group)
        )
        self._processor(new_lending_account)

    def _record_deposit(self, event: Event):
        """

        :param event:
        :return:
        """
        mint = event.data.mint
        amount = event.data.amount

        # check deposit balances
        depositor = event.data.header.signer

        deposit = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_deposit',
            event_name= event.name,

            position='asset',
            token=str(mint),
            amount=amount,
            amount_decimal=None,

            account=str(event.data.header.marginfi_account),
            signer=str(depositor)
        )

        self._processor(deposit)

    def _record_repay(self, event: Event):
        """

        :param event:
        :return:
        """
        mint = event.data.mint
        amount = event.data.amount

        # get token decimals from token post balances
        signer = event.data.header.signer
        post_token_balance = next((
            b for b in self.last_tx.meta.post_token_balances
            if b.mint == mint
        ), None)
        amount_decimal = post_token_balance.ui_token_amount.decimals if post_token_balance else None
        payment = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_repay',
            event_name=event.name,

            position='liability',
            token=str(mint),
            amount=-amount,
            amount_decimal=amount_decimal,

            account=str(event.data.header.marginfi_account),
            signer=str(signer)
        )

        self._processor(payment)

    def _record_borrow(self, event: Event):
        """

        :param event:
        :return:
        """
        mint = event.data.mint
        amount = event.data.amount

        # check deposit balances
        borrower = event.data.header.signer
        # attempt to obtain decimal for mint amount
        post_token_balance = next((
            b for b in self.last_tx.meta.post_token_balances
            if b.owner == borrower and b.mint == mint
        ), None)
        amount_decimal = post_token_balance.ui_token_amount.decimals if post_token_balance else None

        loan = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_borrow',
            event_name=event.name,

            position='liability',
            token=str(mint),
            amount=amount,
            amount_decimal=amount_decimal,
            account=str(event.data.header.marginfi_account),
            signer=str(borrower)
        )

        self._processor(loan)

    def _record_withdraw(self, event: Event):
        """

        :param event:
        :return:
        """
        mint = event.data.mint
        amount = event.data.amount
        signer = event.data.header.signer

        # get token balance for relevant token to obtain number of decimals
        post_token_balance = next((
            b for b in self.last_tx.meta.post_token_balances
            if b.mint == mint
        ), None)

        amount_decimal = post_token_balance.ui_token_amount.decimals if post_token_balance else None
        withdrawal = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_withdraw',
            event_name=event.name,

            position='asset',
            token=str(mint),
            amount=-amount,
            amount_decimal=amount_decimal,
            account=str(event.data.header.marginfi_account),
            signer=str(signer)
        )
        self._processor(withdrawal)

    def _record_liquidation(self, event: Event):
        """

        :param event:
        :return:
        """
        asset_token = event.data.asset_mint
        liability_token = event.data.liability_mint

        liquidatee_removed_assets = event.data.post_balances.liquidatee_asset_balance - \
                                    event.data.pre_balances.liquidatee_asset_balance

        liquidator_received_assets = event.data.post_balances.liquidator_asset_balance - \
                                    event.data.pre_balances.liquidator_asset_balance

        liquidatee_removed_liability = event.data.post_balances.liquidatee_liability_balance - \
                                    event.data.pre_balances.liquidatee_liability_balance

        liquidator_received_liability = event.data.post_balances.liquidator_liability_balance - \
                                     event.data.pre_balances.liquidator_liability_balance

        post_token_balance = next((b for b in self.last_tx.meta.post_token_balances if b.mint == liability_token), None)
        amount_decimal_asset_token = post_token_balance.ui_token_amount.decimals if post_token_balance else None
        amount_decimal_liability_token = post_token_balance.ui_token_amount.decimals if post_token_balance else None

        # Assets
        liquidator_received_assets_record = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_liquidate',
            event_name=event.name,
            position='asset',
            token=str(asset_token),
            amount=math.ceil(liquidator_received_assets),
            amount_decimal=amount_decimal_asset_token,

            account=str(event.data.header.marginfi_account),
            signer=str(event.data.header.signer)
        )

        liquidatee_removed_assets_record = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_liquidate',
            event_name=event.name,
            position='asset',
            token=str(asset_token),
            amount=math.ceil(liquidatee_removed_assets),
            amount_decimal=amount_decimal_asset_token,

            account=str(event.data.liquidatee_marginfi_account),
            signer=str(event.data.liquidatee_marginfi_account_authority)
        )

        # Liability
        liquidator_received_liability_record = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_liquidate',
            event_name=event.name,
            position='liability',
            token=str(liability_token),
            amount=math.ceil(liquidator_received_liability),
            amount_decimal=amount_decimal_liability_token,

            account=str(event.data.header.marginfi_account),
            signer=str(event.data.header.signer)
        )

        liquidatee_removed_liability_record = MarginfiParsedTransactions(
            transaction_id=str(self.last_tx.transaction.signatures[0]),
            instruction_name='lending_account_liquidate',
            event_name=event.name,
            position='liability',
            token=str(liability_token),
            amount=math.ceil(liquidatee_removed_liability),
            amount_decimal=amount_decimal_liability_token,

            account=str(event.data.liquidatee_marginfi_account),
            signer=str(event.data.liquidatee_marginfi_account_authority)
        )

        self._processor(liquidator_received_assets_record)
        self._processor(liquidatee_removed_assets_record)
        self._processor(liquidator_received_liability_record)
        self._processor(liquidatee_removed_liability_record)

    def save_event(self, event: Event) -> None:
        """
        Save event based on its name.
        """
        if event.name == "MarginfiAccountCreateEvent":
            self._create_lending_account(event)

        if event.name == "LendingAccountDepositEvent":
            self._record_deposit(event)

        if event.name == "LendingAccountRepayEvent":
            self._record_repay(event)

        if event.name == "LendingAccountBorrowEvent":
            self._record_borrow(event)

        if event.name == "LendingAccountWithdrawEvent":
            self._record_withdraw(event)

        if event.name == "LendingAccountLiquidateEvent":
            self._record_liquidation(event)

        if event.name == "MarginfiAccountTransferAccountAuthorityEvent":
            self._change_account_authority(event)

    def parse_transaction(self, transaction_with_meta: EncodedTransactionWithStatusMeta):
        """
        Parse marginfi transaction instructions and correlates with log messages.

        Args:
            transaction_with_meta (EncodedTransactionWithStatusMeta): The transaction data with metadata.

        This method processes a given transaction, attempting to parse its instructions if they
        are encoded and match a known program ID. It also associates these instructions with
        corresponding log messages, and handles specific events accordingly.
        """
        self.last_tx = transaction_with_meta
        log_msgs = transaction_with_meta.meta.log_messages

        try:
            self.event_parser.parse_logs(
                log_msgs, self.save_event
            )
        except StreamError:
            LOGGER.warning(f"Stream error at transaction = `{self.last_tx.transaction.signatures[0]}`")


if __name__ == "__main__":
    from solana.rpc.api import Client

    tx_decoder = MarginfiTransactionParser()

    rpc_url = os.getenv("RPC_URL")
    solana_client = Client(rpc_url)  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '64dt9xEoEkrS5ML3Bo5xhpLpJLz7L1BoDJPwTK5XFwbzswtYusiTSgHv1d2rH2o8ao2UzJgVpjgxTHhTuV834iB'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )
    tx_decoder.parse_transaction(transaction.value.transaction)
