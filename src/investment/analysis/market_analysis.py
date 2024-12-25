# src/investment/analysis/market_analysis.py
import asyncio
import json
from typing import Any, Dict, Optional
import logging
import aiohttp
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

class MarketAnalyzer:
    def __init__(self, data_sources: Optional[Dict[str, str]] = None):
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.jupiter_api_base = "https://quote-api.jup.ag/v6"
        self.data_sources = data_sources or {
            "prices": "coingecko",
            "volume": "coingecko",
            "social": "twitter"
        }
        self.initialized = False

    @property
    async def session(self) -> aiohttp.ClientSession:
        """Get or create session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=aiohttp.TCPConnector(ssl=False)  # Disable SSL verification if needed
            )
        return self._session

    async def initialize(self) -> None:
        """Initialize the market analyzer"""
        try:
            # Perform any necessary initialization steps here
            self.initialized = True
            self.logger.info("MarketAnalyzer initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MarketAnalyzer: {e}")
            raise

    async def get_market_overview(self) -> Dict[str, Any]:
        """Get an overview of the market"""
        try:
            market_data = await self.get_market_data()
            return market_data
        except Exception as e:
            self.logger.error(f"Error getting market overview: {e}")
            raise

    async def _update_engagement_metrics(self, username: str):
        """Update engagement metrics for the given username"""
        try:
            metrics = await self._get_twitter_metrics(username)
            # Process metrics
        except Exception as e:
            self.logger.error(f"Error updating engagement metrics: {e}")

    async def get_market_data(self) -> Dict[str, Any]:
        """Get market data from data sources"""
        try:
            if not self.initialized:
                raise RuntimeError("MarketAnalyzer not initialized")

            market_data = {}
            if "prices" in self.data_sources:
                market_data["prices"] = await self.fetch_price("solana")
            if "volume" in self.data_sources:
                market_data["volume"] = await self.fetch_volume()
            if "social" in self.data_sources:
                market_data["social"] = self._fetch_social_sentiment()

            return market_data
        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def fetch_price(self, token: str) -> Dict[str, Any]:
        """Fetch token price with retries"""
        try:
            session = await self.session
            url = f"{self.jupiter_api_base}/price"
            params = {"ids": token.lower()}

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data.get('data', {}).get('price'), (int, float)):
                        return {
                            "price": float(data['data']['price']),
                            "success": True
                        }
                elif response.status == 404:
                    self.logger.error(f"Failed to fetch price for {token}: {response.status}")
                    return {"price": 0.0, "success": False}
                elif response.status == 429:
                    self.logger.warning("Rate limit reached for Jupiter API")
                    await asyncio.sleep(1)  # Add delay before retry

                self.logger.warning(f"Failed to fetch price for {token}: {response.status}")

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching price for {token}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error fetching price for {token}: {str(e)}")
            return {"price": 0.0, "success": False}

        return {"price": 0.0, "success": False}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def fetch_volume(self) -> Dict[str, Any]:
        """Fetch trading volume with validation"""
        try:
            session = await self.session
            url = f"{self.coingecko_api}/simple/price"
            params = {
                "ids": "solana",
                "vs_currencies": "usd",
                "include_24hr_vol": "true"
            }

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    volume = data.get('solana', {}).get('usd_24h_vol', 0)

                    if isinstance(volume, (int, float)):
                        return {
                            "volume": float(volume),
                            "success": True
                        }

                    self.logger.error(f"Invalid volume data type: {type(volume)}")
                elif response.status == 429:
                    self.logger.warning("Rate limit reached for CoinGecko API")
                    await asyncio.sleep(1)  # Add delay before retry

                self.logger.warning(f"Failed to fetch volume: {response.status}")

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching volume: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Volume fetch error: {str(e)}")

        return {"volume": 0.0, "success": False}

    async def cleanup(self):
        """Cleanup resources"""
        if self._session and not self._session.closed:
            await self._session.close()

    def _fetch_social_sentiment(self) -> Dict[str, Any]:
        """Fetch social sentiment data from the data source"""
        try:
            # Example implementation for fetching social sentiment from Twitter
            # This is a placeholder and should be replaced with actual implementation
            return {
                "bitcoin": {"positive": 70, "negative": 30},
                "ethereum": {"positive": 65, "negative": 35}
            }
        except Exception as e:
            self.logger.error(f"Error fetching social sentiment: {e}")
            return {}

import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging
from datetime import datetime

class MarketFetcher:
    """Handles all market data fetching with proper error handling"""
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        
        # Correct SOL token addresses
        self.SOL_MINT = "So11111111111111111111111111111111111111112"
        self.USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        
        # API endpoints
        self.JUPITER_API = "https://quote-api.jup.ag/v6"
        self.COINGECKO_API = "https://api.coingecko.com/api/v3"

    @property
    async def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(ssl=False)
            )
        return self._session

    async def fetch_price(self, token: str) -> Dict[str, Any]:
        """Fetch token price with proper error handling"""
        try:
            session = await self.session
            
            # Build quote URL correctly
            quote_params = {
                'inputMint': self.SOL_MINT,
                'outputMint': self.USDC_MINT,
                'amount': '1000000000',  # 1 SOL
                'slippageBps': 50
            }
            
            url = f"{self.JUPITER_API}/quote"
            
            async with session.get(url, params=quote_params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'data' in data:
                        return {
                            'price': float(data['data']['outAmount']) / 1e9,
                            'success': True,
                            'timestamp': datetime.now().isoformat()
                        }
                
                self.logger.error(f"Failed to fetch price: {response.status}")
                return {
                    'price': 0.0,
                    'success': False,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching price: {str(e)}")
            return {
                'price': 0.0,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

    async def fetch_volume(self) -> Dict[str, Any]:
        """Fetch volume data with type checking"""
        try:
            session = await self.session
            url = f"{self.COINGECKO_API}/coins/solana"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract volume with type checking
                    volume = data.get('market_data', {}).get('total_volume', {}).get('usd', 0)
                    
                    if not isinstance(volume, (int, float)):
                        volume = float(volume) if volume else 0.0
                    
                    return {
                        'volume': volume,
                        'success': True,
                        'timestamp': datetime.now().isoformat()
                    }
                
                return {
                    'volume': 0.0,
                    'success': False,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error fetching volume: {str(e)}")
            return {
                'volume': 0.0,
                'success': False,
                'timestamp': datetime.now().isoformat()
            }

    async def cleanup(self):
        """Cleanup resources"""
        if self._session and not self._session.closed:
            await self._session.close()