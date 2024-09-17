import math

import pandas



# TODO: finish implementation once the db can be accessed
# def get_bar_chart_figures(
#     supply_stats: pandas.DataFrame,
#     collateral_stats: pandas.DataFrame,
#     debt_stats: pandas.DataFrame,
# ) -> tuple[plotly.graph_objs.Figure, plotly.graph_objs.Figure, plotly.graph_objs.Figure]:
#     underlying_addresses_to_decimals = {
#         x.address: int(math.log10(x.decimal_factor))
#         for x in src.settings.TOKEN_SETTINGS.values()
#     }
#     underlying_symbols_to_addresses = {
#         x.symbol: x.address
#         for x in src.settings.TOKEN_SETTINGS.values()
#     }
#     prices = src.helpers.get_prices(token_decimals=underlying_addresses_to_decimals)
#     bar_chart_supply_stats = pandas.DataFrame()
#     bar_chart_collateral_stats = pandas.DataFrame()
#     bar_chart_debt_stats = pandas.DataFrame()
#     for column in supply_stats.columns:
#         if "Protocol" in column or "Total" in column:
#             continue
#         underlying_symbol = column.split(" ")[0]
#         underlying_address = underlying_symbols_to_addresses[underlying_symbol]
#         bar_chart_supply_stats[underlying_symbol] = supply_stats[column] * prices[underlying_address]
#         bar_chart_collateral_stats[underlying_symbol] = collateral_stats[underlying_symbol + ' collateral'] * prices[underlying_address]
#         bar_chart_debt_stats[underlying_symbol] = debt_stats[underlying_symbol + ' debt'] * prices[underlying_address]
#     bar_chart_supply_stats = bar_chart_supply_stats.T
#     bar_chart_collateral_stats = bar_chart_collateral_stats.T
#     bar_chart_debt_stats = bar_chart_debt_stats.T

#     supply_figure = plotly.graph_objs.Figure(
#         data = [
#             plotly.graph_objs.Bar(
#                 name = 'zkLend',
#                 x = bar_chart_supply_stats.index,
#                 y = bar_chart_supply_stats['zkLend'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fff7bc'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Alpha',
#                 x = bar_chart_supply_stats.index,
#                 y = bar_chart_supply_stats['Nostra Alpha'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fec44f'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Mainnet', 
#                 x = bar_chart_supply_stats.index, 
#                 y = bar_chart_supply_stats['Nostra Mainnet'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#d95f0e'),
#             ),
#         ],
#     )
#     supply_figure.update_layout(title_text = 'Supply (USD) per token')
#     collateral_figure = plotly.graph_objs.Figure(
#         data = [
#             plotly.graph_objs.Bar(
#                 name = 'zkLend', 
#                 x = bar_chart_collateral_stats.index, 
#                 y = bar_chart_collateral_stats['zkLend'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fff7bc'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Alpha', 
#                 x = bar_chart_collateral_stats.index, 
#                 y = bar_chart_collateral_stats['Nostra Alpha'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fec44f'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Mainnet', 
#                 x = bar_chart_collateral_stats.index, 
#                 y = bar_chart_collateral_stats['Nostra Mainnet'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#d95f0e'),
#             ),
#         ],
#     )
#     collateral_figure.update_layout(title_text = 'Collateral (USD) per token')
#     debt_figure = plotly.graph_objs.Figure(
#         data = [
#             plotly.graph_objs.Bar(
#                 name = 'zkLend', 
#                 x = bar_chart_debt_stats.index, 
#                 y = bar_chart_debt_stats['zkLend'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fff7bc'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Alpha', 
#                 x = bar_chart_debt_stats.index, 
#                 y = bar_chart_debt_stats['Nostra Alpha'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#fec44f'),
#             ),
#             plotly.graph_objs.Bar(
#                 name = 'Nostra Mainnet', 
#                 x = bar_chart_debt_stats.index, 
#                 y = bar_chart_debt_stats['Nostra Mainnet'],
#                 marker = plotly.graph_objs.bar.Marker(color = '#d95f0e'),
#             ),
#         ],
#     )
#     debt_figure.update_layout(title_text = 'Debt (USD) per token')
#     return supply_figure, collateral_figure, debt_figure