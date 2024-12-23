from dataclasses import dataclass
import asyncio
from datetime import datetime
from typing import Dict, List
import pandas as pd
import numpy as np


@dataclass
class SentimentMetrics:
    overall_score: float
    social_score: float
    news_score: float
    market_score: float
    developer_score: float
    timestamp: datetime


class SentimentAnalyzer:
    def __init__(self):
        self.nlp_model = self._load_nlp_model()
        self.sentiment_history = pd.DataFrame()

    async def analyze_sentiment(self, token: str) -> SentimentMetrics:
        social_metrics = await self._analyze_social_sentiment(token)
        news_metrics = await self._analyze_news_sentiment(token)
        market_metrics = await self._analyze_market_sentiment(token)
        dev_metrics = await self._analyze_developer_sentiment(token)

        overall_score = self._calculate_overall_sentiment(
            social_metrics, news_metrics, market_metrics, dev_metrics
        )

        metrics = SentimentMetrics(
            overall_score=overall_score,
            social_score=social_metrics["score"],
            news_score=news_metrics["score"],
            market_score=market_metrics["score"],
            developer_score=dev_metrics["score"],
            timestamp=datetime.now(),
        )

        await self._store_sentiment_history(token, metrics)
        return metrics

    async def _analyze_social_sentiment(self, token: str) -> Dict:
        twitter_sentiment = await self._analyze_twitter(token)
        discord_sentiment = await self._analyze_discord(token)
        telegram_sentiment = await self._analyze_telegram(token)

        return {
            "score": np.mean(
                [
                    twitter_sentiment["score"],
                    discord_sentiment["score"],
                    telegram_sentiment["score"],
                ]
            ),
            "metrics": {
                "twitter": twitter_sentiment,
                "discord": discord_sentiment,
                "telegram": telegram_sentiment,
            },
        }

    async def analyze_sentiment_trends(self, token: str, timeframe: str) -> Dict:
        history = self.sentiment_history[self.sentiment_history["token"] == token]
        history = self._resample_history(history, timeframe)

        trends = {
            "sentiment_change": self._calculate_sentiment_change(history),
            "volatility": self._calculate_sentiment_volatility(history),
            "momentum": self._calculate_sentiment_momentum(history),
            "extremes": self._identify_sentiment_extremes(history),
        }

        anomalies = self._detect_sentiment_anomalies(history)
        if anomalies:
            trends["anomalies"] = anomalies

        return trends

    async def generate_sentiment_report(self, token: str) -> Dict:
        current_sentiment = await self.analyze_sentiment(token)
        trends = await self.analyze_sentiment_trends(token, "1d")

        return {
            "current": current_sentiment.__dict__,
            "trends": trends,
            "signals": await self._generate_sentiment_signals(
                current_sentiment, trends
            ),
            "correlations": await self._analyze_sentiment_correlations(token),
        }
