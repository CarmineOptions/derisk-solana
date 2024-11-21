import logging
import time
import itertools
from typing import List

import pandas
import pandas as pd
import sqlalchemy
from sqlalchemy.orm.session import Session

import db
import src.visualizations.protocol_stats
import src.visualizations.main_chart
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map
from src.prices import get_prices_for_tokens


LOGGER = logging.getLogger(__name__)


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
    liquidable_debt_data: pandas.DataFrame | None = None
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
        lambda x: src.visualizations.main_chart.get_debt_token_supply_at_price_point(adjusted_entries, x,
                                                                                     debt_token_price)
    )

    if data['debt_token_supply'].sum() < 1_000:
        return None

    if liquidable_debt_data:
        latest_liquidable_debt_per_pair = []
        for protocol in liquidable_debt_data.protocol.unique():
            last_slot = liquidable_debt_data[liquidable_debt_data.protocol == protocol].slot.max()
            latest_liquidable_debt_per_pair.append(
                liquidable_debt_data[
                    (liquidable_debt_data.protocol == protocol) & (liquidable_debt_data.slot == last_slot)]
            )

        liquidable_debt_per_protocol = pd.concat(latest_liquidable_debt_per_pair)
        liquidable_dept = (
            liquidable_debt_per_protocol.groupby(["collateral_token", "debt_token", "collateral_token_price"])
            .agg({"amount": "sum"})
            .reset_index()
        )
    else:
        liquidable_dept = src.visualizations.main_chart.get_liquidable_debt(protocols=protocols,
                                                                            token_pair=token_selection)

    if liquidable_dept is not None:
        data = pd.merge(
            data,
            liquidable_dept[['collateral_token_price', 'amount']],
            left_on='collateral_token_price',
            right_on='collateral_token_price',
            how='left',
        )
        data['amount'] = data['amount'].fillna(0)

        return data

    return None


def store_cta(
    timestamp: int,
    collateral_token: str,
    debt_token: str,
    message: str,
    session: Session,
):
    # TODO store only if differ from the last message stored if not skip, mb add last update field.
    session.add(
        db.CallToActions(
            timestamp=timestamp,
            collateral_token=collateral_token,
            debt_token=debt_token,
            message=message,
        )
    )
    session.commit()


def get_complete_liquidable_debt_data(protocols: List[str]) -> pandas.DataFrame:
    """
    Collect all available liquidable debt data for given protocols
     and for all pairs present in last 2 runs of liquidable debt computations.
    :param protocols: list of protocols
    :return:
    """
    data_for_protocols = []
    LOGGER.info(f"Start collecting liquidable debt data for protocols {protocols}.")
    timestamp = time.time()
    for protocol in protocols:
        LOGGER.info(f"Start collecting liquidable debt data for `{protocol}`")
        model = src.visualizations.main_chart.protocol_to_model(protocol)
        with db.get_db_session() as _session:
            latest_two_slots_subquery = (
                _session.query(model.slot)
                .distinct()
                .order_by(model.slot.desc())
                .limit(2)
            ).subquery()

            # data over all protocols for the last two slots
            data = (
                _session.query(model)
                .filter(model.slot.in_(latest_two_slots_subquery))
                .all()
            )
            df = pd.DataFrame(
                [
                    {
                        "collateral_token": d.collateral_token,
                        "debt_token": d.debt_token,
                        "collateral_token_price": d.collateral_token_price,
                        "amount": d.amount,
                        "slot": d.slot,
                        "protocol": d.protocol
                    }
                    for d in data
                ]
            )

            data_for_protocols.append(df)
    complete_liquidable_debt_data = pd.concat(data_for_protocols)
    LOGGER.info(f"Complete liquidable debt data collected in {(time.time() - timestamp):.2f} sec.")
    return complete_liquidable_debt_data


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
    protocols = ["kamino", "mango", "solend", "marginfi"]
    liquidable_debt_data = get_complete_liquidable_debt_data(protocols)
    unique_pairs = liquidable_debt_data[['collateral_token', 'debt_token']].drop_duplicates()

    # Convert the DataFrame to a set of unique pairs
    pairs_with_liq_debt_data = set(unique_pairs.apply(tuple, axis=1))
    LOGGER.info(f"Liquidable debt found for {len(pairs_with_liq_debt_data)} unique pairs.")
    # Generate token pairs
    tokens_combos = [
        (i, j) for i, j in list(itertools.product(tokens, tokens))
        if i != j
    ]
    # Filter out pairs with same base/quote
    tokens_combos = [
        src.visualizations.main_chart.TokensSelected(
            collateral=i,
            loan = j
        ) for i, j in tokens_combos
    ]
    # filter out pairs without liquidable debt
    tokens_combos = [i for i in tokens_combos if (i.collateral.address, i.loan.address) in pairs_with_liq_debt_data]
    num_combos = len(tokens_combos)
    LOGGER.info(f"{num_combos} unique pairs to process.")
    # We want to generate CTA for all protocols
    # Main loop iterating over the token pairs
    for ix, selection in enumerate(tokens_combos):
        LOGGER.info(f'Generating cta for: {selection}')

        collateral_price = tokens_prices.get(selection.collateral.address)
        if collateral_price is None:
            logging.error(f"Collateral token price is None for address: {selection.collateral.address}")

        # Df containing liquidity and liquidable debt 
        cta_data = get_cta_data(
            protocols, 
            selection,
            tokens_prices,
            liquidable_debt_data[
                (liquidable_debt_data.collateral_token == selection.collateral.address)
                &
                (liquidable_debt_data.debt_token == selection.loan.address)
            ]
        )

        if cta_data is None:
            LOGGER.warning(f'No cta data for {selection}')
            continue

        collateral_token = selection.collateral.address
        debt_token = selection.loan.address
        
        # Get CTA message
        message = get_cta_message(
            data = cta_data,
            collateral_token_price = collateral_price
        )
        
        if not message:
            LOGGER.warning(f'No cta message for {selection}')
            continue

        store_cta(
            timestamp = int(time.time()),
            collateral_token = collateral_token,
            debt_token = debt_token,
            message = message,
            session = session,
        )

        LOGGER.info(f'Generated cta for {ix} out of {num_combos} combinations.')
    
    
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
