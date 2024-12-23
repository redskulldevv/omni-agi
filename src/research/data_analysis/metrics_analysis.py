from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


@dataclass
class MetricsConfig:
    timeframes: List[str]
    metrics: List[str]
    thresholds: Dict[str, float]


class MetricsAnalyzer:
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.metrics_history = pd.DataFrame()
        self.scaler = StandardScaler()

    async def analyze_metrics(self, data: pd.DataFrame) -> Dict:
        normalized_data = self._normalize_data(data)
        metrics = {}

        for timeframe in self.config.timeframes:
            timeframe_data = self._get_timeframe_data(normalized_data, timeframe)
            metrics[timeframe] = {
                "growth": self._analyze_growth(timeframe_data),
                "volatility": self._analyze_volatility(timeframe_data),
                "correlation": self._analyze_correlation(timeframe_data),
                "trends": self._analyze_trends(timeframe_data),
            }

        return metrics

    def _normalize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            self.scaler.fit_transform(data), columns=data.columns, index=data.index
        )

    def _analyze_growth(self, data: pd.DataFrame) -> Dict:
        return {
            "total_growth": data.pct_change().sum(),
            "cagr": self._calculate_cagr(data),
            "growth_stability": self._calculate_growth_stability(data),
        }

    def _analyze_volatility(self, data: pd.DataFrame) -> Dict:
        returns = data.pct_change().dropna()
        return {
            "std_dev": returns.std(),
            "var_95": self._calculate_var(returns, 0.95),
            "max_drawdown": self._calculate_max_drawdown(data),
        }
