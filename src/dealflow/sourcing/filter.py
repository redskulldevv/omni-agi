from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd


@dataclass
class FilterCriteria:
    min_github_stars: int
    min_tvl: float
    required_chains: List[str]
    min_team_size: int
    required_audits: bool
    max_age_months: int


class ProjectFilter:
    def __init__(self, criteria: FilterCriteria):
        self.criteria = criteria
        self.filtered_projects = pd.DataFrame()

    async def apply_filters(self, projects: pd.DataFrame) -> pd.DataFrame:
        filtered = projects.copy()

        filtered = filtered[
            (filtered["github_stars"] >= self.criteria.min_github_stars)
            & (filtered["tvl"] >= self.criteria.min_tvl)
            & (filtered["team_size"] >= self.criteria.min_team_size)
            & (filtered["age_months"] <= self.criteria.max_age_months)
        ]

        if self.criteria.required_audits:
            filtered = filtered[filtered["has_audit"] == True]

        filtered = filtered[
            filtered["chains"].apply(
                lambda x: all(chain in x for chain in self.criteria.required_chains)
            )
        ]

        self.filtered_projects = filtered
        return filtered

    async def rank_projects(self, weights: Dict[str, float]) -> pd.DataFrame:
        if self.filtered_projects.empty:
            return pd.DataFrame()

        for metric, weight in weights.items():
            self.filtered_projects[f"{metric}_weighted"] = (
                self.filtered_projects[metric] * weight
            )

        self.filtered_projects["total_score"] = sum(
            self.filtered_projects[f"{metric}_weighted"] for metric in weights.keys()
        )

        return self.filtered_projects.sort_values("total_score", ascending=False)
