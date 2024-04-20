import decimal
import logging

import pandas

import src.loans.helpers
import src.loans.types
import src.loans.state


# Keys are values of the "event_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
    # 'lending_account_borrow': 'process_borrowing_event',
    # 'lending_account_deposit': 'process_deposit_event',
    # 'lending_account_liquidate': 'process_liquidation_event',
    # 'lending_account_repay': 'process_repayment_event',
    # 'lending_account_withdraw': 'process_withdrawal_event',
    'borrow_obligation_liquidity': 'process_borrowing_event',
    'deposit_obligation_collateral': 'process_deposit_event',
    # 'deposit_reserve_liquidity': 'process_deposit_event',  # do not affect collateral or debt
    'deposit_reserve_liquidity_and_obligation_collateral': 'process_deposit_event',
    'liquidate_obligation': 'process_liquidation_event',
    'liquidate_obligation_and_redeem_reserve_collateral': 'process_liquidation_event',
    # 'redeem_reserve_collateral': 'process_withdrawal_event',  # do not affect collateral or debt
    'repay_obligation_liquidity': 'process_repayment_event',
    'withdraw_obligation_collateral': 'process_withdrawal_event',
    'withdraw_obligation_collateral_and_redeem_reserve_liquidity': 'process_withdrawal_event',
    # 'flash_borrow_reserve_liquidity': '',
    # 'flash_repay_reserve_liquidity': '',
}


def get_events(start_block_number: int = 0) -> pandas.DataFrame:
    return src.loans.helpers.get_events(
        table='lenders.solend_parsed_transactions_v2',
        event_names=tuple(EVENTS_METHODS_MAPPING),
        start_block_number=start_block_number,
        event_column='instruction_name'
    )


class SolendLoanEntity(src.loans.state.LoanEntity):
    """ A class that describes the Solend loan entity. """

    def __init__(self) -> None:
        super().__init__()


class SolendState(src.loans.state.State):
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
        self.where = 0
        super().__init__(
            protocol='Solend',
            loan_entity_class=SolendLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    def get_unprocessed_events(self) -> None:
        self.unprocessed_events = src.loans.helpers.get_events(
            table='lenders.solend_parsed_transactions_v2',
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

        if self.last_slot > self.where * 1000000:
            self.where = (self.last_slot - self.last_slot % 1000000) / 1000000 + 1
            logging.info("Processing {} slot.".format(self.last_slot))

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-userCollateralPubkey-destinationDepositCollateralPubkey']
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
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
        transfer_event = event[
            event['event_name'] == 'transfer-sourceCollateralPubkey-destinationCollateralPubkey'
        ]
        assert len(transfer_event) > 0  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
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
        transfer_event = event[event['event_name'].str.startswith('transfer-sourceLiquidityPubkey-')]
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["source"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} borrow / paid fee = {} of token = {}. \n current debt = {}".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                        self.loan_entities[user].debt[token]
                    )
                )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-sourceLiquidityPubkey-destinationLiquidityPubkey']
        assert len(transfer_event) > 0  # TODO
        # return
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            token = individual_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            paid_interest = 0
            
            if self.loan_entities[user].debt[token] < 0:
                paid_interest = -self.loan_entities[user].debt[token]
                amount = amount - paid_interest
                self.loan_entities[user].debt[token] += paid_interest
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} repayed amount = {} of token = {}, \n paid interest = {} \n current debt = {}.".format(
                        individual_transfer_event["block"],
                        user,
                        amount,
                        token,
                        paid_interest,
                        self.loan_entities[user].debt[token]
                    )
                )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        # withdraw collateralprocess_unprocessed_events()
        transfer_event = event[event['event_name'] == 'transfer-withdrawReserveCollateralSupplyPubkey-destinationCollateralPubkey']
        assert len(transfer_event) > 0
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            assert user in self.loan_entities  # TODO
            # TODO: The very first liquidation events do not change the collateral.
            collateral_token = individual_transfer_event["source"]
            collateral_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            assert collateral_amount >= 0
            self.loan_entities[user].collateral.increase_value(token=collateral_token, value=-collateral_amount)

        # repay liquidity
        transfer_event = event[event['event_name'] == 'transfer-sourceLiquidityPubkey-repayReserveLiquiditySupplyPubkey']
        assert len(transfer_event) > 0  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
            assert user in self.loan_entities  # TODO
            # TODO: The very first liquidation events do not change the collateral.
            debt_token = individual_transfer_event["destination"]
            debt_amount = decimal.Decimal(str(individual_transfer_event["amount"]))
            paid_interest = 0
            assert debt_amount >= 0
            self.loan_entities[user].debt.increase_value(token=debt_token, value=-debt_amount)
            if self.loan_entities[user].debt[debt_token] < 0:
                paid_interest = -self.loan_entities[user].debt[debt_token]
                debt_amount -= paid_interest
                self.loan_entities[user].debt[debt_token] += paid_interest

        if user in self.verbose_users:
            logging.info(
                "In block number = {}, debt of raw amount = {} of token = {} and collateral of raw amount = {} of "
                "token = {} of user = {} were liquidated. \n paid interest = {} \n current debt = {}".format(
                    event["block"].iloc[0],
                    debt_amount,
                    debt_token,
                    collateral_amount,
                    collateral_token,
                    user,
                    paid_interest,
                    self.loan_entities[user].debt[debt_token]
                )
            )


if __name__ == '__main__':
    state = src.loans.solend.SolendState(
        verbose_users={'D3H9aPp5SpYZbeJ2Xe21z2XGV4bsyT5aEd31KifBMTUT'},
    )
    state.get_unprocessed_events()
    print('success')
    # state.unprocessed_events