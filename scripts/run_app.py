# import datetime
import logging

# import multiprocessing
# import os
import sys

import streamlit as st

sys.path.append(".")

import plotly.express as px
import numpy as np

# import src.data_processing
# import src.persistent_state
# import src.prices
# import src.visualizations.histogram
import src.cta.cta
import src.prices
import src.visualizations.protocol_stats
import src.protocols
import src.visualizations.main_chart
import src.visualizations.settings
from src.prices import get_prices_for_tokens
from src.protocols.dexes.amms.utils import get_tokens_address_to_info_map
import src.visualizations.loans_table
import src.visualizations.user_stats


def main():
    st.title("DeRisk Solana")

    tokens_available = src.visualizations.protocol_stats.get_unique_token_supply_mints()
    if not tokens_available:
        tokens_available = [
            "So11111111111111111111111111111111111111112", # SOL
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", # USDC
        ]
        # TODO: handle better

    tokens_info = get_tokens_address_to_info_map()
    tokens_prices = get_prices_for_tokens(tokens_available)
    tokens_with_tvl = src.visualizations.protocol_stats.get_lending_tokens_with_tvl(tokens_prices, tokens_info)

    tokens_to_offer = [i[0] for i in tokens_with_tvl]

    tokens = src.visualizations.main_chart.token_addresses_to_Token_list(
        tokens_to_offer, tokens_info
    )

    # Select protocols and token pair of interest.
    col1, col2, col3 = st.columns(3)

    with col1:
        protocols = st.multiselect(
            label="Select protocols",
            options=["kamino", "mango", "solend", "marginfi"],
            default=["kamino", "mango", "solend", "marginfi"],
        )

    with col2:
        collateral_token = st.selectbox(
            label="Select collateral token:",
            options=tokens,
            index=0,
        )

    with col3:
        loan_token = st.selectbox(
            label="Select loan token:",
            options=tokens,
            index=2,
        )

    selected_tokens = src.visualizations.main_chart.TokensSelected(
        collateral=collateral_token,  # type: ignore
        loan=loan_token,  # type: ignore
    )

    # # Load relevant data and plot the liquidable debt against the available supply.
    main_chart_data = src.visualizations.main_chart.get_main_chart_data(
        protocols=protocols,
        token_selection=selected_tokens,  # type: ignore
        prices=tokens_prices,
    )
    main_chart_figure = src.visualizations.main_chart.get_figure(
        token_pair=selected_tokens, data=main_chart_data, prices=tokens_prices
    )
    st.plotly_chart(figure_or_data=main_chart_figure, use_container_width=True)


    # Compute the price at which the liquidable debt to the available supply ratio is dangerous. Create and display the
    # warning message.
    cta_message = src.cta.cta.fetch_latest_cta_message(
        collateral_token_address=selected_tokens.collateral.address,
        debt_token_address=selected_tokens.loan.address,
    )

    if cta_message:
        st.write(cta_message.message)

    # # Select the range of debt in USD and display individual loans with the lowest health factors.
    # streamlit.header("Loans with low health factor")
    # loans_table_data = src.visualizations.loans_table.load_data(protocols=protocols, token_pair=token_pair)  # type: ignore
    # col1, _ = streamlit.columns([1, 3])
    # with col1:
    # 	# TODO: Use `int(loans_table_data["Debt (USD)"].max())`.
    # 	max_debt_usd = 100
    # 	debt_usd_lower_bound, debt_usd_upper_bound = streamlit.slider(
    # 		label="Select range of USD debt",
    # 		min_value=0,
    # 		max_value=max_debt_usd,
    # 		value=(0, max_debt_usd),
    # 	)
    # streamlit.dataframe(
    # 	loans_table_data[
    # 		loans_table_data["Debt (USD)"].between(debt_usd_lower_bound, debt_usd_upper_bound)
    # 	].sort_values("Health factor").iloc[:20],
    # 	use_container_width=True,
    # )


    # # Display comparison stats for all lending protocols.
    st.header("Comparison of lending protocols")

    st.subheader("Token utilizations")
    utilizations_df = src.visualizations.protocol_stats.get_token_utilizations_df(tokens_prices, tokens_info)
    st.dataframe(utilizations_df, use_container_width=True)

    token_supplies_df = src.visualizations.protocol_stats.get_top_12_lending_supplies_df(
        tokens_prices, tokens_info
    )
    if len(token_supplies_df) == 0:
        # TODO: Handle
        pass

    supplies_data = list(token_supplies_df.groupby("symbol"))
    supplies_data.sort(key=lambda x: x[1]["Deposits"].sum(), reverse=True)
    supplies_data_chunks = src.prices.split_into_chunks(supplies_data, 3)

    columns = st.columns(4)
    for column, supply_chunk in zip(columns, supplies_data_chunks):
        with column:
            for token_symbol, token_supply_df in supply_chunk:
                to_show = "Deposits"
                figure = px.pie(
                    token_supply_df[["Protocol", to_show]]
                    .groupby("Protocol")
                    .sum()
                    .reset_index(),
                    values=to_show,
                    names="Protocol",
                    title=f"{token_symbol} {to_show}, Total: ${token_supply_df[to_show].sum():,.2f}",
                    color_discrete_sequence=px.colors.sequential.Oranges_r,
                )
                st.plotly_chart(figure, True)

            for token_symbol, token_supply_df in supply_chunk:
                to_show = "Borrowed"
                figure = px.pie(
                    token_supply_df[["Protocol", to_show]]
                    .groupby("Protocol")
                    .sum()
                    .reset_index(),
                    values=to_show,
                    names="Protocol",
                    title=f"{token_symbol} {to_show}, Total: ${token_supply_df[to_show].sum():,.2f}",
                    color_discrete_sequence=px.colors.sequential.Greens_r,
                )
                st.plotly_chart(figure, True)

            for token_symbol, token_supply_df in supply_chunk:
                to_show = "Available"
                figure = px.pie(
                    token_supply_df[["Protocol", to_show]]
                    .groupby("Protocol")
                    .sum()
                    .reset_index(),
                    values=to_show,
                    names="Protocol",
                    title=f"{token_symbol} {to_show}, Total: ${token_supply_df[to_show].sum():,.2f}",
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                )
                st.plotly_chart(figure, True)

    st.subheader("User healths")
    user_health_ratios_df = src.visualizations.loans_table.load_user_health_ratios(protocols)
    st.dataframe(user_health_ratios_df.sort_values('Standardized Health Factor', ascending=True).head(50), use_container_width=True)
    
    st.subheader("User statistics")
    user_stats_df = src.visualizations.user_stats.load_users_stats(protocols)
    st.dataframe(user_stats_df, use_container_width=True)

