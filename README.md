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
### AMMs

For updating AMMs' pools data following environmental variables are required:

- `POSTGRES_USER` name of the database user
- `POSTGRES_PASSWORD` database user's password
- `POSTGRES_HOST` host address, IP address or DNS of the database
- `POSTGRES_DB` database name

Then, run the following commands:

```sh
docker build --file ./Dockerfile.update-amm-pools -t amms .
docker run -d --name amms -e POSTGRES_USER=$POSTGRES_USER -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_HOST=$POSTGRES_HOST -e POSTGRES_DB=$POSTGRES_DB amms
```

Data collected from following DEXes:
- [Orca](https://www.orca.so/)
- [Raydium](https://raydium.io/)
- [Meteora](https://www.meteora.ag/)

Data Collection Strategy
The data collection process involves querying each DEX's first-party API for current pool statuses. This process is automated through a scheduled task that runs the above Docker container, ensuring data freshness. The approach is as follows:

1) Initialization: On startup, the Docker container queries the DEX APIs to fetch the initial state of all liquidity pools.
2) Continuous Update: The container polls the APIs every 300 seconds to capture any changes in pools' liquidity.
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
