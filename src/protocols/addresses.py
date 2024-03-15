# Addresses of accounts for which we gather transactions.
# Source: https://docs.solend.fi/Architecture/addresses.
SOLEND_ADDRESS: str = 'So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo'
# Source: https://github.com/blockworks-foundation/mango-v4.
MANGO_ADDRESS: str = '4MangoMjqJ2firMokCjjGgoK8d4MXcrgL7XJaL3w6fVg'
# Source: https://docs.kamino.finance/build-on-kamino/sdk-and-smart-contracts.
KAMINO_ADDRESS: str = 'KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD'
# Source: https://github.com/mrgnlabs/marginfi-v2/tree/main
MARGINFI_ADDRESS: str = 'MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA'

ALL_ADDRESSES: dict[str, str] = {
	'Kamino': KAMINO_ADDRESS,
	'Mango': MANGO_ADDRESS,
	'Solend': SOLEND_ADDRESS,
	'MarginFi': MARGINFI_ADDRESS
}
