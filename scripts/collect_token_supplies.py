import logging
from src.protocols.token_supplies import update_token_supplies_continuously


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    update_token_supplies_continuously()
