"""
"""
import os
from pathlib import Path
import math

from anchorpy.program.common import Event
from solders.signature import Signature
from solders.transaction_status import EncodedTransactionWithStatusMeta
from construct.core import StreamError

from src.parser.parser import TransactionDecoder
from db import MarginfiParsedTransactions, MarginfiLendingAccounts


class MarginfiTransactionParser(TransactionDecoder):

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
        amount_decimal = post_token_balance.ui_token_amount.decimals
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
        pre_token_balance = next((
            b for b in self.last_tx.meta.pre_token_balances
            if b.owner == borrower and b.mint == mint
        ), None)
        post_token_balance = next((
            b for b in self.last_tx.meta.post_token_balances
            if b.owner == borrower and b.mint == mint
        ), None)
        pre_token_balance_amount = int(pre_token_balance.ui_token_amount.amount if pre_token_balance else "0")
        post_token_balance_amount = int(post_token_balance.ui_token_amount.amount)
        # assert post_token_balance_amount - pre_token_balance_amount == amount

        amount_decimal = post_token_balance.ui_token_amount.decimals

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

        amount_decimal = post_token_balance.ui_token_amount.decimals
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


    def decode_tx(self, transaction_with_meta: EncodedTransactionWithStatusMeta):
        self.last_tx = transaction_with_meta
        log_msgs = transaction_with_meta.meta.log_messages

        try:
            self.event_parser.parse_logs(
                log_msgs, lambda x: self.save_event(x)
            )
        except StreamError:
            print('bananan')


if __name__ == "__main__":
    from solana.rpc.api import Pubkey, Client

    tx_decoder = MarginfiTransactionParser(
        Path('src/protocols/idls/marginfi_idl.json'),
        Pubkey.from_string("MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA")
    )

    token = os.getenv("RPC_URL")

    ppk = "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA"

    solana_client = Client(
        "https://docs-demo.solana-mainnet.quiknode.pro/")  # RPC url - now it's just some demo i found on internet

    transaction = solana_client.get_transaction(
        Signature.from_string(
            '64dt9xEoEkrS5ML3Bo5xhpLpJLz7L1BoDJPwTK5XFwbzswtYusiTSgHv1d2rH2o8ao2UzJgVpjgxTHhTuV834iB'
        ),
        'jsonParsed',
        max_supported_transaction_version=0
    )

    tx_decoder.decode_tx(transaction.value.transaction)
