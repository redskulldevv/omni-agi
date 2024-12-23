from typing import Dict, List
import asyncio
from datetime import datetime
import aiohttp
import pandas as pd


class ProjectScanner:
    def __init__(self, sources: Dict[str, str]):
        self.sources = sources
        self.scanned_projects = pd.DataFrame()

    async def scan_sources(self) -> pd.DataFrame:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for source_name, url in self.sources.items():
                task = asyncio.create_task(self._scan_source(session, source_name, url))
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        all_projects = pd.concat(results, ignore_index=True)
        self.scanned_projects = all_projects
        return all_projects

    async def _scan_source(
        self, session: aiohttp.ClientSession, source_name: str, url: str
    ) -> pd.DataFrame:
        try:
            if source_name == "github":
                return await self._scan_github(session)
            elif source_name == "defillama":
                return await self._scan_defillama(session)
            elif source_name == "twitter":
                return await self._scan_twitter(session)
        except Exception as e:
            print(f"Error scanning {source_name}: {e}")
            return pd.DataFrame()

    async def fetch_project_details(self, project_id: str) -> Dict:
        try:
            github_data = await self._fetch_github_data(project_id)
            defi_data = await self._fetch_defi_metrics(project_id)
            social_data = await self._fetch_social_metrics(project_id)

            return {
                "github": github_data,
                "defi": defi_data,
                "social": social_data,
                "last_updated": datetime.now(),
            }
        except Exception as e:
            print(f"Error fetching details for {project_id}: {e}")
            return {}

    async def monitor_projects(self, project_ids: List[str]):
        while True:
            updates = []
            for project_id in project_ids:
                details = await self.fetch_project_details(project_id)
                updates.append(details)

            self._update_project_data(updates)
            await asyncio.sleep(3600)  # Update hourly

    def _update_project_data(self, updates: List[Dict]):
        for update in updates:
            idx = self.scanned_projects["id"] == update["id"]
            self.scanned_projects.loc[idx] = update

    async def get_trending_projects(self, timeframe: str = "24h") -> pd.DataFrame:
        metrics = {
            "github_growth": self._calculate_growth("github_stars"),
            "tvl_growth": self._calculate_growth("tvl"),
            "social_growth": self._calculate_growth("social_engagement"),
        }

        trending = self.scanned_projects.copy()
        for metric, values in metrics.items():
            trending[metric] = values

        trending["trend_score"] = sum(trending[metric] for metric in metrics.keys())

        return trending.sort_values("trend_score", ascending=False)
