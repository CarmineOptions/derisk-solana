# DeRisk Solana

Monorepo with components required for the implementation of DeRisk on Solana.

## Project Setup

The setup consists of:

1. [`Database`] Creating an empty database for raw data.
2. [`Raw Data Fetching`] Running a script that feeds the database with raw data.
3. [`API`] Creating an API for fetching the raw data from the database.
4. [`Raw Data Processing`] Running a script which processes the raw data.
5. [`Frontend`] Running a frontend with visualizations of the processed data.

Each step is described in detail below.

The relevant commit for which the following commands for running individual containers were tested is `3d40c20cca42425f2d2584cae6592ab75ee08eab`.

### Database

The project uses _Postgres 15_ as database. The schema can be found in `db/schema.sql`. To start the database run:

```sh
docker build -t db -f Dockerfile.db .
export POSTGRES_USER=<username>
export POSTGRES_PASSWORD=<password>
# default port for Postgres is 5432
docker run -p 5432:5432 db
```

### Raw Data Fetching

For fetching raw data, the following ENV variables are needed:

- `POSTGRES_USER` name of the database user
- `POSTGRES_PASSWORD` database user's password
- `POSTGRES_HOST` host address, IP address or DNS of the database
- `POSTGRES_DB` database name
- `AUTHENTICATED_RPC_URL` URL of the node provider, includingthe RPC token, used to initialize the Solana client
- `RATE_LIMIT` maximum number of RPC calls allowed per second

Then, run the following commands:

```sh
docker build -t raw-data-fetching -f Dockerfile.raw-data-fetching .
docker run -e POSTGRES_USER=<username> -e POSTGRES_PASSWORD=<password> -e POSTGRES_HOST=<host> -e POSTGRES_DB=<db_name> -e AUTHENTICATED_RPC_URL=<rpc_url> -e RATE_LIMIT=<rate_limit> raw-data-fetching
```

The data collection works as follows:

1. Signatures of transactions are fetched in batches and stored in the database. 
2. For each slot containing at least 1 signature, all transactions are fetched, but only those which match the previously saved signatures are kept and saved in the database.

The data is being fetched from the newest transactions at the time when the script is run (`T0`). When the available history preceding `T0` is stored in the database, the process starts again at time `T1`, fetching all data between `T0` and `T1`. With the rate limit set high enough, the process approaches a state when the script feeds the database with nearly real-time data. If restarted, the fetching of the data continues from the last transaction stored in the database. 

### CLOB DEXes

For updating CLOB DEXes data following environmental variables are required:

- `POSTGRES_USER` name of the database user
- `POSTGRES_PASSWORD` database user's password
- `POSTGRES_HOST` host address, IP address or DNS of the database
- `POSTGRES_DB` database name
- `AUTHENTICATED_RPC_URL` Solana rpc url

Then, run the following commands:

```sh
docker build --file ./Dockerfile.ob-liq-fetcher -t ob-liq-fetcher .
docker run -d -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_HOST=$POSTGRES_HOST -e POSTGRES_DB=$POSTGRES_DB -e AUTHENTICATED_RPC_URL=$AUTHENTICATED_RPC_URL ob-liq-fetcher
```

