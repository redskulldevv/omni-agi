from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime

from dealflow.tracking.metrics import DealMetrics, MetricsTracker


class DealStage(Enum):
    SOURCED = "sourced"
    SCREENING = "screening"
    DEEP_DIVE = "deep_dive"
    COMMITTEE = "committee"
    NEGOTIATION = "negotiation"
    CLOSED = "closed"
    REJECTED = "rejected"


@dataclass
class Deal:
    id: str
    name: str
    stage: DealStage
    investment_size: float
    entry_date: datetime
    last_updated: datetime
    team: Dict
    metrics: Dict
    notes: List[str]


class PipelineManager:
    def __init__(self, metrics_tracker: MetricsTracker):
        self.deals: Dict[str, Deal] = {}
        self.metrics_tracker = metrics_tracker
        self.stage_limits = {
            DealStage.SCREENING: 20,
            DealStage.DEEP_DIVE: 10,
            DealStage.COMMITTEE: 5,
        }

    async def add_deal(self, deal: Deal):
        self.deals[deal.id] = deal
        await self._track_metrics(deal)

    async def update_stage(self, deal_id: str, new_stage: DealStage):
        if deal_id not in self.deals:
            raise ValueError(f"Deal {deal_id} not found")

        deal = self.deals[deal_id]
        old_stage = deal.stage

        if await self._can_move_to_stage(new_stage):
            deal.stage = new_stage
            deal.last_updated = datetime.now()
            await self._track_metrics(deal)
            await self._notify_stage_change(deal, old_stage, new_stage)

    async def _can_move_to_stage(self, stage: DealStage) -> bool:
        if stage not in self.stage_limits:
            return True

        current_count = len([d for d in self.deals.values() if d.stage == stage])
        return current_count < self.stage_limits[stage]

    async def get_pipeline_summary(self) -> Dict:
        summary = {}
        for stage in DealStage:
            stage_deals = [d for d in self.deals.values() if d.stage == stage]
            summary[stage.value] = {
                "count": len(stage_deals),
                "value": sum(d.investment_size for d in stage_deals),
            }
        return summary

    async def get_deal_velocity(self) -> Dict:
        velocities = {}
        for stage in DealStage:
            stage_deals = [d for d in self.deals.values() if d.stage == stage]
            if stage_deals:
                avg_time = sum(
                    (d.last_updated - d.entry_date).days for d in stage_deals
                ) / len(stage_deals)
                velocities[stage.value] = avg_time
        return velocities

    async def _track_metrics(self, deal: Deal):
        metrics = DealMetrics(
            deal_id=deal.id,
            stage=deal.stage.value,
            time_in_stage=(datetime.now() - deal.entry_date).days,
            total_time=(datetime.now() - deal.entry_date).days,
            conversion_probability=self._calculate_probability(deal),
            investment_size=deal.investment_size,
            team_score=deal.metrics.get("team_score", 0),
            tech_score=deal.metrics.get("tech_score", 0),
            market_score=deal.metrics.get("market_score", 0),
        )
        await self.metrics_tracker.track_deal(metrics)
