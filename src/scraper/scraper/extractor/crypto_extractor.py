from typing import Dict

import numpy as np
import tweepy

from scraper.iterator import DataIterator


class CryptoExtractor:
    """
    Data extractor component

    Constructs data iterator [ online, offline ] and sources API for data ingestion.

    Args:
        param: [config]: configuration dictionary

    Internal State:
        :param [iterator_type]: type of data iterator [ online, offline ]
        :param [crypto_type]: crypto dataset used to train the agent [ btc, ether ]
        :param [time_interval]: value depicting the evaluation time for the agent
        :param [black_size]: number of adjacent time intervals
    """

    def __init__(
        self,
        config: Dict,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
    ) -> None:
        self.iterator_type = config["iterator_type"]
        self.crypto_type = config["crypto_type"]
        self.time_interval = config["time_interval"]
        self.day_count = config["day_count"]
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.client = self.authenticate()

        self.data_iterator = self._construct_iterator()

    def authenticate(self):
        auth = tweepy.OAuth1UserHandler(
            self.api_key, self.api_secret, self.access_token, self.access_token_secret
        )
        return tweepy.API(auth)

    def _construct_iterator(self) -> DataIterator:
        """construct iterator based on iterator_type parameter"""
        if self.iterator_type == "offline":
            return iter(
                DataIterator(
                    self.crypto_type,
                    self.time_interval,
                    self.day_count,
                )
            )
        else:
            raise NotImplementedError("Not yet implemented")

    def get_data_sample(self):
        """return single sample from data iterator"""
        return next(self.data_iterator)

    def get_crypto_mean_window_price(self) -> np.ndarray:
        """calculate mean of the window dataset and return value associated"""
        return self.data_iterator.mean_window_crypto_price

    def reset_data_iterator(self) -> None:
        """reset data iteator entity"""
        self.data_iterator = self._construct_iterator()

    @property
    def window_day_count(self) -> int:
        return self.day_count

    @property
    def window_time_interval(self) -> int:
        return self.time_interval
