from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


@dataclass
class RebalanceConfig:
    threshold: float
    max_drift: float
    min_trade_size: float
    target_weights: Dict[str, float]


class PortfolioRebalancer:
    def __init__(self, config: RebalanceConfig):
        self.config = config
        self.rebalance_history = pd.DataFrame()

    async def check_rebalance_needed(self, current_positions: Dict) -> bool:
        current_weights = self._calculate_weights(current_positions)
        max_drift = max(
            abs(current_weights[token] - self.config.target_weights[token])
            for token in current_weights
        )
        return max_drift > self.config.threshold

    async def generate_rebalance_trades(
        self, current_positions: Dict, market_prices: Dict
    ) -> List[Dict]:
        trades = []
        current_weights = self._calculate_weights(current_positions)

        for token, target in self.config.target_weights.items():
            current = current_weights.get(token, 0)
            if abs(current - target) > self.config.threshold:
                trade = self._calculate_trade(
                    token, current, target, current_positions, market_prices
                )
                if trade:
                    trades.append(trade)

        return self._optimize_trades(trades)

    def _calculate_trade(
        self,
        token: str,
        current_weight: float,
        target_weight: float,
        positions: Dict,
        prices: Dict,
    ) -> Optional[Dict]:
        portfolio_value = sum(positions[t] * prices[t] for t in positions)

        target_value = portfolio_value * target_weight
        current_value = portfolio_value * current_weight
        trade_value = target_value - current_value

        if abs(trade_value) < self.config.min_trade_size:
            return None

        return {
            "token": token,
            "side": "buy" if trade_value > 0 else "sell",
            "amount": abs(trade_value) / prices[token],
            "estimated_price": prices[token],
        }
