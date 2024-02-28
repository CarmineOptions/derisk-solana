
import { sleep } from './utils.js';

import { updateSaberLiqudity } from './saber.js';
import { updateInvariantLiqudity } from './invariant.js';
import { updateLifinityLiqudity } from './lifinity.js';

// Collect data every 5 minutes
const COLLECTION_INTERVAL_MILLISECONDS = 5 * 60 * 1000;

async function main() {

    while (true) {
        var start = Date.now();

        // Update Liquidity
        await updateInvariantLiqudity();
        await updateSaberLiqudity();
        await updateLifinityLiqudity();

        // Sleep until the end of collection interval
        var execution_time = Date.now() - start;
        var to_sleep = Math.max(0, COLLECTION_INTERVAL_MILLISECONDS - execution_time);

        await sleep(to_sleep);
    };

}

await main()




