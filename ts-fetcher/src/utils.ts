import { Wallet } from '@project-serum/anchor';
import { Connection, Keypair } from '@solana/web3.js';

function getSolanaRpcUrl(): string {
  if (process.env.AUTHENTICATED_RPC_URL === undefined) {
    throw new Error("Solana RPC url ENV undefined");
  }
  return process.env.AUTHENTICATED_RPC_URL;
}

export const solana_connection = new Connection(getSolanaRpcUrl());
export const solana_wallet = new Wallet(Keypair.generate());

export function sleep(time_milliseconds: number) {
  return new Promise((resolve) => setTimeout(resolve, time_milliseconds));
}
