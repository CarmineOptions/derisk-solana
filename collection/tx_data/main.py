import logging

from collection.tx_data.connector import TXFromBlockConnector


LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    collector = TXFromBlockConnector()
    LOG.info(f"Collector for `{collector.COLLECTION_STREAM}` data is ready...")
    collector.run()

