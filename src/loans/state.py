import abc
import collections
import logging

import pandas

import src.loans.types



class LoanEntity(abc.ABC):
    """
    A class that describes and entity which can hold collateral, borrow debt and be liquidable. For example, on 
    Starknet, such an entity is the user in case of zkLend, Nostra Alpha and Nostra Mainnet, or an individual loan in 
    case od Hashstack V0 and Hashstack V1.
    """

    def __init__(self) -> None:
        self.collateral: src.loans.types.Portfolio = src.loans.types.Portfolio()
        self.debt: src.loans.types.Portfolio = src.loans.types.Portfolio()


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
        self.set_initial_loan_states(initial_loan_states=initial_loan_states)
        self.unprocessed_events: pandas.DataFrame = pandas.DataFrame()
        self.last_slot: int = 0

    def set_initial_loan_states(self, initial_loan_states: pandas.DataFrame) -> None:
        if initial_loan_states.empty:
            return
        assert initial_loan_states['protocol'].nunique() == 1
        assert initial_loan_states['protocol'].iloc[0] == self.protocol
        assert initial_loan_states['slot'].nunique() == 1
        self.last_slot = initial_loan_states['slot'].iloc[0]
        for _, loan_state in initial_loan_states.iterrows():
            user = loan_state['user']
            self.loan_entities[user].collateral = loan_state['collateral']
            self.loan_entities[user].debt = loan_state['debt']

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
            self.process_event(event=event)
        self.unprocessed_events = pandas.DataFrame()

    @abc.abstractmethod
    def process_event(self) -> None:
        pass