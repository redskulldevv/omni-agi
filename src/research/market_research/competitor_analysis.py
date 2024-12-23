from dataclasses import dataclass
from typing import Dict, List
import pandas as pd


@dataclass
class Competitor:
    name: str
    token: str
    tvl: float
    volume_24h: float
    users: int
    features: List[str]
    metrics: Dict[str, float]


class CompetitorAnalyzer:
    def __init__(self):
        self.competitors = {}
        self.metrics_history = pd.DataFrame()

    async def analyze_competitor(self, competitor_id: str) -> Competitor:
        metrics = await self._fetch_competitor_metrics(competitor_id)
        features = await self._analyze_features(competitor_id)
        users = await self._analyze_user_metrics(competitor_id)

        return Competitor(
            name=metrics["name"],
            token=metrics["token"],
            tvl=metrics["tvl"],
            volume_24h=metrics["volume_24h"],
            users=users,
            features=features,
            metrics=metrics,
        )

    async def generate_competitive_analysis(self) -> Dict:
        market_share = self._calculate_market_share()
        feature_comparison = self._compare_features()
        growth_analysis = self._analyze_growth_trends()

        return {
            "market_share": market_share,
            "feature_comparison": feature_comparison,
            "growth_analysis": growth_analysis,
            "recommendations": self._generate_recommendations(),
        }

    def _calculate_market_share(self) -> Dict:
        total_tvl = sum(comp.tvl for comp in self.competitors.values())
        total_volume = sum(comp.volume_24h for comp in self.competitors.values())

        return {
            comp.name: {
                "tvl_share": (comp.tvl / total_tvl) * 100,
                "volume_share": (comp.volume_24h / total_volume) * 100,
            }
            for comp in self.competitors.values()
        }
