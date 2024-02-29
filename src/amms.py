# TODO: To be implemented.
from abc import ABC


class Amms:
	"""
	A class that describes the state of all relevant pools of all relevant swap AMMs.
	"""

	def __init__(self) -> None:
		pass

	def update_pools(self) -> None:
		pass


# TODO: To be implemented.
def load_amm_data() -> Amms:
	amms = Amms()
	amms.update_pools()
	return amms


class Amm(ABC):

	def __init__(self):
		pass


class OrcaAMM(Amm):
	pass


class RaydiumAMM(Amm):
	pass


class MeteoraAMM(Amm):
	pass
