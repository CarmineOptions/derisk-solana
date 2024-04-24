import decimal
import logging
import warnings
from typing import Any

import pandas

import src.database
import src.loans.helpers
import src.loans.types
import src.loans.state


# Ignore all warnings
warnings.filterwarnings('ignore')


# Keys are values of the "event_name" column in the database, values are the respective method names.
EVENTS_METHODS_MAPPING: dict[str, str] = {
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
        self.reserves = SolendState._fetch_reserves()
        super().__init__(
            protocol='solend',
            loan_entity_class=SolendLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    @staticmethod
    def _fetch_reserves() -> pandas.DataFrame:
        connection = src.database.establish_connection()
        reserves = pandas.read_sql(
            sql=f"""
                select 
                    reserve_pubkey,
                    reserve_liquidity_mint_pubkey, 
                    reserve_liquidity_supply_pubkey,
                    reserve_collateral_mint_pubkey,
                    reserve_collateral_supply_pubkey
                from lenders.solend_reserves_v2;
                """,
            con=connection,
        )
        connection.close()
        return reserves

    # def get_

    def get_token_for_liquidity_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_liquidity_supply_pubkey'] == reserve_pubkey
        ].reserve_liquidity_mint_pubkey.values[0]

    def get_token_for_collateral_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_collateral_supply_pubkey'] == reserve_pubkey
        ].reserve_collateral_mint_pubkey.values[0]

    def get_reserve_for_liquidity_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_liquidity_supply_pubkey'] == reserve_pubkey
        ].reserve_pubkey.values[0]

    def get_reserve_for_collateral_supply(self, reserve_pubkey):
        return self.reserves[
            self.reserves['reserve_collateral_supply_pubkey'] == reserve_pubkey
        ].reserve_pubkey.values[0]

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
        transfer_event = event[event['event_name'].isin([
            'transfer-sourceCollateralPubkey-destinationCollateralPubkey',
            'transfer-userCollateralPubkey-destinationDepositCollateralPubkey'
        ])]
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
                    "In block number = {}, user = {} repayed amount = {} of "
                    "token = {}, \n paid interest = {} \n current debt = {}.".format(
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
        transfer_event = event[
            event['event_name'] == 'transfer-withdrawReserveCollateralSupplyPubkey-destinationCollateralPubkey']
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


def compute_liquidable_debt_at_price(
        state,
        loan_states: pandas.DataFrame,
        target_collateral_token_price: decimal.Decimal,
        collateral_token: str,
        debt_token: str,
        debt_data: list,
        collateral_data: list
) -> decimal.Decimal:
    # get current token price and liquidation params
    account = next(i for i in collateral_data if i['underlying_token'] == collateral_token)
    collateral_token_price = account['price']
    liquidation_threshold = account['config']['reserve']['config']['liquidationThreshold'] / 100
    liquidation_bonus = account['config']['reserve']['config']['liquidationBonus'] / 100
    # compute price ratio
    price_ratio = target_collateral_token_price / collateral_token_price

    # re-adjust price of collateral
    for supply_data in collateral_data:
        if supply_data['underlying_token'] == collateral_token:
            related_collateral_column = f"collateral_usd_{supply_data['supply_account']}"
            if related_collateral_column in loan_states.columns:
                loan_states[related_collateral_column] = loan_states[related_collateral_column] * price_ratio
                # re-adjust price of debt
    for supply_data in debt_data:
        if supply_data['token'] == collateral_token:
            related_debt_column = f"debt_usd_{supply_data['supply_account']}"
            if related_debt_column in loan_states.columns:
                loan_states[related_debt_column] = loan_states[related_debt_column] * price_ratio

    loan_states['total_collateral_usd'] = loan_states[[x for x in loan_states.columns if 'collateral_usd_' in x]].sum(
        axis=1)
    loan_states['total_debt_usd'] = loan_states[[x for x in loan_states.columns if 'debt_usd_' in x]].sum(axis=1)

    loan_states['loan_to_value'] = loan_states['total_debt_usd'] / loan_states['total_collateral_usd']
    loan_states['liquidable'] = loan_states['loan_to_value'] > liquidation_threshold

    # 20% of the debt value is liquidated.
    liquidable_debt_ratio = 0.2 + liquidation_bonus

    affected_debt_supply_accounts = [sa['supply_account'] for sa in debt_data if sa['token'] == debt_token]
    affected_debt_columns = [f"debt_usd_{account}" for account in affected_debt_supply_accounts]

    loan_states['affected_debt'] = loan_states[[
        x for x in loan_states.columns if x in affected_debt_columns
    ]].sum(axis=1)
    loan_states['debt_to_be_liquidated'] = liquidable_debt_ratio * loan_states['affected_debt'] * loan_states[
        'liquidable']

    return loan_states['debt_to_be_liquidated'].sum()


if __name__ == '__main__':
    state = src.loans.solend.SolendState(
        verbose_users={'D3H9aPp5SpYZbeJ2Xe21z2XGV4bsyT5aEd31KifBMTUT'},
    )
    state.get_unprocessed_events()
    print('success')
    # state.unprocessed_events