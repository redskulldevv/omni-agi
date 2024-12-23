from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np


@dataclass
class PositionSize:
    token: str
    size: float
    value: float
    risk_amount: float
    stop_loss: float
    take_profit: float


class PositionSizer:
    def __init__(self, config: Dict):
        self.config = config
        self.portfolio_value = 0
        self.risk_per_trade = config["risk_per_trade"]
        self.max_position_size = config["max_position_size"]

    async def calculate_position_size(
        self, token: str, entry_price: float, stop_loss: float
    ) -> PositionSize:
        risk_amount = self.portfolio_value * self.risk_per_trade
        position_value = self._calculate_value(risk_amount, entry_price, stop_loss)

        if position_value > self.portfolio_value * self.max_position_size:
            position_value = self.portfolio_value * self.max_position_size

        size = position_value / entry_price
        take_profit = self._calculate_take_profit(entry_price, stop_loss)

        return PositionSize(
            token=token,
            size=size,
            value=position_value,
            risk_amount=risk_amount,
            stop_loss=stop_loss,
            take_profit=take_profit,
        )

    def _calculate_value(self, risk_amount: float, entry: float, stop: float) -> float:
        risk_percent = abs((entry - stop) / entry)
        return risk_amount / risk_percent

    def _calculate_take_profit(self, entry: float, stop: float) -> float:
        risk = abs(entry - stop)
        return entry + (risk * self.config["reward_risk_ratio"])
