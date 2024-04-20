import decimal
import logging

import pandas

import src.loans.helpers
import src.loans.types
import src.loans.state



# Keys are values of the "event_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
    'lending_account_borrow': 'process_borrowing_event',
    'lending_account_deposit': 'process_deposit_event',
    'lending_account_liquidate': 'process_liquidation_event',
    'lending_account_repay': 'process_repayment_event',
    'lending_account_withdraw': 'process_withdrawal_event',
}


def get_events(start_block_number: int = 0) -> pandas.DataFrame:
    return src.loans.helpers.get_events(
        table='lenders.marginfi_parsed_transactions_v5',
        event_names=tuple(EVENTS_METHODS_MAPPING),
        start_block_number=start_block_number,
    )


class MarginFiLoanEntity(src.loans.state.LoanEntity):
    """ A class that describes the MarginFi loan entity. """

    def __init__(self) -> None:
        super().__init__()


class MarginFiState(src.loans.state.State):
    """
    A class that describes the state of all MarginFi loan entities. It implements methods for correct processing of
    every relevant event.
    """

    EVENTS_METHODS_MAPPING: dict[str, str] = EVENTS_METHODS_MAPPING

    def __init__(
        self,
        verbose_users: set[str] | None = None,
        initial_loan_states: pandas.DataFrame = pandas.DataFrame(),
    ) -> None:
        super().__init__(
            protocol='MarginFi',
            loan_entity_class=MarginFiLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    def get_unprocessed_events(self) -> None:
        self.unprocessed_events = src.loans.helpers.get_events(
            table='lenders.marginfi_parsed_transactions_v5',
            event_names=tuple(EVENTS_METHODS_MAPPING),
            event_column='instruction_name',
            start_block_number=self.last_slot + 1,
        )

    def process_event(self, event: pandas.DataFrame) -> None:
        min_slot = event["block"].min()
        assert min_slot >= self.last_slot
        event_name = event["instruction_name"].iloc[0]
        getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        self.last_slot = min_slot

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-signerTokenAccount-bankLiquidityVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} deposited amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_withdrawal_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-destinationTokenAccount']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} withdrew amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_borrowing_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-destinationTokenAccount']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} borrowed amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-signerTokenAccount-bankLiquidityVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} repaid amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        # Under MarginFi, each liquidation event consists of a collateral transfer event, debt transfer event and fee
        # transfer event. The collateral transfer under the liquidation is handled as a separate withdrawal event, the
        # debt transfer event is handled as a separate repayment event and only the fee transfer event is handled here.
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-bankInsuranceVault']
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["liquidatee_marginfi_account"]
            assert user in self.loan_entities
            debt_token = individual_transfer_event["source"]
            debt_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert debt_amount >= 0
            self.loan_entities[user].debt.increase_value(token=debt_token, value=-debt_amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} paid liquidation fee amount = {} of token = {}.".format(
                        event["block"].iloc[0],
                        user,
                        debt_amount,
                        debt_token,
                    )
                )
