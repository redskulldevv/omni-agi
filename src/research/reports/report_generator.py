from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from research.reports.templates import TemplateManager


@dataclass
class ReportConfig:
    type: str
    timeframe: str
    sections: List[str]
    metrics: List[str]
    format: str = "markdown"


class ReportGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.reports_history = []

    async def generate_report(self, config: ReportConfig, data: Dict) -> str:
        report_data = await self._prepare_report_data(config, data)
        report = self.template_manager.render_template(
            f"{config.type}_report", report_data
        )

        await self._store_report(config, report)
        return report

    async def _prepare_report_data(self, config: ReportConfig, data: Dict) -> Dict:
        prepared_data = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
        }

        if config.type == "market":
            prepared_data.update(await self._prepare_market_data(data))
        elif config.type == "investment":
            prepared_data.update(await self._prepare_investment_data(data))

        return prepared_data

    async def _prepare_market_data(self, data: Dict) -> Dict:
        return {
            "market_cap": data.get("market_cap", 0),
            "volume_24h": data.get("volume_24h", 0),
            "sentiment": data.get("sentiment", "neutral"),
            "key_metrics": self._format_metrics(data.get("metrics", {})),
            "trends": data.get("trends", []),
            "opportunities": data.get("opportunities", []),
            "risks": data.get("risks", []),
        }

    async def _prepare_investment_data(self, data: Dict) -> Dict:
        return {
            "portfolio_value": data.get("portfolio_value", 0),
            "period_return": data.get("period_return", 0),
            "risk_adjusted_return": data.get("risk_adjusted_return", 0),
            "positions": data.get("positions", []),
            "recommendations": data.get("recommendations", []),
        }

    def _format_metrics(self, metrics: Dict) -> List[Dict]:
        return [{"name": name, "value": value} for name, value in metrics.items()]

    async def generate_summary(self, reports: List[str]) -> str:
        """Generate executive summary from multiple reports"""
        summaries = []
        for report in reports:
            summary = await self._extract_key_points(report)
            summaries.append(summary)

        return self._combine_summaries(summaries)
