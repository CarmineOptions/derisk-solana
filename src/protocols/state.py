import abc

import pandas



# TODO: To be implemented.
class State(abc.ABC):
    """
    A class that describes the state of all loan entities of the given lending protocol.
    """

    def __init__(self) -> None:
        self.last_block_number: int = 0

    # TODO: To be implemented.
    def process_event(self, event: pandas.Series) -> None:
        pass