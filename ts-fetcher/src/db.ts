import pkg from "pg";
import { ClientConfig } from "pg";
const { Client } = pkg;

function getDBClientConfig(): ClientConfig {
  if (process.env.POSTGRES_USER === undefined) {
    throw new Error("PG User ENV undefined");
  }
  if (process.env.POSTGRES_PASSWORD === undefined) {
    throw new Error("PG Password ENV undefined");
  }
  if (process.env.POSTGRES_HOST === undefined) {
    throw new Error("PG HOST ENV undefined");
  }
  if (process.env.POSTGRES_DB === undefined) {
    throw new Error("PG DB ENV undefined");
  }
  // Return ClientConfig
  return {
    user: process.env.POSTGRES_USER,
    password: process.env.POSTGRES_PASSWORD,
    host: process.env.POSTGRES_HOST,
    database: process.env.POSTGRES_DB,
  };
}

export type AmmLiquidityEntry = {
  timestamp: number,
  dex: string;
  pair: string;
  market_address: string;
  token_x: number,
  token_y: number,
  token_x_decimals: number,
  token_y_decimals: number,
  additional_info: string,
};

export const writeAmmLiquidityEntries = async (signatures: AmmLiquidityEntry[]) => {
  const client = new Client(getDBClientConfig());
  await client.connect();
  try {
    await client.query("BEGIN");
    const insertQuery = `
      INSERT INTO amm_liquidity(timestamp, dex, pair, market_address, token_x, token_y, token_x_decimals, token_y_decimals, additional_info)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `;

    for (const { timestamp, dex, pair, market_address, token_x, token_y, token_x_decimals, token_y_decimals, additional_info } of signatures) {
      await client.query(insertQuery, [
        timestamp,
        dex,
        pair,
        market_address,
        token_x,
        token_y,
        token_x_decimals,
        token_y_decimals,
        additional_info
      ]);
    }

    await client.query("COMMIT");
  } catch (e) {
    await client.query("ROLLBACK");

    console.log("DB: Writing failed");
    console.log(e)

  } finally {
    await client.end();
  }
};
