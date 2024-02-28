
import { PublicKey } from '@solana/web3.js';
import { calculatePoolLiquidity } from '@invariant-labs/sdk/lib/utils.js';

import { AmmLiquidityEntry, writeAmmLiquidityEntries } from './db.js';
import { Market, Network } from '@invariant-labs/sdk';
import { solana_wallet, solana_connection } from './utils.js';

const INVARIANT_IDENTIFIER = 'INVARIANT';
const RELEVANT_MARKETS = [{
    "publicKey": "BRt1iVYDNoohkL1upEb8UfHE8yji6gEDAmuN9Y4yekyc",
    "pairName": "USDC-USDT",
    "tokenX": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenY": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "tokenXdecimals": 6,
    "tokenYdecimals": 6,
    "tokenXReserve": "AdQtahZZ8x9LV8aKHfu4YuWLfzhhNUMeZz6ZiprC8qwv",
    "tokenYReserve": "Ef2mXsg83FeXsV7qmGChGFfod6uGAA5qQ4LnqdL3DRow",
    "tickSpacing": 1,
},
{
    "publicKey": "FeKSMTD9Z22kdnMLeNWAfaTXydbhVixUPcfZDW3QS1X4",
    "pairName": "SOL-mSOL",
    "tokenX": "So11111111111111111111111111111111111111112",
    "tokenY": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "tokenXdecimals": 9,
    "tokenYdecimals": 9,
    "tokenXReserve": "6xwtCxEhukSieXS62GcpanATyvemUxRxn5i2abnFVZq6",
    "tokenYReserve": "ABZ4vFHVwP4vS1pobTMsRwY9JnaZFms6rhKk4scEwrjY",
    "tickSpacing": 1,
},
{
    "publicKey": "EWZW9aJmY2LX6ZyV5RU8waHWKF1aGaxzbuBuRQp6G4j",
    "pairName": "wBTC-USDC", // Sollet wBTC
    "tokenX": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
    "tokenY": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenXdecimals": 6,
    "tokenYdecimals": 6,
    "tokenXReserve": "CPRZ6BB8AShFhSfAMcv5rdpfqUXcFS3cHavkPy3FTK9Q",
    "tokenYReserve": "CRr2mE2AWhWSZRh5hxgeyQRRhnWjmvGtNSybuDCidTtK",
    "tickSpacing": 5,
},
{
    "publicKey": "6rvpVhL9fxm2WLMefNRaLwv6aNdivZadMi56teWfSkuU",
    "pairName": "USDC-wSOL",
    "tokenX": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenY": "So11111111111111111111111111111111111111112",
    "tokenXdecimals": 6,
    "tokenYdecimals": 9,
    "tokenXReserve": "GK9QHeWnAmyZkAZnWbzbzp6kEHT5eJKgKPkn2JyvpVnF",
    "tokenYReserve": "f6nwMTRpKTCVmRhGUbjfJPEBeXaaDUCvUUQh1941e4a",
    "tickSpacing": 5,
},
{
    "publicKey": "2c1yGddbVmbiGR6pAX16xUkeMUwcYC1kxr3LZaLmuC8u",
    "pairName": "poETH-USDC",
    "tokenX": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs",
    "tokenY": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenXdecimals": 8,
    "tokenYdecimals": 6,
    "tokenXReserve": "5EmuYt7z3sizK6J5qoJzznL97F11CeptTBL3TsJAHMEX",
    "tokenYReserve": "Ckq22eUU9UZxJ5N8DKaSNfdQPXBPZEPVEXeBWuDqDLCz",
    "tickSpacing": 10,
},
{
    "publicKey": "2SgUGxYDczrB6wUzXHPJH65pNhWkEzNMEx3km4xTYUTC",
    "pairName": "USDC-wSOL",
    "tokenX": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenY": "So11111111111111111111111111111111111111112",
    "tokenXdecimals": 6,
    "tokenYdecimals": 9,
    "tokenXReserve": "3f9kSZg8PPJ6NkLwVdXeff16ZT1XbkmT5eaQCqUnpDWx",
    "tokenYReserve": "4maNZQtYFA1cdB55aLS321dxwdH1Y8NWaH4qiMedKpTZ",
    "tickSpacing": 1,
},
{
    "publicKey": "FwiuNR91xfiUvWiBu4gieK4SFmh9qjMhYS9ebyYJ8PGj",
    "pairName": "USDC-USDH",
    "tokenX": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenY": "USDH1SM1ojwWUga67PGrgFWUHibbjqMvuMaDkRJTgkX",
    "tokenXdecimals": 6,
    "tokenYdecimals": 6,
    "tokenXReserve": "5TqGGXetx6MeFnrpSWnfa7S2KPo6K7vNTzYockd5MTo6",
    "tokenYReserve": "EBq8j6ZtD9ZH1So51gm4ktn8aW3WEnS7gQ5ALPFJjgHN",
    "tickSpacing": 1
},
{
    "publicKey": "5dX3tkVDmbHBWMCQMerAHTmd9wsRvmtKLoQt6qv9fHy7",
    "pairName": "USDC-USDT",
    "tokenX": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "tokenY": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "tokenXdecimals": 6,
    "tokenYdecimals": 6,
    "tokenXReserve": "4go7nr5sVMTDztb5a7sF92HoeasDnpadspuHR9ACsfw6",
    "tokenYReserve": "9J1h43E5XFdMpYsWsqK8q8SFyXPAt8dHm52enfjWhSJt",
    "tickSpacing": 1,
}]

async function getInvariantMarket(): Promise<Market> {
    return await Market.build(
        Network.MAIN,
        solana_wallet,
        solana_connection
    );
}


async function getInvariantAmmLiquidityEntries(): Promise<AmmLiquidityEntry[]> {

    var pools: AmmLiquidityEntry[] = [];
    const market = await getInvariantMarket();

    for (let i = 0; i < RELEVANT_MARKETS.length; i++) {
        let pool = RELEVANT_MARKETS[i];
        const pool_pubkey = new PublicKey(pool.publicKey)
        const pool_struct = await market.getPoolByAddress(pool_pubkey);
        const pool_positions = await market.getPositionsForPool(pool_pubkey);

        const { x, y } = calculatePoolLiquidity(pool_struct, pool_positions);

        const entry: AmmLiquidityEntry = {
            timestamp: Math.floor(Date.now() / 1000),
            dex: INVARIANT_IDENTIFIER,
            pair: pool.pairName,
            market_address: pool.publicKey,
            token_x: x.toNumber(),
            token_y: y.toNumber(),
            token_x_decimals: pool.tokenXdecimals,
            token_y_decimals: pool.tokenYdecimals,
            additional_info: '{}',
        };

        pools.push(entry);
    }

    return pools;
}

export async function updateInvariantLiqudity() {
    try {
        var poolUpdates = await getInvariantAmmLiquidityEntries();
        await writeAmmLiquidityEntries(poolUpdates);

        console.log('Updated Invariant Liquidity');
    } catch (e) {
        console.log("Encountered error while updating Invariant liquidity: ");
        console.log(e);
    }
}

