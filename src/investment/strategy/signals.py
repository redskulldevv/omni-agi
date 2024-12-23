from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import pandas as pd


@dataclass
class SignalParams:
    timeframe: str
    indicators: List[str]
    thresholds: Dict[str, float]
    weights: Dict[str, float]


class SignalGenerator:
    def __init__(self, params: SignalParams):
        self.params = params
        self.signals = []
        self.indicators = self._initialize_indicators()

    async def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        indicator_signals = {}

        for indicator in self.params.indicators:
            values = await self._calculate_indicator(indicator, market_data)
            signals = self._evaluate_indicator(indicator, values)
            indicator_signals[indicator] = signals

        combined_signals = self._combine_indicator_signals(indicator_signals)
        filtered_signals = self._filter_signals(combined_signals)

        return filtered_signals

    async def _calculate_indicator(
        self, indicator: str, data: pd.DataFrame
    ) -> pd.Series:
        if indicator == "rsi":
            return self._calculate_rsi(data)
        elif indicator == "macd":
            return self._calculate_macd(data)
        elif indicator == "bollinger":
            return self._calculate_bollinger_bands(data)

    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(
        self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, pd.Series]:
        exp1 = data["close"].ewm(span=fast).mean()
        exp2 = data["close"].ewm(span=slow).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal).mean()

        return {"macd": macd, "signal": signal_line, "histogram": macd - signal_line}

    def _evaluate_indicator(self, indicator: str, values: pd.Series) -> List[Dict]:
        threshold = self.params.thresholds[indicator]
        signals = []

        if indicator == "rsi":
            signals.extend(self._evaluate_rsi(values, threshold))
        elif indicator == "macd":
            signals.extend(self._evaluate_macd(values, threshold))

        return signals

    def _combine_indicator_signals(
        self, indicator_signals: Dict[str, List]
    ) -> List[Dict]:
        combined = []
        weights = self.params.weights

        for indicator, signals in indicator_signals.items():
            for signal in signals:
                signal["strength"] *= weights[indicator]
                combined.append(signal)

        return combined

    def _filter_signals(self, signals: List[Dict]) -> List[Dict]:
        filtered = []
        min_strength = self.params.thresholds["min_signal_strength"]

        for signal in signals:
            if signal["strength"] >= min_strength:
                filtered.append(signal)

        return sorted(filtered, key=lambda x: x["strength"], reverse=True)
