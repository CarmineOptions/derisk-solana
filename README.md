# DeRisk Solana

Monorepo with components required for DeRisk to function on Solana.

### Event Aggregator

Aggregates Solana events into the database.

### Research

Calculates the state of the lending protocols and the risk of underwater loans from events.

### Frontend

Visualisation of the Research data.

## Project Setup

The setup consists of:
1) [`Database`] Creating an empty database for raw data.
2) [`Raw Data Fetching`] Running a script that feeds the database with raw data.
3) [`API`] Creating an API for fetching the raw data from the database.
4) [`Raw Data Processing`] Running a script which processes the raw data.
5) [`Frontend`] Running a frontend with visualizations of the processed data.

Each step is described in detail below.

### Database

TODO

### Raw Data Fetching

TODO

### API

TODO

### Raw Data Processing

The pipeline has the following steps:
1) Fetching raw data, i.e., transactions from the database.
2) Transforming transactions into events. Events are parsed transactions from which we can infer the action that occured within the given transaction, e.g., that some user deposited collateral, borrowed some tokens, or was liquidated.
3) Interpreting all events since origin to get the current state of all loans on the chain.
4) Model the expected volume of liquidations for a given price level, aggregated across all loans.
5) Gather information about available liquidity for a given price level in the amm pools.
6) Compute information about individual loans, e.g., the health ratio or the total debt in USD.
7) Compute comparison statistics for all lending protocols, e.g., the number of users or utilization rates.
8) Save the processed data and the information about the last update, so that next time, we do not need to start the computations from origin.

For running the data processing pipeline, run the following commands:
```sh
docker build -t data-processing -f Dockerfile.data-processing .
docker run data-processing
```

Currently, the script outlines all of the above-mentioned steps, but their implementation is part of the future milestones.

### Frontend

TODO
