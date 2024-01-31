from typing import Any

import src.protocols.kamino
import src.protocols.mango
import src.protocols.solend
import src.protocols.state



# TODO: To be defined.
LAST_UPDATE_FILENAME: str = ''
# TODO: To be defined.
PERSISTENT_STATE_DIRECTORY: str = ''


# TODO: To be implemented.
def upload_object_as_pickle(
	object: Any,
	path: str,
) -> None:
	pass


# TODO: To be implemented.
def load_states() -> dict[str, src.protocols.state.State]:
	return {
		'Kamino': src.protocols.kamino.KaminoState(),
		'Mango': src.protocols.mango.MangoState(),
		'Solend': src.protocols.solend.SolendState(),
	}


# TODO: To be implemented.
def get_last_update() -> dict[str, str]:
	return {"timestamp": '1681284183', "block_number": ''}