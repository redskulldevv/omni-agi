import tweepy
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Tweet:
    """Data class for Tweet information"""
    id: str
    text: str
    created_at: datetime
    author_id: str
    metrics: Dict[str, int]
    referenced_tweets: Optional[List[Dict]] = None
    conversation_id: Optional[str] = None

class TwitterAnalytics:
    """Analytics for Twitter engagement and performance"""
    
    def __init__(self):
        self.engagement_scores: Dict[str, float] = {}
        
    def calculate_engagement_rate(self, metrics: Dict[str, int]) -> float:
        """Calculate engagement rate from tweet metrics"""
        total_engagement = sum([
            metrics.get('like_count', 0),
            metrics.get('retweet_count', 0),
            metrics.get('reply_count', 0),
            metrics.get('quote_count', 0)
        ])
        impressions = metrics.get('impression_count', 1)
        return (total_engagement / impressions) * 100
    
    def analyze_best_time(self, tweets: List[Tweet]) -> Dict[str, List[int]]:
        """Analyze best posting times based on engagement"""
        engagement_by_hour = {str(i): [] for i in range(24)}
        
        for tweet in tweets:
            hour = tweet.created_at.hour
            engagement = self.calculate_engagement_rate(tweet.metrics)
            engagement_by_hour[str(hour)].append(engagement)
            
        return {
            hour: sum(engagements)/len(engagements) if engagements else 0 
            for hour, engagements in engagement_by_hour.items()
        }

class TwitterClient:
    """Twitter API client for AGI agent interactions"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str,
        access_token_secret: str,
        bearer_token: str
    ):
        # Initialize API v1 client
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
        
        # Initialize API v2 client
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        self.analytics = TwitterAnalytics()
        
    async def post_tweet(
        self,
        text: str,
        reply_to: Optional[str] = None,
        media_ids: Optional[List[str]] = None
    ) -> Tweet:
        """Post a new tweet"""
        try:
            response = self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to,
                media_ids=media_ids
            )
            
            tweet_data = response.data
            logger.info(f"Posted tweet: {tweet_data['id']}")
            
            return Tweet(
                id=tweet_data['id'],
                text=text,
                created_at=datetime.now(),
                author_id=tweet_data['author_id'],
                metrics={},
                conversation_id=tweet_data.get('conversation_id')
            )
            
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            raise
            
    async def get_mentions(
        self,
        since_id: Optional[str] = None,
        max_results: int = 100
    ) -> List[Tweet]:
        """Get recent mentions of the agent"""
        try:
            mentions = self.client.get_users_mentions(
                self.client.get_me().data.id,
                since_id=since_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'referenced_tweets', 'conversation_id']
            )
            
            return [
                Tweet(
                    id=tweet.id,
                    text=tweet.text,
                    created_at=tweet.created_at,
                    author_id=tweet.author_id,
                    metrics=tweet.public_metrics,
                    referenced_tweets=tweet.referenced_tweets,
                    conversation_id=tweet.conversation_id
                )
                for tweet in mentions.data or []
            ]
            
        except Exception as e:
            logger.error(f"Error getting mentions: {e}")
            raise
            
    async def get_tweet_metrics(self, tweet_id: str) -> Dict[str, int]:
        """Get metrics for a specific tweet"""
        try:
            tweet = self.client.get_tweet(
                tweet_id,
                tweet_fields=['public_metrics']
            ).data
            
            return tweet.public_metrics
            
        except Exception as e:
            logger.error(f"Error getting tweet metrics: {e}")
            raise
            
    async def follow_user(self, user_id: str):
        """Follow a user"""
        try:
            self.client.follow_user(user_id)
            logger.info(f"Followed user: {user_id}")
        except Exception as e:
            logger.error(f"Error following user: {e}")
            raise
            
    async def analyze_audience(self) -> Dict[str, any]:
        """Analyze follower demographics and engagement"""
        try:
            followers = self.client.get_users_followers(
                self.client.get_me().data.id,
                user_fields=['public_metrics', 'description', 'location']
            ).data
            
            analysis = {
                'total_followers': len(followers),
                'engagement_rate': 0,
                'locations': {},
                'influential_followers': []
            }
            
            for follower in followers:
                # Track locations
                if follower.location:
                    analysis['locations'][follower.location] = \
                        analysis['locations'].get(follower.location, 0) + 1
                
                # Track influential followers
                if follower.public_metrics['followers_count'] > 1000:
                    analysis['influential_followers'].append({
                        'id': follower.id,
                        'followers_count': follower.public_metrics['followers_count']
                    })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audience: {e}")
            raise
            
    async def get_trending_topics(self, woeid: int = 1) -> List[str]:
        """Get current trending topics"""
        try:
            trends = self.api.get_place_trends(woeid)[0]['trends']
            return [trend['name'] for trend in trends]
        except Exception as e:
            logger.error(f"Error getting trends: {e}")
            raise
            
    async def analyze_tweet_performance(self, tweet: Tweet) -> Dict[str, Union[float, str]]:
        """Analyze the performance of a tweet"""
        metrics = await self.get_tweet_metrics(tweet.id)
        engagement_rate = self.analytics.calculate_engagement_rate(metrics)
        
        performance = {
            'engagement_rate': engagement_rate,
            'performance_score': 'high' if engagement_rate > 2.0 else 'medium' if engagement_rate > 1.0 else 'low'
        }
        
        return performance