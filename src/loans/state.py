import abc
import collections
import decimal
import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Any, Dict

import pandas

import src.loans.types

@dataclass
class CollateralPosition:
    reserve: str
    mint: str
    amount: float
    decimals: int | None = None
    ltv: float | None = None
    c_token_exchange_rate: float = ''
    liquidation_threshold: float | None = None
    liquidation_bonus: float | None = None
    underlying_asset_price_wad: str = ''
    underlying_token: str = ''

    def __hash__(self):
        return hash((self.reserve, self.mint, round(self.amount, 10)))

    @abc.abstractmethod
    def market_value(self):
        """ Position market value, USD """
        raise NotImplementedError('Implement me!')

    @abc.abstractmethod
    def risk_adjusted_market_value(self):
        """ Position market value, USD """
        raise NotImplementedError('Implement me!')


@dataclass
class DebtPosition:
    reserve: str
    mint: str
    raw_amount: float
    decimals: int | None = None
    weight: float | None = None
    cumulative_borrow_rate_wad: str = ''
    underlying_asset_price_wad: str = ''
    borrow_factor: float | None = None

    def __hash__(self):
        return hash((self.reserve, self.mint, round(self.raw_amount, 10)))

    @abc.abstractmethod
    def risk_adjusted_market_value(self):
        """ Position risk adjusted market value, USD """
        raise NotImplementedError('Implement me!')

    @abc.abstractmethod
    def market_value(self):
        """ Position market value, USD """
        raise NotImplementedError('Implement me!')


class CustomLoanEntity:
    """ A class that describes the Solend loan entity. """

    def __init__(self, obligation: str, slot: int) -> None:
        self.collateral: List[CollateralPosition] = list()
        self.debt: List[DebtPosition] = list()
        self.obligation = obligation
        self.last_updated = slot

    @property
    def is_zero_debt(self):
        if not self.debt:
            return True
        return all([position.raw_amount == 0 for position in self.debt])

    @property
    def is_zero_deposit(self):
        if not self.collateral:
            return True
        return all([position.amount == 0 for position in self.collateral])

    @lru_cache()
    def collateral_market_value(self):
        return sum([position.market_value() for position in self.collateral])

    @lru_cache()
    def debt_market_value(self):
        return sum([position.market_value() for position in self.debt])

    @lru_cache()
    def collateral_risk_adjusted_market_value(self):
        return sum([position.risk_adjusted_market_value() for position in self.collateral])

    @lru_cache()
    def debt_risk_adjusted_market_value(self):
        return sum([position.risk_adjusted_market_value() for position in self.debt])

    @lru_cache()
    def std_health_ratio(self) -> str:
        """
        Compute standardized health ratio:
            std_health_ratio = risk adjusted collateral / risk adjusted debt
        :return:
        """
        if self.is_zero_debt:
            return 'inf'
        if self.is_zero_deposit:
            return '0'
        deposited_value = self.collateral_risk_adjusted_market_value()
        borrowed_value = self.debt_risk_adjusted_market_value()
        return str(round(deposited_value / borrowed_value, 6))

    @lru_cache()
    def health_ratio(self) -> str:
        """
        Compute Solend health ratio:
            health_ratio = risk adjusted debt / risk adjusted collateral
        :return:
        """
        std_health_ratio = self.std_health_ratio()
        if std_health_ratio == 'inf':
            return '0'
        if std_health_ratio in {'0', '0.0'}:
            return 'inf'
        std_health_ratio_num = float(std_health_ratio)
        health_ratio = 1 / std_health_ratio_num
        return str(round(health_ratio, 6))

    def get_unique_reserves(self) -> List[str]:
        reserves = []
        if self.debt:
            reserves.extend([position.reserve for position in self.debt])
        if self.collateral:
            reserves.extend([position.reserve for position in self.collateral])
        return list(set(reserves))

    @abc.abstractmethod
    def update_positions_from_reserve_config(self, reserve_configs: Dict[str, Any], prices: Dict[str, Any]):
        """ Fill missing data in position object with parameters from reserve configs. """
        raise NotImplementedError('Implement me!')


class LoanEntity(abc.ABC):
    """
    A class that describes and entity which can hold collateral, borrow debt and be liquidable.
    """

    def __init__(self) -> None:
        self.collateral: src.loans.types.Portfolio = src.loans.types.Portfolio()
        self.debt: src.loans.types.Portfolio = src.loans.types.Portfolio()

    def is_zero_debt(self):
        return self.debt.is_zero()


class State(abc.ABC):
    """
    A class that describes the state of all loan entities of the given lending protocol.
    """

    EVENTS_METHODS_MAPPING: dict[str, str] = {}

    def __init__(
        self,
        protocol: str,
        loan_entity_class: LoanEntity,
        verbose_users: set[str] | None = None,
        initial_loan_states: pandas.DataFrame = pandas.DataFrame(),
    ) -> None:
        self.protocol: str = protocol
        self.loan_entity_class: LoanEntity = loan_entity_class
        self.verbose_users: set[str] | None = verbose_users
        self.loan_entities: collections.defaultdict = collections.defaultdict(self.loan_entity_class)
        self.last_slot: int = 0
        self.set_initial_loan_states(initial_loan_states=initial_loan_states)
        self.unprocessed_events: pandas.DataFrame = pandas.DataFrame()

    def set_initial_loan_states(self, initial_loan_states: pandas.DataFrame) -> None:
        if initial_loan_states.empty:
            return
        assert initial_loan_states['protocol'].nunique() == 1
        assert initial_loan_states['protocol'].iloc[0] == self.protocol
        assert initial_loan_states['slot'].nunique() == 1
        self.last_slot = initial_loan_states['slot'].iloc[0]
        for _, loan_state in initial_loan_states.iterrows():
            user = loan_state['user']
            for collateral_token, collateral_amount in loan_state['collateral'].items():
                if collateral_amount:
                    self.loan_entities[user].collateral[collateral_token] = decimal.Decimal(str(collateral_amount))
            for debt_token, debt_amount in loan_state['debt'].items():
                if debt_amount:
                    self.loan_entities[user].debt[debt_token] = decimal.Decimal(str(debt_amount))

    @abc.abstractmethod
    def get_unprocessed_events(self) -> None:
        pass

    def process_unprocessed_events(self) -> None:
        min_unprocessed_slot = self.unprocessed_events['block'].min()
        if min_unprocessed_slot < self.last_slot:
            logging.warning(
                'Minimum unprocessed slot  = {} is lower than last slot = {}. Refreshing unprocessed events.'.format(
                    min_unprocessed_slot,
                    self.last_slot,
                )
            )
            self.get_unprocessed_events()

        if self.unprocessed_events.empty:
            return

        # Iterate over ordered events to obtain the final state of each user.
        for _, event in self.unprocessed_events.groupby(['transaction_id', 'instruction_name'], sort=False):
            try:
                self.process_event(event=event)
            except:
                logging.error('Failed to process event data = {}.'.format(event), exc_info=True)
        self.unprocessed_events = pandas.DataFrame()

    @abc.abstractmethod
    def process_event(self) -> None:
        pass
