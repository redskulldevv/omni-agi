from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


@dataclass
class DealMetrics:
    deal_id: str
    stage: str
    time_in_stage: int
    total_time: int
    conversion_probability: float
    investment_size: float
    team_score: float
    tech_score: float
    market_score: float


class MetricsTracker:
    def __init__(self):
        self.metrics = pd.DataFrame()
        self.kpis = {}

    async def track_deal(self, metrics: DealMetrics):
        df = pd.DataFrame([metrics.__dict__])
        self.metrics = pd.concat([self.metrics, df], ignore_index=True)
        await self._update_kpis()

    async def _update_kpis(self):
        self.kpis = {
            "avg_deal_time": self.metrics["total_time"].mean(),
            "conversion_rate": len(self.metrics[self.metrics["stage"] == "closed"])
            / len(self.metrics),
            "avg_investment": self.metrics[self.metrics["stage"] == "closed"][
                "investment_size"
            ].mean(),
            "pipeline_value": self.metrics[self.metrics["stage"] != "rejected"][
                "investment_size"
            ].sum(),
        }

    async def get_stage_metrics(self, stage: str) -> Dict:
        stage_data = self.metrics[self.metrics["stage"] == stage]
        return {
            "count": len(stage_data),
            "avg_time": stage_data["time_in_stage"].mean(),
            "total_value": stage_data["investment_size"].sum(),
        }