# t = data[0][1][['protocol', 'Borrowed', 'Deposits', 'Available']].groupby('protocol').sum()


# data = list(df.groupby('symbol'))

# # Plot supply, collateral and debt stats for all lending protocols.
# collateral_stats = src.visualizations.protocol_stats.load_collateral_stats()
# debt_stats = src.visualizations.protocol_stats.load_debt_stats()
# supply_stats = src.visualizations.protocol_stats.load_supply_stats()
# columns = streamlit.columns(6)
# for column, token in zip(columns, src.visualizations.settings.TOKENS):
# 	with column:
# 		collateral_stats_figure = src.visualizations.protocol_stats.get_collateral_stats_figure(
# 			data=collateral_stats,
# 			token=token,
# 		)
# 		streamlit.plotly_chart(figure_or_data=collateral_stats_figure, use_container_width=True)
# 		debt_stats_figure = src.visualizations.protocol_stats.get_debt_stats_figure(
# 			data=debt_stats,
# 			token=token,
# 		)
# 		streamlit.plotly_chart(figure_or_data=debt_stats_figure, use_container_width=True)
# 		supply_stats_figure = src.visualizations.protocol_stats.get_supply_stats_figure(
# 			data=supply_stats,
# 			token=token,
# 		)
# 		streamlit.plotly_chart(figure_or_data=supply_stats_figure, use_container_width=True)

# # Plot histograms of loan size distribution.
# streamlit.header("Loan size distribution")
# histogram_data = src.visualizations.histogram.load_data(protocols=protocols, token_pair=token_pair)  # type: ignore
# histogram_figure = src.visualizations.histogram.get_figure(data=histogram_data)
# streamlit.plotly_chart(figure_or_data=histogram_figure, use_container_width=True)

# # Display information about the last update.
# last_update = src.persistent_state.get_last_update()
# last_timestamp = last_update["timestamp"]
# last_block_number = last_update["block_number"]
# date_str = datetime.datetime.utcfromtimestamp(int(last_timestamp))
# streamlit.write(f"Last update timestamp: {date_str} UTC, last block: {last_block_number}.")


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    st.set_page_config(
        layout="wide",
        page_title="DeRisk by Carmine Finance",
        page_icon="https://carmine.finance/assets/logo.svg",
    )

    # if os.environ.get("CONTINUOUS_DATA_PROCESSING_PROCESS_RUNNING") is None:
    # 	os.environ["CONTINUOUS_DATA_PROCESSING_PROCESS_RUNNING"] = "True"
    # 	logging.info("Spawning data processing process.")
    # 	data_processing_process = multiprocessing.Process(
    # 		target=src.data_processing.process_data_continuously,
    # 		daemon=True,
    # 	)
    # 	data_processing_process.start()
    main()
