import os
from enum import Enum
from pathlib import Path


ROOT_DIR = os.getenv("SCRAPER_ROOT", ".")
CORE_DIR = Path(f"{ROOT_DIR}/scraper")
DATA_DIR = Path(f"{ROOT_DIR}/data")


class OfflineDataStream(Enum):
    BITCOIN_DATA_FNAME = "bitcoin_data.csv"
    STOP_ITERATION_FLAG = "STOP ITERATION"


class OnlineDataStream(Enum):
    pass
