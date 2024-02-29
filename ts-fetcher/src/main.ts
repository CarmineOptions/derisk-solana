

import { sleep } from './utils.js';

import { updateSaberLiqudity } from './saber.js';
import { updateInvariantLiqudity } from './invariant.js';
import { updateLifinityLiqudity } from './lifinity.js';
import { updateSentreLiqudity } from './sentre.js';

// Collect data every 5 minutes
const COLLECTION_INTERVAL_MILLISECONDS = 5 * 1 * 1000;

async function main() {

    while (true) {
        const start = Date.now();

        // Update Liquidity
        await updateInvariantLiqudity();
        await updateSaberLiqudity();
        await updateLifinityLiqudity();
        await updateSentreLiqudity();

        // Sleep until the end of collection interval
        const execution_time = Date.now() - start;
        const to_sleep = Math.max(0, COLLECTION_INTERVAL_MILLISECONDS - execution_time);

        await sleep(to_sleep);
    };

}

await main()
