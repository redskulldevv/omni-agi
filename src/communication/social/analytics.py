from typing import Any, Dict, List, Union
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass
import logging
from textblob import TextBlob

logger = logging.getLogger(__name__)


@dataclass
class EngagementMetrics:
    """Data class for engagement metrics"""

    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    engagement_rate: float = 0.0
    sentiment_score: float = 0.0


class SocialAnalytics:
    """Analytics for social media engagement and performance"""

    def __init__(self):
        self.platforms = ["twitter", "discord"]
        self.metrics_history: Dict[str, List[EngagementMetrics]] = defaultdict(list)
        self.trend_cache: Dict[str, Dict] = {}

    async def analyze_engagement(
        self, platform: str, data: List[Dict], timeframe: str = "24h"
    ) -> Dict[str, Union[float, Dict]]:
        """Analyze engagement metrics across platforms"""
        try:
            metrics = EngagementMetrics()

            for item in data:
                # Aggregate engagement metrics
                metrics.likes += item.get("likes", 0)
                metrics.comments += item.get("comments", 0)
                metrics.shares += item.get("shares", 0)
                metrics.views += item.get("views", 0)

                # Calculate sentiment
                if "text" in item:
                    blob = TextBlob(item["text"])
                    metrics.sentiment_score += blob.sentiment.polarity

            # Calculate averages
            total_items = len(data)
            if total_items > 0:
                metrics.sentiment_score /= total_items
                metrics.engagement_rate = self._calculate_engagement_rate(metrics)

            # Store metrics history
            self.metrics_history[platform].append(metrics)

            return {
                "total_engagement": metrics.likes + metrics.comments + metrics.shares,
                "engagement_rate": metrics.engagement_rate,
                "sentiment": {
                    "score": metrics.sentiment_score,
                    "label": self._get_sentiment_label(metrics.sentiment_score),
                },
                "platform_metrics": vars(metrics),
            }

        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            raise

    async def detect_trends(
        self, platform: str, data: List[Dict], min_mentions: int = 3
    ) -> Dict[str, List[str]]:
        """Detect trending topics and hashtags"""
        try:
            mentions = defaultdict(int)
            hashtags = defaultdict(int)

            for item in data:
                # Extract mentions
                if "mentions" in item:
                    for mention in item["mentions"]:
                        mentions[mention] += 1

                # Extract hashtags
                if "hashtags" in item:
                    for tag in item["hashtags"]:
                        hashtags[tag] += 1

            # Filter trends
            trending_mentions = [
                mention for mention, count in mentions.items() if count >= min_mentions
            ]

            trending_hashtags = [
                tag for tag, count in hashtags.items() if count >= min_mentions
            ]

            self.trend_cache[platform] = {
                "mentions": trending_mentions,
                "hashtags": trending_hashtags,
                "timestamp": datetime.now(),
            }

            return {
                "trending_mentions": trending_mentions,
                "trending_hashtags": trending_hashtags,
            }

        except Exception as e:
            logger.error(f"Error detecting trends: {e}")
            raise

    async def analyze_growth(
        self,
        platform: str,
        current_metrics: Dict[str, int],
        previous_metrics: Dict[str, int],
    ) -> Dict[str, Union[float, str]]:
        """Analyze growth and changes in metrics"""
        try:
            growth_metrics = {}

            for metric, current_value in current_metrics.items():
                if metric in previous_metrics:
                    previous_value = previous_metrics[metric]
                    if previous_value > 0:
                        growth_rate = (
                            (current_value - previous_value) / previous_value
                        ) * 100
                        growth_metrics[metric] = {
                            "rate": growth_rate,
                            "trend": "up" if growth_rate > 0 else "down",
                            "change": current_value - previous_value,
                        }

            return growth_metrics

        except Exception as e:
            logger.error(f"Error analyzing growth: {e}")
            raise

    async def get_performance_report(
        self, platform: str, timeframe: str = "7d"
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            metrics_history = self.metrics_history[platform]
            if not metrics_history:
                return {}

            # Calculate average metrics
            avg_metrics = EngagementMetrics()
            for metrics in metrics_history:
                avg_metrics.likes += metrics.likes
                avg_metrics.comments += metrics.comments
                avg_metrics.shares += metrics.shares
                avg_metrics.views += metrics.views
                avg_metrics.sentiment_score += metrics.sentiment_score

            total_periods = len(metrics_history)
            for field in vars(avg_metrics):
                current_value = getattr(avg_metrics, field)
                setattr(avg_metrics, field, current_value / total_periods)

            # Generate report
            return {
                "summary": {
                    "average_engagement_rate": avg_metrics.engagement_rate,
                    "sentiment_trend": self._get_sentiment_label(
                        avg_metrics.sentiment_score
                    ),
                    "total_interactions": sum(
                        [m.likes + m.comments + m.shares for m in metrics_history]
                    ),
                },
                "metrics_trend": self._calculate_metrics_trend(metrics_history),
                "recommendations": self._generate_recommendations(avg_metrics),
            }

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            raise

    def _calculate_engagement_rate(self, metrics: EngagementMetrics) -> float:
        """Calculate engagement rate"""
        if metrics.views == 0:
            return 0.0
        return (
            (metrics.likes + metrics.comments + metrics.shares) / metrics.views
        ) * 100

    def _get_sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.2:
            return "positive"
        elif score < -0.2:
            return "negative"
        return "neutral"

    def _calculate_metrics_trend(
        self, metrics_history: List[EngagementMetrics]
    ) -> Dict[str, str]:
        """Calculate trends for each metric"""
        trends = {}
        if len(metrics_history) < 2:
            return trends

        current = metrics_history[-1]
        previous = metrics_history[-2]

        for field in vars(current):
            curr_value = getattr(current, field)
            prev_value = getattr(previous, field)

            if prev_value != 0:
                change = ((curr_value - prev_value) / prev_value) * 100
                trends[field] = "up" if change > 0 else "down"

        return trends

    def _generate_recommendations(self, metrics: EngagementMetrics) -> List[str]:
        """Generate recommendations based on metrics"""
        recommendations = []

        if metrics.engagement_rate < 1.0:
            recommendations.append(
                "Consider increasing interactive content to boost engagement"
            )

        if metrics.sentiment_score < 0:
            recommendations.append("Focus on positive messaging to improve sentiment")

        if metrics.comments < metrics.likes * 0.1:
            recommendations.append(
                "Encourage more discussions through questions and polls"
            )

        return recommendations