Data collected from following CLOBs:
- [Phoenix](https://www.phoenix.trade/), [SDK](https://github.com/Ellipsis-Labs/phoenix-sdk)
- [OpenBook](https://openbookdex.com/), [SDK](https://github.com/openbook-dex/resources)
- [GooseFX](https://www.goosefx.io/), [SDK](https://docs.goosefx.io/developer-resources/perpetual-dex-sdks/python-sdk)

#### Database Schema
The orderbook_liquidity table is structured in a following way:

- `timestamp`: Stores time of the data record.
- `dex`: Identifies the DEX from which the orderbook data were collected.
- `pair`: Represents the token pair of the liquidity pool in following format `<symbol_x>/<symbol_y>` e.g. `"SOL/USDC"`.
- `market_address`: Holds the market's pubkey.
- `bids` and `asks`: Hold lists of two sized tuples where first entry in the tuple is price level and the second entry is the amount of liquidity on given level.

### AMMs

For updating AMMs' pools data following environmental variables are required:

- `POSTGRES_USER` name of the database user
- `POSTGRES_PASSWORD` database user's password
- `POSTGRES_HOST` host address, IP address or DNS of the database
- `POSTGRES_DB` database name
- `AUTHENTICATED_RPC_URL` Solana rpc url

Then, run the following commands:

```sh
docker build --file ./Dockerfile.update-amm-pools -t amms .
docker run -d --name amms -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_HOST=$POSTGRES_HOST -e POSTGRES_DB=$POSTGRES_DB amms
```

Note that updating of few AMMs' pools is done with their corresponding TypeScript SDK. These are updated in separate Docker container, which is run followingly: 

```sh
docker build --file ./Dockerfile.ts-fetching -t ts-fetcher .
docker run -d -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_HOST=$POSTGRES_HOST -e POSTGRES_DB=$POSTGRES_DB -e AUTHENTICATED_RPC_URL=$AUTHENTICATED_RPC_URL ts-fetcher
```

Data collected from following DEXes:
- [Orca](https://www.orca.so/), [API](https://orca-so.gitbook.io/orca-developer-portal/whirlpools/interacting-with-the-protocol/orca-whirlpools-parameters#api-endpoint-for-orca-ui-supported-whirlpools)
- [Raydium](https://raydium.io/), [API](https://api.raydium.io/v2/main/pairs)
- [Meteora](https://www.meteora.ag/), [API](https://docs.meteora.ag/dynamic-pools-integration/dynamic-pool-api/pool-info)
- [LIFINITY](https://lifinity.io/), [SDK](https://www.npmjs.com/package/@lifinity/sdk-v2)
- [Sentre](https://sentre.io/), [SDK](https://docs.senswap.sentre.io/)
- [Saber](https://app.saber.so), [SDK](https://docs.saber.so/developing/sdks/saber-common)
- [Invariant](https://invariant.app/swap), [SDK](https://docs.invariant.app/docs/solana/introduction)

Data Collection Strategy:

The data collection process involves querying each DEX's first-party API for current pool statuses. This process is automated through a scheduled task that runs the above Docker container, ensuring data freshness. The approach is as follows:

1) Initialization: On startup, the Docker container queries the DEX APIs to fetch the initial state of all liquidity pools.
2) Continuous Update: The container polls the APIs every 300 seconds to capture any changes in pools' liquidity.
3) Data Transformation: Before insertion into the database, data undergoes normalization to fit the amm_liquidity table schema, ensuring consistency across different DEX sources.

For LIFINITY, Sentre, Saber and Invariant, the data collection is done directly using on-chain data through their respective SDK. This is done in regular intervals in a Docker container. Generally speaking, the process is very similar to previous one:

1) Initialization: On startup, the Docker container fetches initial on-chain state of all liquidity pools.
2) Continuous Update: The container fetches the liqduity every 300 seconds to capture any changes in pools' liquidity.
3) Data Transformation: Before insertion into the database, data undergoes normalization to fit the amm_liquidity table schema, ensuring consistency across different DEX sources.

#### Database Schema

The amm_liquidity table is structured to accommodate data from multiple DEXes efficiently. Key fields include:

- `timestamp`: Stores time of the data record.
- `dex`: Identifies the DEX from which the pool data was sourced, e.g., Orca, Raydium, Meteora.
- `pair`: Represents the token pair of the liquidity pool in following format `<symbol_x>-<symbol_y>` e.g. `"SOL-USDC"`.
- `market_address`: Holds the pool's pubkey.
- `token_x` and `token_y`: Capture the amounts of the tokens in the liquidity pool.
- `token_x_decimals` and `token_y_decimals`: Define the decimal precision for each token in the pair.
- `additional_info`: Additional info provided by DEXes.

### API

The API exposes an endpoint that allows access to data in the database.

##### Endpoints

Currently, there is only one endpoint:

- `/v1/get-transactions?start_block_number=<start>&end_block_number=<end>` returns transactions within the block range

##### Deployment

To run the API, build and run the Docker image with relevant ENV variables.

- `POSTGRES_USER` name of the database user
- `POSTGRES_PASSWORD` database user's password
- `POSTGRES_HOST` host address, IP address or DNS of the database
- `POSTGRES_DB` database name

```sh
docker build -t api -f Dockerfile.api .
docker run -e POSTGRES_USER=<username> -e POSTGRES_PASSWORD=<password> -e POSTGRES_HOST=<host> -e POSTGRES_DB=<db_name> -p 3000:3000 api
```

### Raw Data Processing

The pipeline has the following steps:

1. Fetching raw data, i.e., transactions from the database.
2. Transforming transactions into events. Events are parsed transactions from which we can infer the action that occured within the given transaction, e.g., that some user deposited collateral, borrowed some tokens, or was liquidated.
3. Interpreting all events since origin to get the current state of all loans on the chain.
4. Model the expected volume of liquidations for a given price level, aggregated across all loans.
5. Gather information about available liquidity for a given price level in the amm pools.
6. Compute information about individual loans, e.g., the health ratio or the total debt in USD.
7. Compute comparison statistics for all lending protocols, e.g., the number of users or utilization rates.
8. Save the processed data and the information about the last update, so that next time, we do not need to start the computations from origin.

For running the data processing pipeline, run the following commands:

```sh
docker build -t data-processing -f Dockerfile.data-processing .
docker run data-processing
```
Currently, the script outlines all of the above-mentioned steps, but their implementation is part of the future milestones.

### Transaction Parsers
Parsing of collected transactions is dockerized. 
 Each protocol has a dedicated Dockerfile:

- `Dockerfile.mango-parser` for Mango Markets
- `Dockerfile.solend-parser` for Solend
- `Dockerfile.marginfi-parserV2` for MarginFi
- `Dockerfile.kamino-parser` for Kamino

Example:
```bash
docker build -t mango-parser -f Dockerfile.mango-parser .
docker run -e POSTGRES_USER=<db_user> \
    -e POSTGRES_PASSWORD=<db_password> -e POSTGRES_HOST=<db_host> \
    -e POSTGRES_DB=<db_name> mango-parser
```

The orchestration of data parsing is managed by `Dockerfile.parsing-pipeline`. To run the pipelines, an environment variable `PROTOCOL` must be set, specifying which protocol's parser to execute. Example of usage can be find below.

Transaction parsing are handled in the following classes:
#### KaminoTransactionParserV2 Class

##### Overview
`KaminoTransactionParserV2` is a class designed to parse transactions for the Kamino protocol.
It decodes transaction instructions, associates them with corresponding log messages, and stores relevant data in a database.

##### Responsibilities
- **Transaction Decoding:** Decodes and validates transaction instructions against the Kamino program ID.
- **Event Handling:** Parses specific transaction types (events) and stores structured data for each recognized instruction.
- **Data Storage:** Saves parsed data to database models designed for different aspects of transaction data.

##### Parsed Events
This parser specifically handles the following types of events within the Kamino protocol:
- `initObligation`: Initializes a new lending obligation.
- `initReserve`: Sets up a new reserve.
- Transactional events such as:
  - `depositObligationCollateral`
  - `withdrawObligationCollateral`
  - `depositReserveLiquidity`
  - `redeemReserveCollateral`
  - `borrowObligationLiquidity`
  - `repayObligationLiquidity`
  - `depositReserveLiquidityAndObligationCollateral`
  - `withdrawObligationCollateralAndRedeemReserveCollateral`
  - `liquidateObligationAndRedeemReserveCollateral`
  - `flashRepayReserveLiquidity`
  - `flashBorrowReserveLiquidity`
- These events handle the collateral and debt change within the Kamino ecosystem.

##### Database Storage
The parser stores data in the following database tables:
- `kamino_obligation_v2`: Stores information about lending obligations.
- `kamino_reserve_v2`: Contains details about liquidity reserves.
- `kamino_parsed_transactions_v2`: Logs detailed transaction data including the type of event, associated accounts, amounts, and other transaction metadata.

#### MangoTransactionParserV2 Class

##### Overview
`MangoTransactionParserV2` is designed to parse and decode 
transaction events specifically for the Mango protocol.
It handles various log events related to trading and lending activities affecting size of debt and its collateralization on the MangoV4 platform.

##### Responsibilities
- **Transaction Decoding:** Decodes transaction events using a predefined IDL (Interface Description Language) and associates them with the Mango program ID.
- **Event Handling:** Identifies and processes all relevant event types within the Mango ecosystem.

##### Parsed Events
This parser handles numerous event types, including but not limited to:
- Trading events like `FillLog`, `FillLogV2`, `FillLogV3`, and `PerpTakerTradeLog`.
- Loan and collateral events such as `WithdrawLoanLog`, `DepositLog`, `WithdrawLog`, and `TokenCollateralFeeLog`.
- Perpetual and futures related logs like `PerpUpdateFundingLog`, `PerpLiqBaseOrPositivePnlLog`, `PerpLiqNegativePnlOrBankruptcyLog`, and `PerpForceClosePositionLog`.
- Flash loan events such as `FlashLoanLog`, `FlashLoanLogV2`, `FlashLoanLogV3`.
- Logs related to conditional swaps, including `TokenConditionalSwapCreateLog`, `TokenConditionalSwapTriggerLog`, and `TokenConditionalSwapCancelLog`.

##### Database Storage
Parsed events are stored in the `MangoParsedEvents` table, which includes fields like:
- `transaction_id`: Unique identifier of the transaction.
- `event_name`: Name of the event parsed.
- `event_data`: Detailed structured data associated with the event.

#### MarginfiTransactionParserV2 Class

##### Overview
`MarginfiTransactionParserV2` is a specialized class designed to decode and parse transaction instructions associated with the Marginfi protocol.

##### Responsibilities
- **Transaction Decoding:** Decodes transaction instructions that match the Marginfi program ID using the provided IDL.
- **Event Handling:** Parses a defined set of transaction events related to Marginfi operations, ensuring that each is correctly interpreted and processed.
- **Data Storage:** Structures and stores parsed transaction data in relevant database tables, facilitating further analysis and record-keeping.

##### Parsed Events
The parser recognizes and handles:
- Account initialization and management: `marginfiAccountInitialize`, `lendingPoolAddBank`
- Lending operations: `lendingAccountDeposit`, `lendingAccountWithdraw`, `lendingAccountBorrow`, `lendingAccountRepay`
- Account and position management: `lendingAccountCloseBalance`, `lendingAccountLiquidate`
- Emission-related transactions: `lendingAccountWithdrawEmissions`, `lendingAccountSettleEmissions`
- Flashloan transactions: `lendingAccountStartFlashloan`, `lendingAccountEndFlashloan`

##### Database Storage
Parsed data is saved to several database models tailored for different aspects of transaction data:
- `MarginfiLendingAccountsV2`: Captures data about lending accounts.
- `MarginfiBankV2`: Stores information about banks within the Marginfi protocol.
- `MarginfiParsedTransactionsV2`: Logs comprehensive details about each parsed transaction event, including transaction identifiers, event names, and associated data.

##### Usage
To utilize this parser, instantiate it with the path to the Marginfi IDL and the program's public key.

#### SolendTransactionParser Class

##### Overview
The `SolendTransactionParser` is designed to parse and decode transaction instructions associated with the Solend protocol.

##### Responsibilities
- **Transaction Decoding:** Decodes transaction instructions based on a predefined set of instruction types using Solend's program ID.
- **Event Handling:** Identifies and processes a wide range of financial operations such as deposits, withdrawals, loans, and repayments.

##### Parsed Events
This parser handles several types of events linked to the core functionality of Solend, including:
- Market and reserve initialization: `init_lending_market`, `init_reserve`
- Liquidity management: `deposit_reserve_liquidity`, `redeem_reserve_collateral`, `withdraw_obligation_collateral_and_redeem_reserve_liquidity`
- Obligation management: `init_obligation`, `deposit_obligation_collateral`, `withdraw_obligation_collateral`, `refresh_obligation`
- Loan operations: `borrow_obligation_liquidity`, `repay_obligation_liquidity`, `liquidate_obligation`
- Flash loan operations: `flash_loan`, `flash_borrow_reserve_liquidity`, `flash_repay_reserve_liquidity`
- Other relevant transactions like `forgive_debt` and `redeem_fee`

##### Database Storage
The parsed data is stored in tables such as `solend_reserves` and `solend_sbligations`:

##### Usage
Instantiate the parser with the Solend program's public key.



### Parsing pipelines
Data parsing orchestration is assured by `Dockerfile.parsing-pipeline`. 
To run pipelines ENV variable `PROTOCOL' is required. 

Example:

```bash
docker build -t parsing-pipeline -f Dockerfile.parsing-pipeline .
docker run -e PROTOCOL=,protocol_name. POSTGRES_USER=<db_user> \
    -e POSTGRES_PASSWORD=<db_password> -e POSTGRES_HOST=<db_host> \
    -e POSTGRES_DB=<db_name> parsing-pipeline
```
Allowed protocol names: `mango`, `kamino`, `marginfi` and `solend`.

### Available Liquidity

We compute liquidity available at orderbook exchanges and swap AMMs. By `available liquidity` we mean the maximum quantity that can be traded or swapped at the given venue withou moving the price by more than 5%.

##### Swap AMMs

We compute the available liquidity on swap AMMs by aggregating the available liquidities on every single AMM/venue. For the given AMM, given debt token, given collateral token and its price, we follow these steps:

1. Fetch raw data, i.e., information about the pools (namely which tokens are in the pool and how many of them are there), and saving it to the database. This is described in the section `AMMs` in detail.
2. Load raw data for the pools containing the tokens of interest from the database. We load the latest data fetched, there is no need to load historical data.
3. Simulate trading/swapping to learn how much of the token of interest can be obtained on the AMM without moving the price by more than 5%.

##### Orderbook Exchanges

In contrast with AMMs, it's not very simple to simulate liquidity that would available on orderbook exchanges in case the price of the collateral token drops. Nevertheless, for the given exchange and given pair of tokens, we use the following approximation:

1. Fetch raw data, i.e., historical snapshots of orderbooks for the tokens of interest, and saving it to the database. This is described in the section `CLOB DEXes` in detail.
2. Load historical snapshots from the exchange for the tokens of interest. We load historical snapshots fromt the past 5 days.
3. For every snapshot, compute limit order quantity available within 5% from the mid price in the direction of interest.
4. Take the resulting time series of snapshots and compute its 5% quantile which is a rough estimate of the liquidity the remains in the orderbook when the price of the collateral token drops suddenly. 

### Frontend

The frontend is a `streamlit` app which spawns a data updating process in the background. The process repeatedly loads new raw data, processes it and saves the outputs. The app then loads the latest outputs to visualize the following:

1. Select boxes for the user the choose protocols and tokens of interest.
2. Chart of the liquidable debt against the available supply, based on the parameters chosen above.
3. Warning message informing the user about the risk of under-the-water loans.
4. Statistics on individual loans with the lowest health factor. The loans fall within the range of debt in USD chosen by the user.
5. Tables depicting various statistics based in which we can compare the lending protocols, e.g., the number of users or utilization rates.
6. Pie charts showing each protocol's collateral, debt and supply for various tokens.
7. Histograms visualizing the distribution of debt sizes across all lending protocols.
8. Timestamp and block number corresponding to when the data was last updated.

For running the frontend, run the following commands:

```sh
docker build -t frontend -f Dockerfile.frontend .
# default port for Streamlit is 8501
docker run -p 8501:8501 frontend
```

Currently, the app visualizes all of the above-mentioned items, but the data is empty and relies on completing future milestones.
