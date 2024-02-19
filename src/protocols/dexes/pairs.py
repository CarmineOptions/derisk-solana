# Addresses of trading pair's for given AMM or OB-DEX

PAIRS: dict[str, dict[str, str]] = {
    'SOL/USDC' : {
        'PHOENIX': '4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg',
        'OPENBOOK': '8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6',
    },
    'SOL/USDT' : {
        'PHOENIX': '3J9LfemPBLowAJgpG3YdYPB9n6pUk7HEjwgS6Y5ToSFg',
    },
    'mSOL/SOL': {
        'PHOENIX': 'FZRgpfpvicJ3p23DfmZuvUgcQZBHJsWScTf2N2jK8dy6',
        'OPENBOOK': 'AYhLYoDr6QCtVb5n1M5hsWLG74oB8VEz378brxGTnjjn'
    },
    'mSOL/USDC': {
        'OPENBOOK': '9Lyhks5bQQxb9EyyX55NtgKQzpM4WK7JCmeaWuQ5MoXD'
    },
    'WETH/USDC': {
        'PHOENIX': 'Ew3vFDdtdGrknJAVVfraxCA37uNJtimXYPY4QjnfhFHH', # From Wormhole
    },
    'ETHpo/USDC': {
        'OPENBOOK': 'BbJgE7HZMaDp5NTYvRh5jZSkQPVDTU8ubPFtpogUkEj4',
    },
    'JUP/USDC' : {
        'PHOENIX': '2pspvjWWaf3dNgt3jsgSzFCNvMGPb7t8FrEYvLGjvcCe',
        'OPENBOOK': 'FbwncFP5bZjdx8J6yfDDTrCmmMkwieuape1enCvwLG33',
    },
    'JUP/SOL' :{
        'PHOENIX': 'Ge1Vb599LquMJziLbLTF5aR4icq8MZQxpmgNywvdPqjL',
    },
    'JUP/USDT' : {
        'PHOENIX': 'Ge1Vb599LquMJziLbLTF5aR4icq8MZQxpmgNywvdPqjL',
    },
    'wBTCpo/USDC': {
        'OPENBOOK': '3BAKsQd3RuhZKES2DGysMhjBdwjZYKYmxRqnSMtZ4KSN',
    },
    'MNGO/USDC' : {
        'OPENBOOK': '3NnxQvDcZXputNMxaxsGvqiKpqgPfSYXpNigZNFcknmD'
    },
    'USDT/USDC': {
        'OPENBOOK': 'B2na8Awyd7cpC59iEU43FagJAPLigr3AP3s38KM982bu'
    },
    'USDH/USDC': {
        'OPENBOOK': '6wD9zcNZi2VpvUB8dnEsF242Gf1tn6qNhLF2UZ3w9MwD'
    },
    'ORCA/USDC' : {
        'OPENBOOK': 'BEhRuJZiKwTdVTsGYjbHRh9RmGbKBtT6xo7yPqxLiSSY'
    },
    'EURC/USDC': {
        'PHOENIX': '5x91Aaegvx1JmW7g8gDfWqwb6kPF7CdNunqNoYCdLjk1',
        'OPENBOOK': 'H6Wvvx5dpt8yGdwsqAsz9WDkT43eQUHwAiafDvbcTQoQ'
    }
}

# NOTES: wETH  - from Wormhole bridge
# NOTES: ETHpo - from Portal bridge

def get_relevant_tickers(dex_identifier: str) -> dict[str, str]:
    '''
    Return relevant pairs for given Dex exchange identifier

    Parameters:
    - dex_identifier (str): String name for given DEX, under which the market
                            addresses are stored in TICKERS dict.

    Returns:
    - dict: Maps ticker to it's market address for given DEX.
    
    '''       
    return  {
        ticker: addresses[dex_identifier] 
        for ticker, addresses in PAIRS.items()
        if addresses.get(dex_identifier, False)
    }