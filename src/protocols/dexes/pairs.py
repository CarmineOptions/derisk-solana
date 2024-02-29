""" 
Module contains addresses of trading pairs for given AMM or CLOB.
"""

PAIRS: dict[str, dict[str, str]] = {
    "SOL/USDC": {
        "PHOENIX": "4DoNfFBfF7UokCC2FQzriy7yHK6DY6NVdYpuekQ5pRgg",
        "OPENBOOK": "8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6",
    },
    "SOL/USDT": {
        "PHOENIX": "3J9LfemPBLowAJgpG3YdYPB9n6pUk7HEjwgS6Y5ToSFg",
    },
    "mSOL/SOL": {
        "PHOENIX": "FZRgpfpvicJ3p23DfmZuvUgcQZBHJsWScTf2N2jK8dy6",
        "OPENBOOK": "AYhLYoDr6QCtVb5n1M5hsWLG74oB8VEz378brxGTnjjn",
    },
    "mSOL/USDC": {"OPENBOOK": "9Lyhks5bQQxb9EyyX55NtgKQzpM4WK7JCmeaWuQ5MoXD"},
    "WETH/USDC": {
        "PHOENIX": "Ew3vFDdtdGrknJAVVfraxCA37uNJtimXYPY4QjnfhFHH",  # From Wormhole
    },
    "ETHpo/USDC": {
        "OPENBOOK": "BbJgE7HZMaDp5NTYvRh5jZSkQPVDTU8ubPFtpogUkEj4",
    },
    "JUP/USDC": {
        "PHOENIX": "2pspvjWWaf3dNgt3jsgSzFCNvMGPb7t8FrEYvLGjvcCe",
        "OPENBOOK": "FbwncFP5bZjdx8J6yfDDTrCmmMkwieuape1enCvwLG33",
    },
    "JUP/SOL": {
        "PHOENIX": "Ge1Vb599LquMJziLbLTF5aR4icq8MZQxpmgNywvdPqjL",
    },
    "JUP/USDT": {
        "PHOENIX": "Ge1Vb599LquMJziLbLTF5aR4icq8MZQxpmgNywvdPqjL",
    },
    "wBTCpo/USDC": {
        "OPENBOOK": "3BAKsQd3RuhZKES2DGysMhjBdwjZYKYmxRqnSMtZ4KSN",
    },
    "MNGO/USDC": {"OPENBOOK": "3NnxQvDcZXputNMxaxsGvqiKpqgPfSYXpNigZNFcknmD"},
    "USDT/USDC": {"OPENBOOK": "B2na8Awyd7cpC59iEU43FagJAPLigr3AP3s38KM982bu"},
    "USDH/USDC": {"OPENBOOK": "6wD9zcNZi2VpvUB8dnEsF242Gf1tn6qNhLF2UZ3w9MwD"},
    "ORCA/USDC": {"OPENBOOK": "BEhRuJZiKwTdVTsGYjbHRh9RmGbKBtT6xo7yPqxLiSSY"},
    "EURC/USDC": {
        "PHOENIX": "5x91Aaegvx1JmW7g8gDfWqwb6kPF7CdNunqNoYCdLjk1",
        "OPENBOOK": "H6Wvvx5dpt8yGdwsqAsz9WDkT43eQUHwAiafDvbcTQoQ",
    },
    "PYTH/USDC": {
        "PHOENIX": "2sTMN9A1D1qeZLF95XQgJCUPiKe5DiV52jLfZGqMP46m",
        "OPENBOOK": "EA1eJqandDNrw627mSA1Rrp2xMUvWoJBz2WwQxZYP9YX",
    },
    "BONK/USDC": {
        "PHOENIX": "GBMoNx84HsFdVK63t8BZuDgyZhSBaeKWB4pHHpoeRM9z",
        'OPENBOOK': "7tV5jsyNUg9j1AARv56b7AirdpLBecibRXLEJtycEgpP"
    },
    "BONK/SOL": {
        "PHOENIX": "FicF181nDsEcasznMTPp9aLa5Rbpdtd11GtSEa1UUWzx",
        "OPENBOOK": "Hs97TCZeuYiJxooo3U73qEHXg3dKpRL4uYKYRryEK9CF",
    },
    "WIF/USDC": {
        "PHOENIX": "6ojSigXF7nDPyhFRgmn3V9ywhYseKF9J32ZrranMGVSX",
        "OPENBOOK":"2BtDHBTCTUxvdur498ZEcMgimasaFrY5GzLv8wS8XgCb"
    },
    "JitoSOL/USDC": {
        "PHOENIX": "5LQLfGtqcC5rm2WuGxJf4tjqYmDjsQAbKo2AMLQ8KB7p",
        "OPENBOOK": "DkbVbMhFxswS32xnn1K2UY4aoBugXooBTxdzkWWDWRkH",
    },
    "DUAL/USDC": {"OPENBOOK": "H6rrYK3SUHF2eguZCyJxnSBMJqjXhUtuaki6PHiutvum"},
    "RAY/USDC": {"OPENBOOK": "DZjbn4XC8qoHKikZqzmhemykVzmossoayV9ffbsUqxVj"},
    "stSOL/USDC": {"OPENBOOK": "JCKa72xFYGWBEVJZ7AKZ2ofugWPBfrrouQviaGaohi3R"},
    "LDO/USDC": {"OPENBOOK": "BqApFW7DwXThCDZAbK13nbHksEsv6YJMCdj58sJmRLdy"},
    "stSOL/SOL": {"OPENBOOK": "GoXhYTpRF4vs4gx48S7XhbaukVbJXVycXimhGfzWNGLF"},
    "JitoSOL/SOL": {"OPENBOOK": "G8KnvNg5puzLmxQVeWT2cRHCm1XmurbWGG9B8Bze6mav"},
    "HNT/USDC": {"OPENBOOK": "CK1X54onkDCqVnqY7hnvhcT7EosnjiLTwPBXAMLxkA2A"},
    "bSOL/USDC": {"OPENBOOK": "ARjaHVxGCQfTvvKjLd7U7srvk6orthZSE6uqWchCczZc"},
    "bSOL/SOL": {"OPENBOOK": "6QNusiQ1g7fKierMQhNeAJxfLXomfcAX3tGRMwxfESsw"},
    "KIN/USDC": {"OPENBOOK": "4WeAXG1V8QTtt3T9ao6LkQa8m1AuwRcY8YLvVcabiuby"},
    "CHAI/USDC": {"OPENBOOK": "7S2fEFvce5n9hGpjp9jd8JRfuBngcDJfykygeqqzEwmq"},
    "ALL/USDC": {"OPENBOOK": "EN41nj1uHaTHmJJLPTerwVu2P9r5G8pMiNvfNX5V2PtP"},
    "RLB/USDC": {"OPENBOOK": "72h8rWaWwfPUL36PAFqyQZU8RT1V3FKG7Nc45aK89xTs"},
    "CROWN/USDC": {"OPENBOOK": "HDwpKCNpB9JvcGrZv6TWcXjFvzxxfzq7ci6kQ1Kv8FMY"},
    "TBTC/USDC": {"OPENBOOK": "6nh2KwhGF8Tott22smj2E3G1R15iXhBrL7Lx6vKgdPFK"},
    "GUAC/USDC": {"OPENBOOK": "63XwffQkMcNqEacDNhixmBxnydkRE3uigV7VoLNfqh9k"},
    "NOS/USDC": {"OPENBOOK": "9LezACAkFsv78P7nBJEzi6QeF9h1QF8hGx2LRN7u9Vww"},
    "NEON/USDC": {"OPENBOOK": "Fb5BfdB7zk2zfWfqgpRtRQbYSYERASsBjz213FaT461F"},
    "SLCL/USDC": {"OPENBOOK": "AuqKXU1Nb5XvRxr5A4vRBLnnSJrdujNJV7HWsfj4KBWS"},
    "JTO/USDC": {"OPENBOOK": "H87FfmHABiZLRGrDsXRZtqq25YpARzaokCzL1vMYGiep"},
    "SAMO/USDC": {"OPENBOOK": "E5AmUKMFgxjEihVwEQNrNfnri5EexYHSBC4HkicVtfxG"},
    "CORN/USDC": {"OPENBOOK": "2mBnnBywAuMwH5FhH27UUFyDGk7J77m5LcKK4VtmwJQi"},
    "TBTC/wBTCpo": {"OPENBOOK": "3rQH87K3UfrDjbjSktHy7EwQHvX4BoRu3Py52D25gKSS"},
    "RENDER/USDC": {"OPENBOOK": "2m7ZLEKtxWF29727DSb5D91erpXPUY1bqhRWRC3wQX7u"},
    "MNDE/USDC": {"OPENBOOK": "CC9VYJprbxacpiS94tPJ1GyBhfvrLQbUiUSVMWvFohNW"},
    "JLP/USDC": {"OPENBOOK": "ASUyMMNBpFzpW3zDSPYdDVggKajq1DMKFFPK1JS9hoSR"},
    "GECKO/USDC": {"OPENBOOK": "8QCdRwLp5CX2XYVaKX3GFxsbc8n7M2xEtMXyAa8tL7r3"},
    "WEN/USDC": {"OPENBOOK": "2oxZZ3YXaVhbZmtzagGooewBAofyVbBTzayAD9UR1eBh"},
    "MOUTAI/USDC": {"OPENBOOK": "74fKpZ1NFfusLacyVzQdMXXawe9Dr1Kz8Yw1cw12QQ3y"},
    "BLZE/USDC": {"OPENBOOK": "GFJjJmm7jTDb7WEM4TkYdA9eAEeJGK1t73tcdDNeZLGT"},
    "GOFX/USDC": {"OPENBOOK": "9FjM1wHvGg2ZZaB3XyRsYELoQE7iD6uwHXizQUDKRYff"},
    "ELON/USDC": {"OPENBOOK": "CDm1Uaos4vWPXezgEobUarGJ6ddKCywvFp8XLcNSqzU9"},
    "STEP/USDC": {"OPENBOOK": "CCepXEQxo8eTqCGtRHXrSnZdhCEQjQeEW3M85AH9skMJ"},
}


def get_relevant_tickers(dex_identifier: str) -> dict[str, str]:
    """
    Return relevant pairs for given Dex exchange identifier

    Parameters:
    - dex_identifier (str): String name for given DEX, under which the market
                            addresses are stored in TICKERS dict.

    Returns:
    - dict: Maps ticker to it's market address for given DEX.

    """
    return {
        ticker: addresses[dex_identifier]
        for ticker, addresses in PAIRS.items()
        if addresses.get(dex_identifier, False)
    }
