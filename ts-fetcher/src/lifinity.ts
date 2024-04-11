
import { getParsedData, getMultipleAccounts } from '@lifinity/sdk-v2';
import { PublicKey } from '@solana/web3.js';
import { solana_connection } from './utils.js';
import { AmmLiquidityEntry, writeAmmLiquidityEntries } from './db.js';

const LIFINITY_IDENTIFIER = 'LIFINITY';
const RELEVANT_MARKETS = {
  'SOL-USDC': {
    amm: '86eq4kdBkUCHGdCC2SfcqGHRCBGhp2M89aCmuvvxaXsm',
    poolMint: 'FbQYjLEq1vNCszmxmxZDoFiy9fgyfdPxzt9Fu5zk5jJ4',
    feeAccount: 'FX5PBDb4nVTs4f9dSkUsj55rEYrCkBs9e7xZpDHqDeVM',
    oracleMainAccount: 'EPBJUVCmzvwkGPGcEuwKmXomfGt78Aozy6pj44x9xxDB',
    oracleSubAccount: 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    oraclePcAccount: 'CdgEC82BZAxFAJFpVPZ1RtnDr9AyH8KP9KygYhCb39eJ',
    poolCoinTokenAccount: '6Nij2pGdpgd6EutLAtdRwQoHaKKxhdNBi4zoLgd9Yuaq',
    poolCoinMint: 'So11111111111111111111111111111111111111112',
    poolPcTokenAccount: 'ELFYDkPYWBopH5Msm2cbA2ueByCXEKpzKWanv1kZC9L2',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 9,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 11
  },
  'SOL-USDC4': {
    amm: '71GHcjkwmtM7HSWBuqzjEp96prcNNwu1wpUywXiytREU',
    poolMint: 'AtpUocL94CzYR1tZouFpo76QeGsUMH7kSqicaTNy7Lvz',
    feeAccount: 'AczCqF64dSgTjmREcaCSB7eq561frTvSeJ7uLrW37QWG',
    oracleMainAccount: '6tnwoQiuLzPPeRqGeYVGmnGFoJo1dHapShP3Lexs83oG',
    oracleSubAccount: 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    oraclePcAccount: '978Mhamcn7XDkq21kvJWhUDPytJkYtkv8pqnXrUcpUxU',
    poolCoinTokenAccount: 'FzMQ1s9vQs4v6wyjVoVTFoDBJX2Qjr5ZsDGi1SA8a8hy',
    poolCoinMint: 'So11111111111111111111111111111111111111112',
    poolPcTokenAccount: 'BmKuiSYs91eP8cn8PTD2eue1vVmqfZq2ipg4WQknY23q',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 9,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 11
  },
  'SOL-USDT': {
    amm: 'EiEAydLqSKFqRPpuwYoVxEJ6h9UZh9tsTaHgs4f8b8Z5',
    poolMint: '2e6NAJy1qaKMq8PaswP2uzimMDvbr71Tbw38G6q9SNZ2',
    feeAccount: '2EVZT2cFMvbqE9nSVidYVkrSouKfudcKG6R8AKiXoSY9',
    oracleMainAccount: 'HTxTndHudFnfPuLpKFoFHCxpURzSqPtKDgBbUauj8EV5',
    oracleSubAccount: 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    oraclePcAccount: '3ZDBff7jeQaksmGvmkRix36rU159EBDjYiPThvV8QVZM',
    poolCoinTokenAccount: 'GUicRosQyLJCYG8hjYcbiGKAVAmT1puQTVmJjFxJmdMK',
    poolCoinMint: 'So11111111111111111111111111111111111111112',
    poolPcTokenAccount: 'D8F3PPxSuykAgyPPKwQdXDGGoRnUXzxowaheVJw5ATDC',
    poolPcMint: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
    poolCoinDecimal: 9,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 11
  },
  'stSOL-USDC': {
    amm: 'HPmjoycx8Vm99Tc9mUhRZWfJy4fsEZxVwhzP5nw7XeEy',
    poolMint: '2bykZULRJwHikmUzDFvQLvoMZWMmbrJR1ivCAwtPuXpG',
    feeAccount: '2kFxaaVnxWRHnVLjmy8DpaaNDPRVU6E9UefKs1P7Riu6',
    oracleMainAccount: 'EPBJUVCmzvwkGPGcEuwKmXomfGt78Aozy6pj44x9xxDB',
    oracleSubAccount: 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    oraclePcAccount: 'GCEitD54CdVVzUvvGVpB4rocCaY91LDHzeAVsD7bK8RZ',
    poolCoinTokenAccount: '35xntLJUTBzV8nSAPY2s1cdMdSNprccYhq7YSZae8gzy',
    poolCoinMint: '7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj',
    poolPcTokenAccount: 'AEyvfXM3pmQmAvijyWeGro25yrCXUWij5YZLhnK3sAKP',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 9,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 11
  },
  'mSOL-USDC': {
    amm: 'HvtYZ3e8JPhy7rm6kvWVB2jJUddyytkLcwTMSSnB7T3U',
    poolMint: '4CuuyBmdbYFUfXh2EHdJ7o2ZT246MR6xVU9vQD1yvDbx',
    feeAccount: '2WbmNq2pbwYzpkgdxFdZjcw5nfVBhmTaUbatMui3pQes',
    oracleMainAccount: '5v86kHPc9XGwiH9FBhnHt1cQUkPGs9yfzPr8D2ZqW6jH',
    oracleSubAccount: 'H6ARHf6YXhGYeQfUzQNGk6rDNnLBQKrenN712K4AQJEG',
    oraclePcAccount: 'F172vv3sZa6gEueEVXBi7A8mZRThUf1RC7JfWQ1JWdS7',
    poolCoinTokenAccount: '5z4wU1DidgndEk4oJPsKUDyQxRgZpVWrhwVnMAU6XTJE',
    poolCoinMint: 'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So',
    poolPcTokenAccount: 'Dz6KvVqCBeiGXMEXyqQv81QHLoEdui1BYGY4RL7F6cwq',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 9,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 11
  },
  'ETH-USDC': {
    amm: '7ru8qArudrbWUQyENQA2NATAp7UEwg7igVWcGw2NoGo8',
    poolMint: 'FV1hz2sZMFs3hWrMC7zvtPx8vx7tCWNaBpjrnXCSg4FA',
    feeAccount: 'FF51QyHAXenCVWmNtPCsRA4Jg85syALFEXPSEqi15fpu',
    oracleMainAccount: '4GR2HYRS5o9HLu2bE3ZyFiRn4e4eitqz3x9GykiQ2EmZ',
    oracleSubAccount: 'JBu1AL4obBcCMqKBBxhpWCNUt136ijcuMZLFvTP7iWdB',
    oraclePcAccount: '5JLNs3VxLVVJt8CCVyRhjgTwey8WCaU3VeKcT7SJCzXQ',
    poolCoinTokenAccount: 'HqFDLiQaVEmTzvEwjjDZYaxmDiGV6hcaBaALmpBDwbn9',
    poolCoinMint: '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
    poolPcTokenAccount: 'E7N9LdnEoJ2cHwCz3ZvXSiH99PQ7GBnGLaMQd8RJv1Gz',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 8,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 10
  },
  'RAY-USDC': {
    amm: '9YDpyJnTtD1sTNHPzMQxBqgmvxhoRksiswGKmq7WJ9cN',
    poolMint: '2NX49p9mnw2PVm34PNT9zyzSNTbs2Z3YQEXzc8239KHs',
    feeAccount: 'C4wKRTbut1dUHtQCV9J5qFbNWSSSsTRX7bW6uuaFuYxs',
    oracleMainAccount: '144FEiqLJXQ5FqmkQXnVcBne7C775K4TneTThxVstSc7',
    oracleSubAccount: 'AnLf8tVYCM816gmBjiy8n53eXKKEDydT5piYjjQDPgTB',
    oraclePcAccount: '4i7W3KmPXwqS5ws48ABPqwRXdUgZt7fJc6ptf7ExfE2B',
    poolCoinTokenAccount: 'CEnDczsUjDDoHwUJBXRABcG62GwKexwW6ZazaZBYeuk',
    poolCoinMint: '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
    poolPcTokenAccount: '5meuZ7hZwJpKWJTbpuu11Py3gifMRWUXqykuiYPhU8xJ',
    poolPcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    poolCoinDecimal: 6,
    poolPcDecimal: 6,
    poolMintDecimal: 9,
    pythBaseDecimal: 8
  },
}


