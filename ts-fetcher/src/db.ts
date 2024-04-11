import pkg from "pg";
import { ClientConfig } from "pg";
const { Client } = pkg;

function getDBClientConfig(): ClientConfig {
  if (!process.env.POSTGRES_USER) {
    throw new Error("PG User ENV undefined");
  }
  if (!process.env.POSTGRES_PASSWORD) {
    throw new Error("PG Password ENV undefined");
  }
  if (!process.env.POSTGRES_HOST) {
    throw new Error("PG HOST ENV undefined");
  }
  if (!process.env.POSTGRES_DB) {
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

const dbClientConfig = getDBClientConfig();

export type AmmLiquidityEntry = {
  timestamp: number,
  dex: string;
  market_address: string;
  token_x_amount: number,
  token_y_amount: number,
  token_x_address: string,
  token_y_address: string,
  additional_info: string,
};

export const writeAmmLiquidityEntries = async (signatures: AmmLiquidityEntry[]) => {
  const client = new Client(dbClientConfig);
  await client.connect();
  try {
    await client.query("BEGIN");
    const insertQuery = `
      INSERT INTO amm_liquidity(timestamp, dex, market_address, token_x_amount, token_y_amount, token_x_address, token_y_address, additional_info)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `;

    for (const { timestamp, dex, market_address, token_x_amount, token_y_amount, token_x_address, token_y_address, additional_info } of signatures) {
      await client.query(insertQuery, [
        timestamp,
        dex,
        market_address,
        token_x_amount,
        token_y_amount,
        token_x_address,
        token_y_address,
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
