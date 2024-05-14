import decimal
import logging
from functools import lru_cache
from typing import Any, Dict

import numpy
import pandas

import src.kamino_vault_map
import src.loans.helpers
import src.loans.types
import src.loans.state
import src.loans.solend


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


class KaminoCollateralPosition(src.loans.state.CollateralPosition):
    underlying_asset_price: str = ''

    @lru_cache()
    def market_value(self):
        """ Position market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.mint}"
        assert self.c_token_exchange_rate, f"Missing collateral token exchange rate: " \
                                           f"{self.c_token_exchange_rate} for {self.mint}"
        assert self.underlying_asset_price, f"Missing asset price: {self.underlying_asset_price} for {self.mint}"
        return (
            self.amount
            * float(self.c_token_exchange_rate)
            * int(self.underlying_asset_price)
            / 10**self.decimals
        )

    @lru_cache()
    def risk_adjusted_market_value(self):
        """ Position market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.mint}"
        assert self.liquidation_threshold is not None, f"Missing liquidation threshold for {self.mint}"
        assert self.c_token_exchange_rate, f"Missing collateral token exchange rate: " \
                                           f"{self.c_token_exchange_rate} for {self.mint}"
        assert self.underlying_asset_price, f"Missing asset price: {self.underlying_asset_price} for {self.mint}"
        return (
            self.amount
            * float(self.c_token_exchange_rate)
            * int(self.underlying_asset_price)
            / 10**self.decimals
            * self.liquidation_threshold
        )


