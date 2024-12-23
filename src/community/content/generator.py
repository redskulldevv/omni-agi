from typing import Dict, List
import asyncio
from anthropic import Anthropic
from datetime import datetime, timedelta


class ContentGenerator:
    def __init__(self, claude_api_key: str):
        self.claude = Anthropic(api_key=claude_api_key)
        self.templates = self._load_templates()

    async def generate_content(self, content_type: str, context: Dict) -> Dict:
        prompt = self.templates[content_type].format(**context)

        response = await self.claude.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "content": response.content,
            "type": content_type,
            "timestamp": datetime.now(),
            "context": context,
        }

    async def generate_market_update(self, market_data: Dict) -> Dict:
        return await self.generate_content("market_update", market_data)

    async def generate_education_content(self, topic: str) -> Dict:
        return await self.generate_content("education", {"topic": topic})

    async def generate_community_poll(self, topic: str) -> Dict:
        return await self.generate_content("poll", {"topic": topic})

    def _load_templates(self) -> Dict[str, str]:
        return {
            "market_update": """Create a market update post about {token}:
                Price: {price}
                24h Change: {change}
                Volume: {volume}
                Key Events: {events}""",
            "education": """Create educational content about {topic}
                focusing on key concepts and practical applications.""",
            "poll": """Create an engaging community poll about {topic}
                with 4 distinct options.""",
        }
