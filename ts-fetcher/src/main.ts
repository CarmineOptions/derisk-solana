import { Signature, fetchTxSignatures, writeTxSignatures } from "./db.js";

const signatures: Signature[] = [
  {
    source: "ExampleSource",
    signature: "ExampleSignature",
    slot: 123,
    block_time: 4567890,
    tx_raw: "mytxdata",
  },
  {
    source: "ExampleSource",
    signature: "ExampleSignature",
    slot: 321,
    block_time: 12345,
    tx_raw: "yourtxdata",
  },
  {
    source: "ExampleSource",
    signature: "ExampleSignature",
    slot: 132,
    block_time: 67891,
    tx_raw: "histxdata",
  },
];

await writeTxSignatures(signatures);

console.log("WRITING DONE");

fetchTxSignatures();
