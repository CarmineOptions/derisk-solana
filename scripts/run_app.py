import datetime
import logging
import multiprocessing
import os
import sys

import streamlit

sys.path.append(".")

import src.data_processing
import src.persistent_state
import src.visualizations.histogram
import src.visualizations.loans_table
import src.visualizations.main_chart
import src.visualizations.protocol_stats
import src.visualizations.settings



def main():
	streamlit.title("DeRisk Solana")

	# Select protocols and token pair of interest.
	col1, _ = streamlit.columns([1, 3])
	with col1:
		protocols = streamlit.multiselect(
			label="Select protocols",
			options=["Kamino", "Mango", "Solend"],
			default=["Kamino", "Mango", "Solend"],
		)
		token_pair = streamlit.selectbox(
			label="Select collateral-loan token pair:",
			options=src.visualizations.settings.TOKEN_PAIRS,
			index=0,
		)

	# Load relevant data and plot the liquidable debt against the available supply.
	main_chart_data = src.visualizations.main_chart.load_data(protocols=protocols, token_pair=token_pair)
	main_chart_figure = src.visualizations.main_chart.get_figure(
		data=main_chart_data, 
		token_pair=token_pair,
	)
	streamlit.plotly_chart(figure_or_data=main_chart_figure, use_container_width=True)

	# Compute the price at which the liquidable debt to the available supply ratio is dangerous. Create and display the
	# warning message.
	dangerous_price_level_data = src.visualizations.main_chart.get_dangerous_price_level_data(data=main_chart_data)
	if not dangerous_price_level_data.empty:
		streamlit.subheader(
			f":warning: At price of {dangerous_price_level_data['collateral_token_price']}, the risk of acquiring bad "
			f"debt for lending protocols is {src.visualizations.main_chart.get_risk(data=dangerous_price_level_data)}."
		)    
		streamlit.write(
			f"The ratio of liquidated debt to available supply is "
			f"{dangerous_price_level_data['debt_to_supply_ratio'] * 100}%. Debt worth of "
			f"{dangerous_price_level_data['liquidable_debt_at_interval']} USD will be liquidated while the AMM swaps "
			f"capacity will be {dangerous_price_level_data['debt_token_supply']} USD."
		)

	# Select the range of debt in USD and display individual loans with the lowest health factors.
	streamlit.header("Loans with low health factor")
	loans_table_data = src.visualizations.loans_table.load_data(protocols=protocols, token_pair=token_pair)
	col1, _ = streamlit.columns([1, 3])
	with col1:
		# TODO: Use `int(loans_table_data["Debt (USD)"].max())`.
		max_debt_usd = 100
		debt_usd_lower_bound, debt_usd_upper_bound = streamlit.slider(
			label="Select range of USD debt",
			min_value=0,
			max_value=max_debt_usd,
			value=(0, max_debt_usd),
		)
	streamlit.dataframe(
		loans_table_data[
			loans_table_data["Debt (USD)"].between(debt_usd_lower_bound, debt_usd_upper_bound)
		].sort_values("Health factor").iloc[:20],
		use_container_width=True,
	)

	# Display comparison stats for all lending protocols.
	streamlit.header("Comparison of lending protocols")
	streamlit.dataframe(src.visualizations.protocol_stats.load_general_stats())
	streamlit.dataframe(src.visualizations.protocol_stats.load_utilization_stats())
	# Plot supply, collateral and debt stats for all lending protocols.
	collateral_stats = src.visualizations.protocol_stats.load_collateral_stats()
	debt_stats = src.visualizations.protocol_stats.load_debt_stats()
	supply_stats = src.visualizations.protocol_stats.load_supply_stats()
	columns = streamlit.columns(6)
	for column, token in zip(columns, src.visualizations.settings.TOKENS):
		with column:
			collateral_stats_figure = src.visualizations.protocol_stats.get_collateral_stats_figure(
				data=collateral_stats, 
				token=token,
			)
			streamlit.plotly_chart(figure_or_data=collateral_stats_figure, use_container_width=True)
			debt_stats_figure = src.visualizations.protocol_stats.get_debt_stats_figure(
				data=debt_stats, 
				token=token,
			)
			streamlit.plotly_chart(figure_or_data=debt_stats_figure, use_container_width=True)
			supply_stats_figure = src.visualizations.protocol_stats.get_supply_stats_figure(
				data=supply_stats, 
				token=token,
			)
			streamlit.plotly_chart(figure_or_data=supply_stats_figure, use_container_width=True)

	# Plot histograms of loan size distribution.
	streamlit.header("Loan size distribution")
	histogram_data = src.visualizations.histogram.load_data(protocols=protocols, token_pair=token_pair)  # TODO
	histogram_figure = src.visualizations.histogram.get_figure(data=histogram_data)
	streamlit.plotly_chart(figure_or_data=histogram_figure, use_container_width=True)

	# Display information about the last update.
	last_update = src.persistent_state.get_last_update()
	last_timestamp = last_update["timestamp"]
	last_block_number = last_update["block_number"]
	date_str = datetime.datetime.utcfromtimestamp(int(last_timestamp))
	streamlit.write(f"Last update timestamp: {date_str} UTC, last block: {last_block_number}.")


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)

	streamlit.set_page_config(
		layout="wide",
		page_title="DeRisk by Carmine Finance",
		page_icon="https://carmine.finance/assets/logo.svg",
	)

	if os.environ.get("CONTINUOUS_DATA_PROCESSING_PROCESS_RUNNING") is None:
		os.environ["CONTINUOUS_DATA_PROCESSING_PROCESS_RUNNING"] = "True"
		logging.info("Spawning data processing process.")
		data_processing_process = multiprocessing.Process(
			target=src.data_processing.process_data_continuously,
			daemon=True,
		)
		data_processing_process.start()
	main()