from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from decimal import Decimal

@dataclass
class MarketMakingConfig:
    spread: float
    depth: float
    min_order_size: float
    max_order_size: float
    num_orders: int
    refresh_interval: int

class MarketMaker:
    def __init__(self, config: MarketMakingConfig):
        self.config = config
        self.active_orders = {}
        self.order_history = pd.DataFrame()
        
    async def generate_orders(self, 
                            mid_price: float,
                            inventory: Dict[str, float]) -> Dict[str, List]:
        try:
            bid_orders = self._generate_bid_orders(mid_price, inventory)
            ask_orders = self._generate_ask_orders(mid_price, inventory)
            
            return {
                "bids": bid_orders,
                "asks": ask_orders
            }
        except Exception as e:
            print(f"Error generating orders: {e}")
            raise

    async def adjust_inventory(self, 
                             current_inventory: Dict[str, float],
                             target_ratio: float) -> List[Dict]:
        try:
            current_ratio = self._calculate_inventory_ratio(current_inventory)
            if abs(current_ratio - target_ratio) > self.config.inventory_threshold:
                return self._generate_rebalancing_orders(
                    current_inventory,
                    target_ratio
                )
            return []
        except Exception as e:
            print(f"Error adjusting inventory: {e}")
            raise

    def _generate_bid_orders(self, 
                           mid_price: float,
                           inventory: Dict[str, float]) -> List[Dict]:
        orders = []
        spread_step = self.config.spread / self.config.num_orders
        
        for i in range(self.config.num_orders):
            price = mid_price * (1 - (spread_step * (i + 1)))
            size = self._calculate_order_size(price, "bid", inventory)
            
            if size >= self.config.min_order_size:
                orders.append({
                    "side": "bid",
                    "price": price,
                    "size": size
                })
        
        return orders