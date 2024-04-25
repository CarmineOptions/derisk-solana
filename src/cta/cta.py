import logging
import time

import sqlalchemy
from sqlalchemy.orm.session import Session

from db import CallToActions, DexNormalizedLiquidity, get_db_session


def generate_message(
    price: int | float, liquidable_debt: int | float, supply: int | float
) -> str:
    """
    Generates Call To Action message from arguments
    Arguments:
        price: underlying token price in USD
        liquidable_debt: amount of debt in USD that can be liquidated at the given price
        supply: amount of underlying token in USD that can be immediately used for liquidation

    Returns:
        CTA message
    """
    ratio = round(liquidable_debt / supply, 2)
    return f"""
    At price of {price}, the risk of acquiring bad debt for lending protocols is very high.
    The ratio of liquidated debt to available supply is {ratio}%.Debt worth of {round(liquidable_debt)} 
    USD will be liquidated while the dex capacity will be {round(supply)} USD.
    """


def store_cta(
    timestamp: int,
    collateral_token: str,
    debt_token: str,
    message: str,
    session: Session,
):
    session.add(
        CallToActions(
            timestamp=timestamp,
            collateral_token=collateral_token,
            debt_token=debt_token,
            message=message,
        )
    )
    session.commit()


def calculate_cta(collateral_token: str, debt_token: str):
    with get_db_session() as session:
        result = (
            session.query(DexNormalizedLiquidity)
            .filter(
                DexNormalizedLiquidity.timestamp
                == session.query(sqlalchemy.func.max(DexNormalizedLiquidity.timestamp)),
                DexNormalizedLiquidity.token_x_address == collateral_token,
                DexNormalizedLiquidity.token_y_address == debt_token,
            )
            .all()
        )

    print(result)


def generate_cta_continuously():
    logging.info("Starting CTAs generation.")
    session = get_db_session()

    while True:
        logging.info("Generated CTAs.")
        time.sleep(3600)