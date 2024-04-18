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
        table='lenders.marginfi_parsed_transactions_v3',
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
            table='lenders.marginfi_parsed_transactions_v3',
            event_names=tuple(EVENTS_METHODS_MAPPING),
            event_column='instruction_name',
            start_block_number=self.last_slot + 1,
        )

    def process_event(self, event: pandas.DataFrame) -> None:
        min_slot = event["block"].min()
        assert min_slot >= self.last_slot
        event_name = event["instruction_name"].iloc[0]
        assert event["instruction_name"].nunique() == 1  # TODO: redundant?
        try:  # TODO
            getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        except:
            logging.error(f'{event_name} {event}')  # TODO
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
        # assert len(transfer_event) <= 1  # TODO
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
        # assert len(transfer_event) <= 1  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["account"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} repayed amount = {} of token = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-bankLiquidityVault-bankInsuranceVault']
        assert len(transfer_event) <= 1  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["liquidatee_marginfi_account"]
            assert user in self.loan_entities  # TODO
            # TODO: The very first liquidation events do not change the collateral.
            collateral_token = None
            collateral_amount = decimal.Decimal('0')
            assert collateral_amount >= 0
            debt_token = individual_transfer_event["source"]
            debt_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert debt_amount >= 0
            self.loan_entities[user].debt.increase_value(token=debt_token, value=-debt_amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, debt of raw amount = {} of token = {} and collateral of raw amount = {} of "
                    "token = {} of user = {} were liquidated.".format(
                        event["block"].iloc[0],
                        debt_amount,
                        debt_token,
                        collateral_amount,
                        collateral_token,
                        user,
                    )
                )
