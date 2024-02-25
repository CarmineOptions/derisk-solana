import logging

from collection.tx_data.collector import TXFromBlockCollector


LOG = logging.getLogger(__name__)


if __name__ == "__main__":
    collector = TXFromBlockCollector()
    LOG.info(f"Collector for `{collector.COLLECTION_STREAM.value}` data is ready...")
    collector.run()
