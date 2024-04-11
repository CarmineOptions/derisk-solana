import { Keypair } from "@solana/web3.js";
import { solana_connection } from "./utils.js";
import { AnchorProvider, Wallet } from "@coral-xyz/anchor";
import SenswapLib from "@sentre/senswap/dist/lib/program.js";
import { AmmLiquidityEntry, writeAmmLiquidityEntries } from './db.js';

type MyObject = {
  default: any;
};

const SENTRE_IDENTIFIER = "SENTRE";
const Senswap = (SenswapLib as unknown as MyObject).default;

const sth = new Senswap(
  new AnchorProvider(solana_connection, new Wallet(Keypair.generate()), {}),
  "D3BBjqUdCYuP18fNvvMbPAZ8DpcRi4io2EsYHQawJDag"
);

const RELEVANT_MARKETS = {
    "SOL-USDC" : {"publicKey":"CT2QmamF6kBBDVbkg8WkvF5gnq6q8mDranPi21tdGeeL", "tokenXdecimals": 9, "tokenYdecimals": 6},
    // "SNTR-USDC": {"publicKey":"2gtDG2iYam6z4eCjx9yfBD7ayRXQGTDymjqQLiHqr7Z6", "tokenXdecimals": 9, "tokenYdecimals": 6},
    // "C98-USDC" : {"publicKey":"13Jn5xugRGjVorHWakzjvdZBMFwPLQniKHRoE6j4BMCC", "tokenXdecimals": 6, "tokenYdecimals": 6},
    // "ETH-USDC" : {"publicKey":"AzPdQteHNWLvgRtFQX2N9K2U14M7rwub4VjEeKhaSbuh", "tokenXdecimals": 8, "tokenYdecimals": 6}
}


async function getSentreAmmLiquidityEntries(): Promise<AmmLiquidityEntry[]> {

    const relevantMarketsValues = Object.entries(RELEVANT_MARKETS);
    const pools: AmmLiquidityEntry[] = [];

    for (let i = 0; i < relevantMarketsValues.length; i++) {
        const [_, poolInfo] = relevantMarketsValues[i];
        
        let pool = await sth.getPoolData(poolInfo['publicKey']);

        const entry: AmmLiquidityEntry = {
            timestamp: Math.floor(Date.now() / 1_000),
            dex: SENTRE_IDENTIFIER,
            market_address: poolInfo['publicKey'],
            token_x_amount: pool.reserves[0].toString(),
            token_y_amount: pool.reserves[1].toString(),
            token_x_address: pool.mints[0].toString(),
            token_y_address: pool.mints[1].toString(),
            additional_info: JSON.stringify({
                "tokenXweight": pool.weights[0].toNumber(),
                "tokenYweight": pool.weights[1].toNumber(),
            })
        };

        pools.push(entry);
    }
    return pools;
}

export async function updateSentreLiqudity() {
  try {
    const poolUpdates = await getSentreAmmLiquidityEntries();
    await writeAmmLiquidityEntries(poolUpdates);

    console.log('Updated Sentre Liquidity');
  } catch (e) {
    console.log("Encountered error while updating Sentre liquidity: ");
    console.log(e);
  }
}
