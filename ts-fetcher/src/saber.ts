
import { loadExchangeInfoFromSwapAccount} from '@saberhq/stableswap-sdk';
import {  PublicKey } from '@solana/web3.js';
import { solana_connection } from './utils.js';

import { AmmLiquidityEntry, writeAmmLiquidityEntries } from './db.js';
const SABER_IDENTIFIER = 'SABER';
const RELEVANT_MARKETS = [
    {
        'name': 'USDT-USDC',
        'swap_account': 'YAkoNb6HKmSxQN9L8hiBE5tPJRsniSSMzND1boHmZxe',
        'tokenXmint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
        'tokenYmint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    },
    {
        'name': 'stSOL-SOL',
        'swap_account': 'Lid8SLUxQ9RmF7XMqUA8c24RitTwzja8VSKngJxRcUa',
        'tokenXmint': '7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj',
        'tokenYmint': 'So11111111111111111111111111111111111111112',
    },
    {
        'name': 'BTC-renBTC',
        'swap_account': 'BkwbeSfcX1h4thMDd7obGkHrPevf3QwgzJ4pCEqG18Lu',
        'tokenXmint': '9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E',
        'tokenYmint': 'CDJWUqTcYTVAKXAVXoQZFes5JUFc7owSeq7eMQcDSbo5',
    },
    {
        'name': 'UXD-USDC',
        'swap_account': 'KEN5P7p3asnb23Sw6yAmJRGvijfAzso3RqfyLAQhznt',
        'tokenXmint': '7kbnvuGBxxj8AG9qp8Scn56muWGaRaFqxg1FsRp3PaFT',
        'tokenYmint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    },
    {
        'name': 'USDH-USDC',
        'swap_account': 'MARpDPs5A7XiyCWPNH8GsMWPLxmwNn9SBmKvPa9LzgA',
        'tokenXmint': 'USDH1SM1ojwWUga67PGrgFWUHibbjqMvuMaDkRJTgkX',
        'tokenYmint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    },
    {
        'name': 'soETH-ETH',
        'swap_account': 'wrmcMSHFi3sWpAEy4rGDvQb3ezh3PhXoV2xNjgLBkKU',
        'tokenXmint': '2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk',
        'tokenYmint': '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
    },
    {
        'name': 'ETH-aeWETH',
        'swap_account': 'ALLwa5WNZbvQsRKAqe1jdRGemdYQnW8E5k4msbRFcYtu',
        'tokenXmint': '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
        'tokenYmint': 'AaAEw2VCw1XzgvKB8Rj2DyK2ZVau9fbt2bE8hZFWsMyE',
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
            market_address: pool.swap_account,
            token_x_amount: exchangeInfo?.reserves[0].amount.toU64().toNumber(),
            token_y_amount: exchangeInfo?.reserves[1].amount.toU64().toNumber(),
            token_x_address: pool.tokenXmint,
            token_y_address: pool.tokenYmint,
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
