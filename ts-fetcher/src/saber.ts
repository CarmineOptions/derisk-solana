
import { loadExchangeInfoFromSwapAccount} from '@saberhq/stableswap-sdk';
import {  PublicKey } from '@solana/web3.js';
import { solana_connection } from './utils.js';

import { AmmLiquidityEntry, writeAmmLiquidityEntries } from './db.js';
const SABER_IDENTIFIER = 'SABER';
const RELEVANT_MARKETS = [
    {
        'name': 'stSOL-SOL',
        'swap_account': 'Lid8SLUxQ9RmF7XMqUA8c24RitTwzja8VSKngJxRcUa'
    },
    {
        'name': 'BTC-renBTC',
        'swap_account': 'BkwbeSfcX1h4thMDd7obGkHrPevf3QwgzJ4pCEqG18Lu'
    },
    {
        'name': 'USDT-USDC',
        'swap_account': 'YAkoNb6HKmSxQN9L8hiBE5tPJRsniSSMzND1boHmZxe'
    },
    {
        'name': 'UXD-USDC',
        'swap_account': 'KEN5P7p3asnb23Sw6yAmJRGvijfAzso3RqfyLAQhznt'
    },
    {
        'name': 'USDH-USDC',
        'swap_account': 'MARpDPs5A7XiyCWPNH8GsMWPLxmwNn9SBmKvPa9LzgA'
    },
    {
        'name': 'soETH-ETH',
        'swap_account': 'wrmcMSHFi3sWpAEy4rGDvQb3ezh3PhXoV2xNjgLBkKU'
    },
    {
        'name': 'ETH-aeWETH',
        'swap_account': 'ALLwa5WNZbvQsRKAqe1jdRGemdYQnW8E5k4msbRFcYtu'
    }
];


async function getSaberAmmLiquidityEntries(): Promise<AmmLiquidityEntry[]> {

    const pools: AmmLiquidityEntry[] = [];

    for (let i = 0; i < RELEVANT_MARKETS.length; i++) {
        const pool = RELEVANT_MARKETS[i];
        const exchangeInfo = await loadExchangeInfoFromSwapAccount(
            solana_connection,
            new PublicKey(pool.swap_account)
        );
        
        if (exchangeInfo === null) {
            throw new Error(`Saber: Exchange info null for pool ${pool}`);
        };

        const entry: AmmLiquidityEntry = {
            timestamp: Math.floor(Date.now() / 1000),
            dex: SABER_IDENTIFIER,
            pair: pool.name, 
            market_address: pool.swap_account,
            token_x: exchangeInfo?.reserves[0].amount.toU64().toNumber(),
            token_y: exchangeInfo?.reserves[1].amount.toU64().toNumber(),
            token_x_decimals: exchangeInfo?.reserves[0].amount.token.info.decimals,
            token_y_decimals: exchangeInfo?.reserves[1].amount.token.info.decimals,
            additional_info: '{}'
        };

        pools.push(entry);
    }
    
    return pools;
}


export async function updateSaberLiqudity() {
    try {
        const poolUpdates = await getSaberAmmLiquidityEntries();
        await writeAmmLiquidityEntries(poolUpdates);
        
        console.log('Updated Saber Liquidity');
    } catch (e) {
        console.log("Encountered error while updating Saber liquidity: ");
        console.log(e);
    } 
}
