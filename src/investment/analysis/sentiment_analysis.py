from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@dataclass
class MarketConditions:
    trend: str  # bullish, bearish, neutral
    price: float
    volume_24h: float
    market_cap: float
    dominance: float
    volatility: float


class MarketAnalyzer:
    def __init__(self, data_sources: Dict[str, str]):
        self.data_sources = data_sources
        self.market_data = pd.DataFrame()
        self.indicators = self._initialize_indicators()

    async def analyze_market_conditions(self, token: str) -> MarketConditions:
        price_data = await self._fetch_price_data(token)
        volume_data = await self._fetch_volume_data(token)
        market_data = await self._fetch_market_data(token)

        trend = self._determine_trend(price_data)
        volatility = self._calculate_volatility(price_data)

        return MarketConditions(
            trend=trend,
            price=price_data["close"].iloc[-1],
            volume_24h=volume_data["volume"].sum(),
            market_cap=market_data["market_cap"].iloc[-1],
            dominance=market_data["dominance"].iloc[-1],
            volatility=volatility,
        )

    async def analyze_market_depth(self, token: str) -> Dict:
        order_book = await self._fetch_order_book(token)
        liquidity = await self._analyze_liquidity(token)
        slippage = self._calculate_slippage(order_book)

        return {
            "buy_depth": self._calculate_buy_depth(order_book),
            "sell_depth": self._calculate_sell_depth(order_book),
            "liquidity_score": liquidity,
            "slippage": slippage,
        }

    async def generate_market_insights(self, token: str) -> Dict:
        conditions = await self.analyze_market_conditions(token)
        depth = await self.analyze_market_depth(token)
        correlations = await self._analyze_correlations(token)

        return {
            "market_conditions": conditions.__dict__,
            "market_depth": depth,
            "correlations": correlations,
            "opportunities": await self._identify_opportunities(conditions, depth),
            "risks": await self._identify_risks(conditions, depth),
        }