class KaminoDebtPosition(src.loans.state.DebtPosition):
    cumulative_borrow_rate: str = ''
    underlying_asset_price: str = ''

    @lru_cache()
    def risk_adjusted_market_value(self):
        """ Position risk adjusted market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.reserve}"
        assert self.cumulative_borrow_rate, f"Missing cumBorrowRate: {self.cumulative_borrow_rate}" \
                                            f" for {self.reserve}"
        assert self.weight, f"Missing borrow rate: {self.weight} for {self.reserve}"
        assert self.underlying_asset_price, f"Missing asset price: {self.underlying_asset_price} for {self.reserve}"
        return (
            self.raw_amount
            * int(self.cumulative_borrow_rate)
            * int(self.underlying_asset_price)
            / 10**self.decimals
            * self.weight
        )

    @lru_cache()
    def market_value(self):
        """ Position market value, USD """
        assert self.decimals is not None, f"Missing collateral mint decimals for {self.reserve}"
        assert self.cumulative_borrow_rate, f"Missing cumBorrowRate: {self.cumulative_borrow_rate}" \
                                            f" for {self.reserve}"
        assert self.underlying_asset_price, f"Missing asset price: " \
                                            f"{self.underlying_asset_price} for {self.reserve}"
        return (
            self.raw_amount
            * int(self.cumulative_borrow_rate)
            * int(self.underlying_asset_price)
            / 10**self.decimals
        )


class KaminoLoanEntity(src.loans.state.CustomLoanEntity):
    """ A class that describes the Kamino loan entity. """

    def update_positions_from_reserve_config(self, reserve_configs: Dict[str, Any]):
        pass  # TODO


class KaminoState(src.loans.solend.SolendState):
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
        self.reserve_configs = dict()
        self.loan_entity_class = KaminoLoanEntity
        super().__init__(
            protocol='Kamino',
            loan_entity_class=KaminoLoanEntity,
            verbose_users=verbose_users,
            initial_loan_states=initial_loan_states,
        )

    def _get_reserve_configs(self):
        pass  # TODO

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
        getattr(self, self.EVENTS_METHODS_MAPPING[event_name])(event=event)
        self.last_slot = min_slot

    def process_deposit_event(self, event: pandas.DataFrame) -> None:
        mint_event_name = (
            'mintTo-userDestinationCollateral'
            if 'mintTo-userDestinationCollateral' in event['event_name'].to_list()
            else 'mintTo-reserveDestinationDepositCollateral'
        )
        mint_event = event[event['event_name'] == mint_event_name]
        assert len(mint_event) == 1
        user = mint_event["obligation"].iloc[0]
        token = mint_event["token"].iloc[0]
        amount = decimal.Decimal(str(mint_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].collateral.increase_value(token=token, value=amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, user = {} deposited amount = {} of token = {}.".format(
                    mint_event["block"].iloc[0],
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
        assert len(burn_event) == 1
        user = burn_event["obligation"].iloc[0]
        token = burn_event["token"].iloc[0]
        amount = decimal.Decimal(str(burn_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].collateral.increase_value(token=token, value=amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, user = {} withdrew amount = {} of token = {}.".format(
                    burn_event["block"].iloc[0],
                    user,
                    amount,
                    token,
                )
            )

    def process_borrowing_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-reserveSourceLiquidity-userDestinationLiquidity']
        assert len(transfer_event) == 1
        user = transfer_event["obligation"].iloc[0]
        token = transfer_event["source"].iloc[0]
        amount = decimal.Decimal(str(transfer_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].debt.increase_value(token=token, value=amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, user = {} borrowed amount = {} of token = {}.".format(
                    transfer_event["block"].iloc[0],
                    user,
                    amount,
                    token,
                )
            )

        # Some of the events have no fee transfer.
        if len(event) == 1:
            return
        fee_transfer_event = event[event['event_name'] == 'transfer-reserveSourceLiquidity-borrowReserveLiquidityFeeReceiver']
        assert len(fee_transfer_event) == 1
        user = fee_transfer_event["obligation"].iloc[0]
        token = fee_transfer_event["source"].iloc[0]
        amount = decimal.Decimal(str(fee_transfer_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].debt.increase_value(token=token, value=amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, user = {} borrowed amount = {} of token = {}.".format(
                    fee_transfer_event["block"].iloc[0],
                    user,
                    amount,
                    token,
                )
            )

    def process_repayment_event(self, event: pandas.DataFrame) -> None:
        transfer_event = event[event['event_name'] == 'transfer-userSourceLiquidity-reserveDestinationLiquidity']
        assert len(transfer_event) == 1
        user = transfer_event["obligation"].iloc[0]
        token = transfer_event["destination"].iloc[0]
        amount = decimal.Decimal(str(transfer_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].debt.increase_value(token=token, value=-amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, user = {} repaid amount = {} of token = {}.".format(
                    transfer_event["block"].iloc[0],
                    user,
                    amount,
                    token,
                )
            )

    def process_liquidation_event(self, event: pandas.DataFrame) -> None:
        collateral_burn_event = event[event['event_name'] == 'burn-userDestinationCollateral']
        assert len(collateral_burn_event) == 1
        user = collateral_burn_event["obligation"].iloc[0]
        token = collateral_burn_event["token"].iloc[0]
        amount = decimal.Decimal(str(collateral_burn_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].collateral.increase_value(token=token, value=-amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, collateral of amount = {} of token = {} of user = {} was liquidated.".format(
                    collateral_burn_event["block"].iloc[0],
                    amount,
                    token,
                    user,
                )
            )

        debt_transfer_event = event[event['event_name'] == 'transfer-userSourceLiquidity-repayReserveLiquiditySupply']
        assert len(debt_transfer_event) == 1
        user = debt_transfer_event["obligation"].iloc[0]
        token = debt_transfer_event["destination"].iloc[0]
        amount = decimal.Decimal(str(debt_transfer_event["amount"].iloc[0]))
        assert amount >= 0
        self.loan_entities[user].debt.increase_value(token=token, value=-amount)
        if user in self.verbose_users:
            logging.info(
                "In block number = {}, debt of amount = {} of token = {} of user = {} was liquidated.".format(
                    debt_transfer_event["block"].iloc[0],
                    amount,
                    token,
                    user,
                )
            )


def compute_liquidable_debt_at_price(
    loan_states: pandas.DataFrame,
    token_prices: dict[str, float],
    debt_token_parameters: dict[str, float],
    mint_to_lp_map: dict[str, str],
    mint_to_supply_map: dict[str, str],
    collateral_token: str,
    target_collateral_token_price: decimal.Decimal,
    debt_token: str,
) -> decimal.Decimal:

    if not debt_token in mint_to_supply_map:
        return decimal.Decimal('0')
    lp_collateral_tokens = mint_to_lp_map[collateral_token]
    supply_collateral_tokens = mint_to_supply_map[collateral_token]
    supply_debt_tokens = mint_to_supply_map[debt_token]

    price_ratio = target_collateral_token_price / token_prices[collateral_token]
    for lp_collateral_token in lp_collateral_tokens:
        lp_collateral_column = f'collateral_usd_{lp_collateral_token}'
        if lp_collateral_column in loan_states.columns:
            loan_states[lp_collateral_column] = loan_states[lp_collateral_column] * price_ratio
    for supply_collateral_token in supply_collateral_tokens:
        supply_collateral_column = f'debt_usd_{supply_collateral_token}'
        if supply_collateral_column in loan_states.columns:
            loan_states[supply_collateral_column] = loan_states[supply_collateral_column] * price_ratio
    loan_states['collateral_usd'] = loan_states[[x for x in loan_states.columns if 'collateral_usd_' in x]].sum(axis = 1)
    loan_states['debt_usd'] = loan_states[[x for x in loan_states.columns if 'debt_usd_' in x]].sum(axis = 1)
    loan_states['loan_to_value'] = loan_states['debt_usd'] / loan_states['collateral_usd']

    liquidation_parameters = debt_token_parameters.get(supply_debt_tokens[0], None)
    liquidation_threshold = (
        liquidation_parameters['liquidation_threshold_pct'] / 100
        if liquidation_parameters
        else 0.5
    )
    loan_states['liquidable'] = loan_states['loan_to_value'] > liquidation_threshold
    # 20% of the debt value is liquidated.
    liquidable_debt_ratio = 0.2 * (
        1 + liquidation_parameters['min_liquidation_bonus_bps'] / 10_000
        if liquidation_parameters
        else 1.02
    )
    loan_states['debt_to_be_liquidated'] = (
        liquidable_debt_ratio
        * loan_states[f'debt_usd_{supply_debt_tokens[0]}']
        * loan_states['liquidable']
    )
    return loan_states['debt_to_be_liquidated'].sum()

def get_kamino_user_stats_df(loan_states: pandas.DataFrame) -> pandas.DataFrame:

    MINT_TO_LP_MAPPING = {x: [] for x in src.kamino_vault_map.lp_to_mint_map.values()}
    for x, y in src.kamino_vault_map.lp_to_mint_map.items():
        MINT_TO_LP_MAPPING[y].append(x)
    MINT_TO_SUPPLY_MAPPING = {x: [] for x in src.kamino_vault_map.supply_vault_to_mint_map.values()}
    for x, y in src.kamino_vault_map.supply_vault_to_mint_map.items():
        MINT_TO_SUPPLY_MAPPING[y].append(x)

    collateral_tokens = {token for collateral in loan_states['collateral'] for token in collateral}
    debt_tokens = {token for debt in loan_states['debt'] for token in debt}

    underlying_collateral_tokens = [
        src.kamino_vault_map.lp_to_mint_map[x]
        for x in collateral_tokens
        if x in src.kamino_vault_map.lp_to_mint_map
    ]
    underlying_debt_tokens = [
        src.kamino_vault_map.supply_vault_to_mint_map[x]
        for x in debt_tokens
        if x in src.kamino_vault_map.supply_vault_to_mint_map
    ]
    token_prices = src.prices.get_prices_for_tokens(underlying_collateral_tokens + underlying_debt_tokens)

    collateral_token_parameters = {
        token: src.kamino_vault_map.lp_to_info_map.get(token, None)
        for token
        in collateral_tokens
    }
    debt_token_parameters = {
        debt_token: src.kamino_vault_map.supply_to_info_map.get(debt_token, None)
        for debt_token
        in debt_tokens
    }

    for token in collateral_tokens:
        loan_states[f'collateral_{token}'] = loan_states['collateral'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )
    for token in debt_tokens:
        loan_states[f'debt_{token}'] = loan_states['debt'].apply(
            lambda x: x[token] if token in x else decimal.Decimal('0')
        )
    
    for token in collateral_tokens:
        if not collateral_token_parameters[token]:
            continue
        if not collateral_token_parameters[token]['underlying_decs']:
            continue
        decimals = collateral_token_parameters[token]['underlying_decs']
        ltv = collateral_token_parameters[token]['ltv']
        underlying_token = src.kamino_vault_map.lp_to_mint_map[token]

        loan_states[f'collateral_usd_{token}'] = (
            loan_states[f'collateral_{token}'].astype(float)
            / (10**decimals)
            * token_prices[underlying_token]
        )
        
        loan_states[f'risk_adj_collateral_usd_{token}'] = loan_states[f'collateral_usd_{token}'] * (ltv/100)
    
    for debt_token in debt_tokens:
        if not debt_token_parameters[debt_token]:
            continue
        if not debt_token_parameters[debt_token]['underlying_decs']:
            continue
        decimals = debt_token_parameters[debt_token]['underlying_decs']
        ltv = debt_token_parameters[debt_token]['ltv']
        underlying_token = src.kamino_vault_map.supply_vault_to_mint_map[debt_token]
        loan_states[f'debt_usd_{debt_token}'] = (
            loan_states[f'debt_{debt_token}'].astype(float)
            / (10**decimals)
            * token_prices[underlying_token]
        )
        loan_states[f'risk_adj_debt_usd_{debt_token}'] = loan_states[f'debt_usd_{debt_token}'] * (1/(ltv/100) if ltv else 1)
        
    loan_states['risk_adj_debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_debt_usd_')]].sum(axis=1)
    loan_states['debt_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('debt_usd_')]].sum(axis=1)

    loan_states['risk_adj_collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('risk_adj_collateral_usd_')]].sum(axis=1)
    loan_states['collateral_usd'] = loan_states[[i for i in loan_states.columns if i.startswith('collateral_usd_')]].sum(axis=1)

    loan_states['std_health'] = (loan_states['risk_adj_collateral_usd'] / loan_states['risk_adj_debt_usd']).fillna(numpy.inf)


    wanted_cols = [
        'protocol', 
        'user', 
        'std_health',
        'collateral_usd', 
        'risk_adj_collateral_usd',
        'debt_usd', 
        'risk_adj_debt_usd',
        'collateral',
        'debt',
    ]
    return loan_states[wanted_cols]