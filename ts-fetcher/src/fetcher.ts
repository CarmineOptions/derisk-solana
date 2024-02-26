import { Connection, PublicKey } from "@solana/web3.js";
import { getAmountOut, IAmountOut } from "@lifinity/sdk-v2";

const connection: Connection = new Connection(
  "https://api.mainnet-beta.solana.com"
);

export const runFetch = async () => {
  const amountIn: number = 1; // Input amount
  const fromMint: PublicKey = new PublicKey(
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
  );
  const toMint: PublicKey = new PublicKey(
    "So11111111111111111111111111111111111111112"
  );
  const slippage: number = 1; // Slippage (%)

  const res: IAmountOut = await getAmountOut(
    connection,
    amountIn,
    fromMint,
    toMint,
    slippage
  );

  console.log("amountIn: number =", res.amountIn);
  console.log("amountOut: number =", res.amountOut);
  console.log("amountOutWithSlippage: number =", res.amountOutWithSlippage);
  console.log("priceImpact: number =", res.priceImpact);
  console.log("fee: number =", res.fee);
  console.log("feePercent: number =", res.feePercent);
};
