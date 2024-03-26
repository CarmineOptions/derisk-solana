import asyncio
import logging

from src.collection.tx_data.current_data_collector import CurrentTXCollector, LOGGER


async def main():
    LOGGER.info('Start collecting new transactions from Solana chain: ...')
    tx_collector = CurrentTXCollector()
    await tx_collector.async_run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    asyncio.run(main())
