from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import pandas as pd


@dataclass
class AllocationStrategy:
    target_weights: Dict[str, float]
    rebalance_threshold: float
    max_allocation: float
    min_allocation: float


class PortfolioAllocator:
    def __init__(self, strategy: AllocationStrategy):
        self.strategy = strategy
        self.current_allocations = {}
        self.historical_allocations = pd.DataFrame()

    async def optimize_allocation(
        self, market_data: pd.DataFrame, risk_metrics: Dict
    ) -> Dict[str, float]:
        returns = self._calculate_returns(market_data)
        risks = self._calculate_risks(returns)
        optimal_weights = self._run_optimization(returns, risks, risk_metrics)

        return self._apply_constraints(optimal_weights)

    async def rebalance_portfolio(
        self, current_positions: Dict[str, float], market_prices: Dict[str, float]
    ) -> Dict[str, Dict]:
        current_weights = self._calculate_weights(current_positions, market_prices)
        deviations = self._calculate_deviations(current_weights)

        if self._needs_rebalancing(deviations):
            return await self._generate_rebalancing_trades(
                current_positions, market_prices
            )
        return {}

    def _calculate_returns(self, market_data: pd.DataFrame) -> pd.DataFrame:
        return market_data.pct_change().dropna()

    def _calculate_risks(self, returns: pd.DataFrame) -> Dict[str, float]:
        return {
            "volatility": returns.std(),
            "var": self._calculate_var(returns),
            "correlation": returns.corr(),
        }
