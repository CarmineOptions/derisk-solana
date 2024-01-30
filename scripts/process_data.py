import itertools
import logging
import sys

sys.path.append(".")

import src.amms
import src.persistent_state
import src.prices
import src.protocols.events
import src.protocols.kamino
import src.protocols.mango
import src.protocols.solend
import src.protocols.state
import src.visualizations.histogram
import src.visualizations.loans_table
import src.visualizations.main_chart
import src.visualizations.protocol_stats
import src.visualizations.settings



def process_data(states: dict[str, src.protocols.state.State]) -> dict[str, src.protocols.state.State]:
    logging.info("Started data processing.")
    # Process lending protocol events.
    max_block_number = 0
    max_timestamp = 0
    for protocol, state in states.items():
        # Load events from the database.
        events = src.protocols.events.get_events(protocol = protocol, start_block_number = state.last_block_number + 1)
        max_block_number = max(max_block_number, events["block_number"].max())
        max_timestamp = max(max_timestamp, events["timestamp"].max())
        logging.info("Loaded events for protocol = {}.".format(protocol))
        # Iterate over ordered events to obtain the final state of each user.
        for _, event in events.iterrows():
            state.process_event(event=event)
    logging.info("Updated lending protocol states.")

    # Gather data about liquidity in pools of swap AMMs.
    amms = src.amms.load_amm_data()
    logging.info("Loaded swap AMM data.")

	# Aggregate data for the main chart plotting liquidable debt against available liquidity.
    prices = src.prices.get_prices()
    for pair, state in itertools.product(src.visualizations.settings.PAIRS, states.values()):
        collateral_token, debt_token = pair.split("-")
        _ = src.visualizations.main_chart.get_main_chart_data(
            state=state,
            prices=prices,
            amms=amms,
            collateral_token=collateral_token,
            debt_token=debt_token,
            save_data=True,
        )
    logging.info("Computed main chart data.")

	# Compute and save histogram data.
    for state in states.values():
        _ = src.visualizations.histogram.get_histogram_data(state=state, prices=prices, save_data=True)
    logging.info("Computed histogram data.")

	# Prepara data for the table of individual loans. 
    individual_loan_stats = {}
    for protocol, state in states.items():
        individual_loan_stats[protocol] = src.visualizations.loans_table.get_loans_table_data(
			state=state,
			prices=prices,
			save_data=True,
		)
    logging.info("Prepared individual loans data.")

	# Compute stats comparing lending protocols.
    general_stats = src.visualizations.protocol_stats.get_general_stats(
		states=states,
		individual_loan_stats=individual_loan_stats,
		save_data=True,
	)
    supply_stats = src.visualizations.protocol_stats.get_supply_stats(states=states, prices=prices, save_data=True)
    _ = src.visualizations.protocol_stats.get_collateral_stats(states=states, save_data=True)
    debt_stats = src.visualizations.protocol_stats.get_debt_stats(states=states, save_data=True)
    _ = src.visualizations.protocol_stats.get_utilization_stats(
        general_stats=general_stats,
        supply_stats=supply_stats, 
        debt_stats=debt_stats, 
        save_data=True,
    )
    logging.info("Computed comparison stats.")

    last_update = {"timestamp": str(max_timestamp), "block_number": str(max_block_number)}
    src.persistent_state.upload_object_as_pickle(object = last_update, path=src.persistent_state.LAST_UPDATE_FILENAME)
    logging.info("Uploaded last update file.")

    logging.info("Ended data processing.")
    return states


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    process_data(
        states = {
            'Kamino': src.protocols.kamino.KaminoState(),
            'Mango': src.protocols.mango.MangoState(),
            'Solend': src.protocols.solend.SolendState(),
        },
    )
