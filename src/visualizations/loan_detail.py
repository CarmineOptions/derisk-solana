import pandas

import src.visualizations.main_chart



def get_specific_loan_usd_amounts(
	loan: pandas.DataFrame,
	tokens: list[src.visualizations.main_chart.Token],
	prices: dict[str, float],
) -> tuple[pandas.DataFrame, pandas.DataFrame]:
	symbols_to_addresses = {
		x.symbol: x.address
		for x in tokens
	}
	symbols_to_decimals = {
		x.symbol: x.decimals
		for x in tokens
	}

	collateral_usd_amounts = pandas.DataFrame()
	debt_usd_amounts = pandas.DataFrame()
	for token, amount in loan['Collaterals'].iloc[0].items():
		_, symbol = token.split(' ')
		symbol = symbol.replace('(', '').replace(')', '')
		address = symbols_to_addresses[symbol]
		decimals = symbols_to_decimals[symbol]

		collateral_usd_amount_symbol = pandas.DataFrame(
			{
				'token': [symbol],
				'amount_usd': [amount['amount'] * prices[address] / (10 ** decimals)],
			},
		)
		collateral_usd_amounts = pandas.concat([collateral_usd_amounts, collateral_usd_amount_symbol])
	for token, amount in loan['Debts'].iloc[0].items():
		_, symbol = token.split(' ')
		symbol = symbol.replace('(', '').replace(')', '')
		address = symbols_to_addresses[symbol]
		decimals = symbols_to_decimals[symbol]

		debt_usd_amount_symbol = pandas.DataFrame(
			{
				'token': [symbol],
				'amount_usd': [amount['rawAmount'] * prices[address] / (10 ** decimals)],
			},
		)
		debt_usd_amounts = pandas.concat([debt_usd_amounts, debt_usd_amount_symbol])
	return collateral_usd_amounts, debt_usd_amounts