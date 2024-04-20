import decimal
import logging

import pandas

import src.loans.helpers
import src.loans.types
import src.loans.state



# Keys are values of the "instruction_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
    'borrow_obligation_liquidity': 'process_borrowing_event',
    'deposit_reserve_liquidity_and_obligation_collateral': 'process_deposit_event',
    'liquidate_obligation_and_redeem_reserve_collateral': 'process_liquidation_event',
    'repay_obligation_liquidity': 'process_repayment_event',
    'withdraw_obligation_collateral_and_redeem_reserve_collateral': 'process_withdrawal_event', 
}


def get_events(start_block_number: int = 0) -> pandas.DataFrame:
    return src.loans.helpers.get_events(
        table='lenders.kamino_parsed_transactions_v4',
        event_names=tuple(EVENTS_METHODS_MAPPING),
        event_column='instruction_name',
        start_block_number=start_block_number,
    )


class KaminoLoanEntity(src.loans.state.LoanEntity):
    """ A class that describes the Kamino loan entity. """

    def __init__(self) -> None:
        super().__init__()


class KaminoState(src.loans.state.State):
    """
    A class that describes the state of all Kamino loan entities. It implements methods for correct processing of every
    relevant event.
    """

    EVENTS_METHODS_MAPPING: dict[str, str] = EVENTS_METHODS_MAPPING

    def __init__(
        self,
        verbose_users: set[str] | None = None,
        initial_loan_states: pandas.DataFrame = pandas.DataFrame(),
    ) -> None:
        super().__init__(
            protocol='Kamino',
            loan_entity_class=KaminoLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    def get_unprocessed_events(self) -> None:
        self.unprocessed_events = src.loans.helpers.get_events(
            table='lenders.kamino_parsed_transactions_v4',
            event_names=tuple(EVENTS_METHODS_MAPPING),
            event_column='instruction_name',
            start_block_number=self.last_slot + 1,
        )

    def process_event(self, event: pandas.DataFrame) -> None:
        min_slot = event["block"].min()
        assert min_slot >= self.last_slot
        event_name = event["instruction_name"].iloc[0]
        try:  # TODO
            assert event["instruction_name"].nunique() == 1
        except:
            logging.error(f'{event_name} {event}')  # TODO
        assert event["instruction_name"].nunique() == 1
        try:  # TODO
            getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        except:
            logging.error(f'{event_name} {event}')  # TODO
            getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        self.last_slot = min_slot

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        mint_event_name = (
            'mintTo-userDestinationCollateral'
            if 'mintTo-userDestinationCollateral' in event['event_name'].to_list()
            else 'mintTo-reserveDestinationDepositCollateral'
        )
        mint_event = event[event['event_name'] == mint_event_name]
        assert len(mint_event) == 1  # TODO
        for _, individual_mint_event in mint_event.iterrows():
            user = individual_mint_event["obligation"]
            token = individual_mint_event["token"]
            amount = decimal.Decimal(str(individual_mint_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} deposited amount = {} of token = {}.".format(
                        individual_mint_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_withdrawal_event(self, event: pandas.DataFrame) -> None:
        burn_event_name = (
            'burn-userDestinationCollateral'
            if 'burn-userDestinationCollateral' in event['event_name'].to_list()
            else 'burn-reserveSourceCollateral'
        )
        burn_event = event[event['event_name'] == burn_event_name]
        assert len(burn_event) == 1  # TODO
        for _, individual_burn_event in burn_event.iterrows():
            user = individual_burn_event["obligation"]
            token = individual_burn_event["token"]
            amount = decimal.Decimal(str(individual_burn_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} withdrew amount = {} of token = {}.".format(
                        individual_burn_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_borrowing_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-reserveSourceLiquidity-userDestinationLiquidity']
        assert len(transfer_event) == 1  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
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
        if len(event) == 1:  # TODO: do not remove?
            return
        fee_transfer_event = event[event['event_name'] == 'transfer-reserveSourceLiquidity-borrowReserveLiquidityFeeReceiver']
        assert len(fee_transfer_event) == 1  # TODO
        for _, individual_fee_transfer_event in fee_transfer_event.iterrows():
            user = individual_fee_transfer_event["obligation"]
            token = individual_fee_transfer_event["source"]
            amount = decimal.Decimal(str(individual_fee_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, user = {} borrowed amount = {} of token = {}.".format(
                        individual_fee_transfer_event["block"],
                        user,
                        amount,
                        token,
                    )
                )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-userSourceLiquidity-reserveDestinationLiquidity']
        assert len(transfer_event) == 1  # TODO
        for _, individual_transfer_event in transfer_event.iterrows():
            user = individual_transfer_event["obligation"]
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
        collateral_burn_event = event[event['event_name'] == 'burn-userDestinationCollateral']
        assert len(collateral_burn_event) == 1  # TODO
        for _, individual_collateral_burn_event in collateral_burn_event.iterrows():
            user = individual_collateral_burn_event["obligation"]
            token = individual_collateral_burn_event["token"]
            amount = decimal.Decimal(str(individual_collateral_burn_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].collateral.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, collateral of amount = {} of token = {} of user = {} was liquidated.".format(
                        individual_collateral_burn_event["block"],
                        amount,
                        token,
                        user,
                    )
                )
        debt_transfer_event = event[event['event_name'] == 'transfer-userSourceLiquidity-repayReserveLiquiditySupply']
        assert len(debt_transfer_event) == 1  # TODO
        for _, individual_debt_transfer_event in debt_transfer_event.iterrows():
            user = individual_debt_transfer_event["obligation"]
            token = individual_debt_transfer_event["destination"]
            amount = decimal.Decimal(str(individual_debt_transfer_event["amount"]))
            assert amount >= 0
            self.loan_entities[user].debt.increase_value(token=token, value=-amount)
            if user in self.verbose_users:
                logging.info(
                    "In block number = {}, debt of amount = {} of token = {} of user = {} was liquidated.".format(
                        individual_debt_transfer_event["block"],
                        amount,
                        token,
                        user,
                    )
                )
