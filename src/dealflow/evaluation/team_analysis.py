from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TeamMember:
    name: str
    role: str
    experience: List[str]
    github: str
    linkedin: str
    score: float


class TeamAnalyzer:
    def __init__(self):
        self.github_client = None  # Initialize GitHub API client
        self.linkedin_client = None  # Initialize LinkedIn API client

    async def analyze_team(self, team_data: List[Dict]) -> List[TeamMember]:
        analyzed_team = []
        for member in team_data:
            github_score = await self._analyze_github(member["github"])
            linkedin_score = await self._analyze_linkedin(member["linkedin"])
            experience_score = self._evaluate_experience(member["experience"])

            score = (github_score + linkedin_score + experience_score) / 3

            analyzed_team.append(
                TeamMember(
                    name=member["name"],
                    role=member["role"],
                    experience=member["experience"],
                    github=member["github"],
                    linkedin=member["linkedin"],
                    score=score,
                )
            )
        return analyzed_team

    async def calculate_team_score(self, team: List[TeamMember]) -> float:
        weights = {"technical": 0.4, "business": 0.3, "product": 0.3}

        scores = {role: [] for role in weights}
        for member in team:
            role_category = self._categorize_role(member.role)
            scores[role_category].append(member.score)

        return sum(
            max(scores[role], default=0) * weight for role, weight in weights.items()
        )
