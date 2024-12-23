from typing import Dict, List
import pandas as pd
from datetime import datetime, timedelta


class MetricsTracker:
    def __init__(self):
        self.metrics: Dict[str, pd.DataFrame] = {
            "user_growth": pd.DataFrame(),
            "token_metrics": pd.DataFrame(),
            "engagement": pd.DataFrame(),
        }

    async def track_metric(self, category: str, data: Dict):
        if category not in self.metrics:
            self.metrics[category] = pd.DataFrame()

        df = pd.DataFrame([{**data, "timestamp": datetime.now()}])

        self.metrics[category] = pd.concat([self.metrics[category], df]).reset_index(
            drop=True
        )

    async def get_growth_rate(self, metric: str, period: str) -> float:
        df = self.metrics[metric]
        if df.empty:
            return 0.0

        now = datetime.now()
        if period == "daily":
            start = now - timedelta(days=1)
        elif period == "weekly":
            start = now - timedelta(weeks=1)
        elif period == "monthly":
            start = now - timedelta(days=30)

        period_data = df[df["timestamp"] >= start]
        if period_data.empty:
            return 0.0

        start_value = period_data.iloc[0]["value"]
        end_value = period_data.iloc[-1]["value"]

        return ((end_value - start_value) / start_value) * 100

    async def calculate_retention(self, days: int) -> float:
        df = self.metrics["user_growth"]
        if df.empty:
            return 0.0

        now = datetime.now()
        start = now - timedelta(days=days)

        cohort = df[df["timestamp"] >= start]
        if cohort.empty:
            return 0.0

        initial_users = len(cohort["user_id"].unique())
        active_users = len(
            cohort[cohort["timestamp"] >= (now - timedelta(days=1))]["user_id"].unique()
        )

        return (active_users / initial_users) * 100

    async def get_campaign_metrics(self, campaign_id: str) -> Dict:
        metrics = {}
        for category, df in self.metrics.items():
            campaign_data = df[df["campaign_id"] == campaign_id]
            if not campaign_data.empty:
                metrics[category] = {
                    "total": len(campaign_data),
                    "success_rate": (
                        len(campaign_data[campaign_data["success"] == True])
                        / len(campaign_data)
                    )
                    * 100,
                    "average_value": campaign_data["value"].mean(),
                }
        return metrics

    async def export_metrics(self, start_date: datetime, end_date: datetime) -> Dict:
        export = {}
        for category, df in self.metrics.items():
            period_data = df[
                (df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)
            ]
            export[category] = period_data.to_dict("records")
        return export
