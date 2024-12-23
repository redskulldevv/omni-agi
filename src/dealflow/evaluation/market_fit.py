from dataclasses import dataclass
from typing import Dict, List
import pandas as pd


@dataclass
class MarketAnalysis:
    market_size: float
    growth_rate: float
    competition: List[str]
    moat: str
    score: float


class MarketFitAnalyzer:
    def __init__(self):
        self.market_data = pd.DataFrame()
        self.scoring_weights = {
            "market_size": 0.3,
            "growth_rate": 0.2,
            "competition": 0.2,
            "moat": 0.3,
        }

    async def analyze_market_fit(self, project_data: Dict) -> MarketAnalysis:
        market_size = await self._calculate_market_size(project_data)
        growth_rate = await self._analyze_growth_rate(project_data)
        competition = await self._analyze_competition(project_data)
        moat = await self._evaluate_moat(project_data)

        score = self._calculate_score(
            {
                "market_size": market_size,
                "growth_rate": growth_rate,
                "competition": len(competition),
                "moat": self._moat_score(moat),
            }
        )

        return MarketAnalysis(
            market_size=market_size,
            growth_rate=growth_rate,
            competition=competition,
            moat=moat,
            score=score,
        )

    def _calculate_score(self, metrics: Dict) -> float:
        return sum(
            metrics[key] * self.scoring_weights[key] for key in self.scoring_weights
        )
