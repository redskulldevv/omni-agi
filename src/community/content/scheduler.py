from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass

from community.content.generator import ContentGenerator


@dataclass
class ContentSchedule:
    content_type: str
    frequency: str  # daily, weekly, monthly
    time: str
    parameters: Dict
    last_posted: Optional[datetime] = None


class ContentScheduler:
    def __init__(self, generator: ContentGenerator):
        self.generator = generator
        self.schedules: List[ContentSchedule] = []
        self.posted_content: List[Dict] = []
        self._running = False

    def add_schedule(self, schedule: ContentSchedule):
        self.schedules.append(schedule)

    async def start(self):
        self._running = True
        await self._run_scheduler()

    async def stop(self):
        self._running = False

    async def _run_scheduler(self):
        while self._running:
            current_time = datetime.now()

            for schedule in self.schedules:
                if self._should_post(schedule, current_time):
                    content = await self.generator.generate_content(
                        schedule.content_type, schedule.parameters
                    )

                    await self._post_content(content)
                    schedule.last_posted = current_time

            await asyncio.sleep(60)  # Check every minute

    def _should_post(self, schedule: ContentSchedule, current_time: datetime) -> bool:
        if not schedule.last_posted:
            return True

        if schedule.frequency == "daily":
            next_post = schedule.last_posted + timedelta(days=1)
        elif schedule.frequency == "weekly":
            next_post = schedule.last_posted + timedelta(weeks=1)
        elif schedule.frequency == "monthly":
            next_post = schedule.last_posted + timedelta(days=30)

        scheduled_time = datetime.strptime(schedule.time, "%H:%M").time()
        current_scheduled_time = current_time.replace(
            hour=scheduled_time.hour,
            minute=scheduled_time.minute,
            second=0,
            microsecond=0,
        )

        return current_time >= next_post and current_time >= current_scheduled_time

    async def _post_content(self, content: Dict):
        self.posted_content.append(content)
        # Implement posting to social platforms
        print(f"Posted {content['type']} content: {content['content'][:100]}...")
