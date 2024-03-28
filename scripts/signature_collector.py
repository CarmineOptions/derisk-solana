import logging

from src.collection.historical_signatures.signature_collector import SignatureCollector, LOGGER


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    LOGGER.info('Start collecting signatures from Solana chain: ...')
    tx_collector = SignatureCollector()
    tx_collector.run()
