import math

import pandas



# TODO: finish implementation once the db can be accessed
# def get_specific_loan_usd_amounts(loan: pandas.DataFrame) -> tuple[pandas.DataFrame, pandas.DataFrame]:
#     underlying_addresses_to_decimals = {
#         x.address: int(math.log10(x.decimal_factor))
#         for x in src.settings.TOKEN_SETTINGS.values()
#     }
#     underlying_symbols_to_addresses = {
#         x.symbol: x.address
#         for x in src.settings.TOKEN_SETTINGS.values()
#     }
#     prices = src.helpers.get_prices(token_decimals=underlying_addresses_to_decimals)
#     loan_collateral = loan['Collateral'].iloc[0]
#     loan_debt = loan['Debt'].iloc[0]
#     collateral_usd_amounts = pandas.DataFrame()
#     debt_usd_amounts = pandas.DataFrame()
#     for symbol, address in underlying_symbols_to_addresses.items():
#         collateral_usd_amount_symbol = pandas.DataFrame(
#             {
#                 'token': [symbol],
#                 'amount_usd': [loan_collateral[address] * prices[address]],
#             },
#         )
#         debt_usd_amount_symbol = pandas.DataFrame(
#             {
#                 'token': [symbol],
#                 'amount_usd': [loan_debt[address] * prices[address]],
#             },
#         )
#         collateral_usd_amounts = pandas.concat([collateral_usd_amounts, collateral_usd_amount_symbol])
#         debt_usd_amounts = pandas.concat([debt_usd_amounts, debt_usd_amount_symbol])
#     return collateral_usd_amounts, debt_usd_amounts