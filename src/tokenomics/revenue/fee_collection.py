from dataclasses import dataclass
from typing import Dict, List, Optional
from decimal import Decimal
import pandas as pd

@dataclass
class FeeConfig:
    trading_fee: float
    protocol_fee: float
    staking_fee: float
    burn_rate: float
    minimum_fee: float

class FeeCollector:
    def __init__(self, config: FeeConfig):
        self.config = config
        self.collected_fees = {}
        self.fee_history = pd.DataFrame()

    async def collect_fees(self, transaction: Dict) -> Dict:
        """Collect fees from a transaction"""
        try:
            fee_breakdown = self._calculate_fees(
                transaction["amount"],
                transaction["type"]
            )
            
            await self._process_fees(fee_breakdown)
            await self._update_fee_history(fee_breakdown)
            
            return fee_breakdown
        except Exception as e:
            print(f"Error collecting fees: {e}")
            raise

    def _calculate_fees(self, amount: float, tx_type: str) -> Dict:
        """Calculate fee breakdown based on transaction type"""
        base_fee = max(amount * self.config.trading_fee, self.config.minimum_fee)
        
        return {
            "trading_fee": base_fee * (1 - self.config.protocol_fee),
            "protocol_fee": base_fee * self.config.protocol_fee,
            "staking_fee": base_fee * self.config.staking_fee,
            "burn_amount": base_fee * self.config.burn_rate,
            "total": base_fee
        }

    async def get_fee_statistics(self, timeframe: str = "24h") -> Dict:
        """Get fee collection statistics for a timeframe"""
        filtered_history = self._filter_fee_history(timeframe)
        
        return {
            "total_collected": filtered_history["total"].sum(),
            "by_type": self._group_fees_by_type(filtered_history),
            "trends": self._analyze_fee_trends(filtered_history)
        }
