from groq import Groq
from typing import Dict, List, Optional, Any, Union
import logging
import json
import asyncio
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class GroqAI:
    """Groq API integration for fast inference"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "mixtral-8x7b-32768",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        retry_attempts: int = 3
    ):
        """Initialize Groq API client
        
        Args:
            api_key: Groq API key
            model: Model name to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
            retry_attempts: Number of retry attempts
        """
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.retry_attempts = retry_attempts
        self.conversation_history: List[Dict[str, Any]] = []
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response from Groq
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instructions
            context: Optional context information
            temperature: Optional override for response temperature
            max_tokens: Optional override for max tokens
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Context: {json.dumps(context)}"
                })
            
            # Add conversation history
            messages.extend(self.conversation_history[-5:])  # Last 5 messages
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Generate completion
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )
            
            # Store in history
            self.conversation_history.extend([
                {
                    "role": "user",
                    "content": prompt
                },
                {
                    "role": "assistant",
                    "content": response.choices[0].message.content
                }
            ])
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
            
    async def analyze_market_fast(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Quick market analysis using Groq's fast inference
        
        Args:
            context: Market context information
            
        Returns:
            Analysis results
        """
        try:
            # Create focused market analysis prompt
            prompt = f"""
            Analyze these market conditions concisely:
            {json.dumps(context, indent=2)}
            
            Return JSON with:
            - sentiment (string)
            - confidence (float 0-1)
            - key_risks (list)
            - opportunities (list)
            """
            
            response = await self.generate_response(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500  # Limit response size for speed
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            raise
            
    async def process_social_signals(
        self,
        data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process social media signals rapidly
        
        Args:
            data: List of social media data points
            
        Returns:
            Processed signals and insights
        """
        try:
            prompt = f"""
            Analyze these social media signals quickly:
            {json.dumps(data[:10], indent=2)}  # Process first 10 for speed
            
            Return JSON with:
            - trending_topics (list)
            - sentiment_summary (string)
            - engagement_metrics (dict)
            """
            
            response = await self.generate_response(
                prompt=prompt,
                temperature=0.2,
                max_tokens=300
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error processing social signals: {e}")
            raise
            
    async def quick_sentiment(
        self,
        text: str
    ) -> Dict[str, Union[float, str]]:
        """Fast sentiment analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment score and label
        """
        try:
            prompt = f"""
            Quick sentiment analysis of: {text}
            Return only JSON:
            {{"score": float (-1 to 1), "label": "positive/negative/neutral"}}
            """
            
            response = await self.generate_response(
                prompt=prompt,
                temperature=0.1,
                max_tokens=100
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            raise
            
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        
    async def stream_response(
        self,
        prompt: str,
        callback: callable
    ):
        """Stream response with callback for each chunk
        
        Args:
            prompt: Input prompt
            callback: Function to call with each response chunk
        """
        try:
            response_stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            async for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    await callback(chunk.choices[0].delta.content)
                    
        except Exception as e:
            logger.error(f"Error in stream response: {e}")
            raise
