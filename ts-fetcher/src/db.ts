import pkg from "pg";
import { ClientConfig } from "pg";

const { Client } = pkg;

const config: ClientConfig = {
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
};

export const fetchTxSignatures = async () => {
  const client = new Client(config);
  await client.connect();
  const res = await client.query("SELECT * from tx_signatures;");
  console.log(res);
  await client.end();
};

export type Signature = {
  source: string;
  signature: string;
  slot: number;
  block_time: number;
  tx_raw: string;
};

export const writeTxSignatures = async (signatures: Signature[]) => {
  const client = new Client(config);
  await client.connect();
  try {
    await client.query("BEGIN");
    const insertQuery = `
      INSERT INTO tx_signatures(source, signature, slot, block_time, tx_raw)
      VALUES ($1, $2, $3, $4, $5)
    `;

    for (const { source, signature, slot, block_time, tx_raw } of signatures) {
      await client.query(insertQuery, [
        source,
        signature,
        slot,
        block_time,
        tx_raw,
      ]);
    }

    await client.query("COMMIT");
    console.log("WRITING SUCCESSFULL");
  } catch (e) {
    await client.query("ROLLBACK");
    console.log("WRITING FAILED");
    throw e;
  } finally {
    await client.end();
  }
};
