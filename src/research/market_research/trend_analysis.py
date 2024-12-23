from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np
import pandas as pd


@dataclass
class TrendMetrics:
    strength: float
    duration: int
    momentum: float
    support: float
    resistance: float


class TrendAnalyzer:
    def __init__(self):
        self.trends = pd.DataFrame()
        self.current_trends = {}

    async def analyze_trends(self, market_data: pd.DataFrame) -> Dict:
        price_trends = self._analyze_price_trends(market_data)
        volume_trends = self._analyze_volume_trends(market_data)
        sentiment_trends = await self._analyze_sentiment_trends(market_data)

        combined_trends = self._combine_trends(
            price_trends, volume_trends, sentiment_trends
        )

        return {
            "trends": combined_trends,
            "strength": self._calculate_trend_strength(combined_trends),
            "signals": self._generate_trend_signals(combined_trends),
        }

    async def identify_market_cycles(self, data: pd.DataFrame) -> List[Dict]:
        cycles = []

        # Detect local maxima and minima
        peaks = self._find_peaks(data["close"])
        troughs = self._find_troughs(data["close"])

        # Identify market phases
        for i in range(len(peaks) - 1):
            cycle = self._analyze_cycle(data, peaks[i], troughs[i], peaks[i + 1])
            cycles.append(cycle)

        return cycles

    def _analyze_price_trends(self, data: pd.DataFrame) -> Dict:
        trends = {}
        timeframes = ["1h", "4h", "1d", "1w"]

        for tf in timeframes:
            resampled = data.resample(tf).agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )

            trends[tf] = self._identify_trend(resampled)

        return trends

    def _identify_trend(self, data: pd.DataFrame) -> TrendMetrics:
        # Calculate moving averages
        ma20 = data["close"].rolling(window=20).mean()
        ma50 = data["close"].rolling(window=50).mean()

        # Determine trend direction and strength
        trend_direction = 1 if ma20.iloc[-1] > ma50.iloc[-1] else -1
        strength = abs(ma20.iloc[-1] - ma50.iloc[-1]) / ma50.iloc[-1]

        # Calculate support and resistance
        support = self._calculate_support(data)
        resistance = self._calculate_resistance(data)

        return TrendMetrics(
            strength=strength * trend_direction,
            duration=self._calculate_trend_duration(data),
            momentum=self._calculate_momentum(data),
            support=support,
            resistance=resistance,
        )

    def _generate_trend_signals(self, trends: Dict) -> List[Dict]:
        signals = []

        for timeframe, trend in trends.items():
            if abs(trend.strength) > 0.1:  # Significant trend
                signals.append(
                    {
                        "timeframe": timeframe,
                        "direction": "bullish" if trend.strength > 0 else "bearish",
                        "strength": abs(trend.strength),
                        "momentum": trend.momentum,
                    }
                )

        return sorted(signals, key=lambda x: x["strength"], reverse=True)
