import tweepy
from typing import Dict, List, Optional
import asyncio
from datetime import datetime


class TwitterManager:
    def __init__(self, api_keys: Dict[str, str]):
        auth = tweepy.OAuthHandler(
            api_keys["consumer_key"], api_keys["consumer_secret"]
        )
        auth.set_access_token(api_keys["access_token"], api_keys["access_token_secret"])
        self.api = tweepy.API(auth)
        self.client = tweepy.Client(
            bearer_token=api_keys["bearer_token"],
            consumer_key=api_keys["consumer_key"],
            consumer_secret=api_keys["consumer_secret"],
            access_token=api_keys["access_token"],
            access_token_secret=api_keys["access_token_secret"],
        )
        self.tweet_queue = asyncio.Queue()

    async def start(self):
        asyncio.create_task(self._process_queue())

    async def post_tweet(self, content: str) -> Optional[str]:
        try:
            tweet = await asyncio.to_thread(self.client.create_tweet, text=content)
            return str(tweet.data["id"])
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return None

    async def schedule_tweet(self, content: str, timestamp: float):
        await self.tweet_queue.put({"content": content, "timestamp": timestamp})

    async def get_mentions(self) -> List[Dict]:
        mentions = await asyncio.to_thread(
            self.client.get_users_mentions, self.client.get_me().data.id
        )
        return [mention.data for mention in mentions.data] if mentions.data else []

    async def analyze_sentiment(self, query: str) -> float:
        tweets = await asyncio.to_thread(
            self.client.search_recent_tweets, query=query, max_results=100
        )
        # Implement sentiment analysis
        return 0.0

    async def _process_queue(self):
        while True:
            tweet = await self.tweet_queue.get()
            current_time = datetime.now().timestamp()

            if current_time >= tweet["timestamp"]:
                await self.post_tweet(tweet["content"])
            else:
                await self.tweet_queue.put(tweet)

            await asyncio.sleep(60)
