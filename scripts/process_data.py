import logging
import sys

sys.path.append(".")

import src.data_processing
import src.protocols.kamino
import src.protocols.mango
import src.protocols.solend
import src.protocols.state



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    src.data_processing.process_data(
        states = {
            'Kamino': src.protocols.kamino.KaminoState(),
            'Mango': src.protocols.mango.MangoState(),
            'Solend': src.protocols.solend.SolendState(),
        },
    )
