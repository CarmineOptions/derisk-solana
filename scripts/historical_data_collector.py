import asyncio
import logging

from src.collection.tx_data.historical_data_collector import HistoricalTXCollector, LOGGER


async def main():
    LOGGER.info('Start collecting old transactions from Solana chain: ...')
    tx_collector = HistoricalTXCollector()
    await tx_collector.async_run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
