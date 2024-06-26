import logging
import time
import itertools

import pandas as pd
import sqlalchemy
from sqlalchemy.orm.session import Session

import db
import src.visualizations.protocol_stats
import src.visualizations.main_chart
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map
from src.prices import get_prices_for_tokens


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
    ratio = liquidable_debt / supply * 100
    return f"""
    At a price of {price:.1f}, the risk of acquiring bad debt for lending protocols is very high.
    The ratio of liquidated debt to available supply is {ratio:.2f}%. Debt worth {round(liquidable_debt):,} 
    USD will be liquidated, while the DEX capacity will be {round(supply):,} USD.
    """


def get_cta_message(data: pd.DataFrame, collateral_token_price: float | None) -> str:
    '''
    Calculates the liquidable debt price point and generated message.

    Parameters:
    - data: Data containing liquidity and liquidable debt info.
    - collateral_token: collateral token address
    - debt_token: debt token address

    Returns:
    - Cta message string
    '''

    data = data.astype(float)
    data['debt_to_supply_ratio'] = data['amount'] / data['debt_token_supply']

    data = data[
        data['debt_to_supply_ratio'] >= 0.75
    ] 

    if collateral_token_price is not None:
        data = data[
            data['collateral_token_price'] <= collateral_token_price
        ]

    if len(data) == 0:
        return ''


    example_row = data.sort_values('collateral_token_price').iloc[-1]



    if not example_row.empty:
        message = generate_message(
            price=example_row['collateral_token_price'],
            liquidable_debt=example_row['amount'],
            supply=example_row['debt_token_supply'],
        )
        return message
    return ''


def get_cta_data(
    protocols: list[str],
    token_selection: src.visualizations.main_chart.TokensSelected,
    prices: dict[str, float | None],
) -> pd.DataFrame | None:
    """
    For list of protocols and selected tokens, generates df containing info about
    liquidity and liquidable debt.

    Parameters:
    - protocols: List of lending protocols which are to be considered when generating data.
    - token_selection: Selected token pair.
    - prices: map of token prices (address -> price)

    Returns:
    - dataframe or None
    """

    liquidity_entries = src.visualizations.main_chart.get_normalized_liquidity(token_selection)
    if not liquidity_entries:
        # logging.warning(f'No liquidity entries available for tokens: {token_selection}')
        return None
    
    adjusted_entries = src.visualizations.main_chart.adjust_liquidity(liquidity_entries, token_selection.loan)

    collateral_token_price = prices.get(token_selection.collateral.address)
    debt_token_price = prices.get(token_selection.loan.address)

    if not collateral_token_price or not debt_token_price:
        return None

    data = pd.DataFrame(
        {
            "collateral_token_price": src.visualizations.main_chart.get_token_range(collateral_token_price),
        }
    )

    data["debt_token_supply"] = data["collateral_token_price"].apply(
        lambda x: src.visualizations.main_chart.get_debt_token_supply_at_price_point(adjusted_entries, x, debt_token_price)
    )

    if data['debt_token_supply'].sum() < 1_000:
        return None

    # TODO: use protocols
    liquidable_dept = src.visualizations.main_chart.get_liquidable_debt(protocols=protocols, token_pair=token_selection)
    if liquidable_dept is None:
        return None
        
    data = pd.merge(
        data,
        liquidable_dept[['collateral_token_price', 'amount']],
        left_on='collateral_token_price',
        right_on='collateral_token_price',
        how='left',
    )
    data['amount'] = data['amount'].fillna(0)

    return data


def store_cta(
    timestamp: int,
    collateral_token: str,
    debt_token: str,
    message: str,
    session: Session,
):
    session.add(
        db.CallToActions(
            timestamp=timestamp,
            collateral_token=collateral_token,
            debt_token=debt_token,
            message=message,
        )
    )
    session.commit()


def generate_and_store_ctas(session: Session):
    '''
    Generates and stores CTAs for all token pairs.

    Parameters:
    - session: DB session
    '''
    
    # Get all unique mints available for token lending
    mints = src.visualizations.protocol_stats.get_unique_token_supply_mints()
    # Get token prices for the mints
    tokens_prices = get_prices_for_tokens(mints)
    # Map with mint infos (address, symbol, decimals)
    tokens_info = get_tokens_address_to_info_map()
    # Fetch tvls of lending tokens
    tvls = src.visualizations.protocol_stats.get_lending_tokens_with_tvl(tokens_prices, tokens_info)

    # Select only tokens with at least 10k usd tvl
    tvls_selected = [i[0] for i in tvls if i[1] > 10_000] 
    tokens = src.visualizations.main_chart.token_addresses_to_Token_list(
        tvls_selected, 
        tokens_info
    )

    # Generate token pairs
    tokens_combos = [(i, j) for i, j in list(itertools.product(tokens, tokens)) if i != j]
    # Filter out pairs with same base/quote
    tokens_combos = [
        src.visualizations.main_chart.TokensSelected(
            collateral=i,
            loan = j
        ) for i, j in tokens_combos
    ]
    num_combos = len(tokens_combos)
    # We want to generate CTA for all protocols
    protocols = ["kamino", "mango", "solend", "marginfi"]

    # Main loop iterating over the token pairs
    for ix, selection in enumerate(tokens_combos):
        logging.info(f'Generating cta for: {selection}')

        collateral_price = tokens_prices.get(selection.collateral.address)

        # Df containing liquidity and liquidable debt 
        df = get_cta_data(
            protocols, 
            selection,
            tokens_prices
        )

        if df is None:
            logging.warning(f'No cta data for {selection}')
            continue

        collateral_token = selection.collateral.address
        debt_token = selection.loan.address
        
        # Get CTA message
        message = get_cta_message(
            data = df,
            collateral_token_price = collateral_price
        )
        
        if not message:
            logging.warning(f'No cta message for {selection}')
            continue
    
        store_cta(
            timestamp = int(time.time()),
            collateral_token = collateral_token,
            debt_token = debt_token,
            message = message,
            session = session,
        )

        logging.info(f'Generated cta for {ix} out of {num_combos} combinations.')
    
    
def fetch_latest_cta_message(collateral_token_address: str, debt_token_address: str) -> db.CallToActions | None:
    '''
    For given collateral token and debt token, fetches latest CTA entry from DB.

    Parameters: 
    - collateral_token_address: String
    - debt_token_address: String

    Returns:
    - latest CTA entry or None
    '''
    with db.get_db_session() as sesh:
        message = sesh.query(db.CallToActions).filter(
            (db.CallToActions.collateral_token == collateral_token_address) & 
            (db.CallToActions.debt_token == debt_token_address)
        ).order_by(db.CallToActions.timestamp.desc()).limit(1).all()

    if message:
        return message[0]

    return None

def generate_cta_continuously():

    while True:
        logging.info("Generating new batch of CTAs.")

        with db.get_db_session() as sesh:
            generate_and_store_ctas(sesh)
