import re
import sys
import os
from pathlib import Path

import numpy as np
import pandas as pd
from pandas import DataFrame

from scraper.utils.common import constants


class DataIterator:
    """
    Offline Data Loader [ csv file ]

    Divides existing dataset into smaller chunks of time periods
    Component structured in a iterable way so to ensure common usage with step method

    Args:
        :param [crypto_type]: crypto dataset used to train the agent [ btc, ether ]
        :param [time_interval]: value depicting the evaluation time for the agent
        :param [black_size]: number of adjacent time intervals
    """

    def __init__(self, crypto_type: str, time_interval: str, day_count: int) -> None:
        self._current_index = 0
        self.crypto_type = crypto_type
        self.time_interval = time_interval
        self.day_count = day_count
        self.data_directory = self._fetch_data_directory()
        self.data = self._preprocess_data(self.data_directory)

    def _fetch_data_directory(self) -> Path:
        """Get crypto data directory"""

        current_file_dir = os.path.abspath(
            sys.modules[DataIterator.__module__].__file__
        )
        target_dir = current_file_dir.split(os.sep)[:-3]
        path_to_scraper = Path(os.path.join(*target_dir))
        if self.crypto_type == "btc":
            return (
                Path("/")
                / path_to_scraper
                / constants.DATA_DIR
                / constants.OfflineDataStream.BITCOIN_DATA_FNAME.value
            )
        else:
            return None

    def _preprocess_data(self, data_path: Path) -> DataFrame:
        """open and preprocess csv file"""
        crypto_df = pd.read_csv(data_path)
        crypto_interpolated_df = crypto_df[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume_(BTC)",
                "Volume_(Currency)",
                "Weighted_Price",
            ]
        ].interpolate()
        crypto_interpolated_df["Timestamp"] = crypto_df["Timestamp"]

        crypto_interpolated_df["Date"] = pd.to_datetime(
            crypto_interpolated_df["Timestamp"], unit="s"
        )
        crypto_interpolated_df.set_index("Timestamp", inplace=True)
        crypto_interpolated_df["Year"] = crypto_interpolated_df["Date"].dt.year

        crypto_correct_data_df = crypto_interpolated_df[
            ~(crypto_interpolated_df["Date"] < "2018-01-01")
        ]
        return crypto_correct_data_df

    def _hit_data_tail(self, start: int, block_step: int, max_index: int) -> bool:
        """check wheter there is no jump to the past once computing slice"""
        overlap = (start + block_step) / max_index
        if overlap > 1.0:
            return True
        else:
            return False

    def _compute_window_slide(self):
        """compute slice properties based on parameters in ctor"""
        int_time_interval = int(re.search(r"\d+", self.time_interval).group())
        minutes_x_freq = 1440 / int_time_interval
        window_slide = int(minutes_x_freq * self.day_count)
        return window_slide

    def _normalize_data_window(self, dataframe: DataFrame) -> DataFrame:
        """normalize dataframe"""
        normalized_df = dataframe.copy()
        column_names = normalized_df.columns.tolist()
        for column in column_names:
            if column == "Date" or column == "Year":
                raise TypeError(
                    "Could not normalize Year and Data series - consider dropping "
                    "before normalizing"
                )
            else:
                next_shift = normalized_df[column].shift(1)
                normalized_df[column] = np.log(normalized_df[column]) - np.log(
                    next_shift
                )
                min_col = normalized_df[column].min()
                max_col = normalized_df[column].max()
                normalized_df[column] = (normalized_df[column] - min_col) / (
                    max_col - min_col
                )
        clean_normalized_df = normalized_df.dropna()
        is_nan = clean_normalized_df.isna().sum()
        if is_nan.any():
            raise SystemError("NaN value found")
        return clean_normalized_df