async function getLifinityAmmLiquidityEntries(): Promise<AmmLiquidityEntry[]> {

  const relevantMarketsValues = Object.entries(RELEVANT_MARKETS);
  const pools: AmmLiquidityEntry[] = [];

  for (let i = 0; i < relevantMarketsValues.length; i++) {
    const [name, poolInfo] = relevantMarketsValues[i];

    const publicKeys = [
      new PublicKey(poolInfo.amm),
      new PublicKey(poolInfo.poolCoinTokenAccount),
      new PublicKey(poolInfo.poolPcTokenAccount),
    ];

    if (poolInfo.oracleMainAccount !== poolInfo.oracleSubAccount) {
      publicKeys.push(new PublicKey(poolInfo.oracleMainAccount));
      publicKeys.push(new PublicKey(poolInfo.oracleSubAccount));
    } else {
      publicKeys.push(new PublicKey(poolInfo.oracleMainAccount));
    }
    if (poolInfo.oracleSubAccount !== poolInfo.oraclePcAccount) {
      publicKeys.push(new PublicKey(poolInfo.oraclePcAccount));
    }

    const multipleInfo = await getMultipleAccounts(solana_connection, publicKeys);
    const data = getParsedData(multipleInfo, poolInfo);

    const entry: AmmLiquidityEntry = {
      timestamp: Math.floor(Date.now() / 1000),
      dex: LIFINITY_IDENTIFIER,
      market_address: poolInfo.amm,
      token_x_amount: data.coinBalance.toNumber(),
      token_y_amount: data.pcBalance.toNumber(),
      token_x_address: poolInfo.poolCoinMint,
      token_y_address: poolInfo.poolPcMint,
      additional_info: '{}',
    }

    pools.push(entry);
  }

  return pools;
}

export async function updateLifinityLiqudity() {
  try {
    const poolUpdates = await getLifinityAmmLiquidityEntries();
    await writeAmmLiquidityEntries(poolUpdates);

    console.log('Updated Lifinity Liquidity');
  } catch (e) {
    console.log("Encountered error while updating Lifinity liquidity: ");
    console.log(e);
  }
}
