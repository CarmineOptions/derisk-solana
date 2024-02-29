
import { Keypair } from '@solana/web3.js';
import { solana_connection } from './utils.js';
import { AnchorProvider, Wallet } from '@coral-xyz/anchor';


import Senswap from '@sentre/senswap';
const sth = new Senswap(
    new AnchorProvider(
        solana_connection,
        new Wallet(Keypair.generate()),
        {}
    ),
    ''
);
