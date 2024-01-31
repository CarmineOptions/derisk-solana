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
