# src/models/groq.py

from groq import Groq
from typing import Dict, List, Optional, Any, Union
import logging
import json
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import partial

logger = logging.getLogger(__name__)

class GroqAI:
    """Groq AI service for agent integration"""

    def __init__(
        self,
        api_key: str,
        model: str = "mixtral-8x7b-32768",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        retry_attempts: int = 3,
    ):
        if not api_key:
            raise ValueError("GROQ_API_KEY not provided")
        
        self.client = Groq(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.retry_attempts = retry_attempts
        self.conversation_history: List[Dict[str, Any]] = []
        self._initialized = False
        self._loop = asyncio.get_event_loop()

    async def initialize(self) -> None:
        """Initialize and verify Groq connection"""
        try:
            # Test connection with a simple prompt
            test_response = await self._run_completion(
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
                temperature=0.1
            )
            
            if test_response:
                self._initialized = True
                logger.info("GroqAI initialized successfully")
            else:
                raise RuntimeError("Failed to get response from Groq")
                
        except Exception as e:
            logger.error(f"Failed to initialize GroqAI: {e}")
            self._initialized = False
            raise

    async def _run_completion(self, **kwargs) -> Optional[str]:
        """Run Groq completion in thread pool"""
        try:
            # Run the synchronous Groq API call in a thread pool
            response = await self._loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model,
                    **kwargs
                )
            )
            
            return response.choices[0].message.content if response.choices else None
            
        except Exception as e:
            logger.error(f"Error in Groq completion: {e}")
            raise

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
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response from Groq"""
        if not self._initialized:
            await self.initialize()

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            if context:
                messages.append(
                    {"role": "system", "content": f"Context: {json.dumps(context)}"}
                )

            messages.extend(self.conversation_history[-5:])
            messages.append({"role": "user", "content": prompt})

            response_text = await self._run_completion(
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature
            )

            if response_text:
                self.conversation_history.extend([
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response_text}
                ])
                return response_text
            else:
                raise RuntimeError("Empty response from Groq")

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def analyze_market(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions"""
        if not self._initialized:
            await self.initialize()

        try:
            prompt = f"""
            Analyze these market conditions:
            {json.dumps(context, indent=2)}

            Return JSON with:
            - sentiment (string)
            - confidence (float 0-1)
            - key_risks (list)
            - opportunities (list)
            - recommended_actions (list)
            """

            response = await self.generate_response(
                prompt=prompt,
                temperature=0.3,
                max_tokens=500
            )

            return json.loads(response)

        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Union[float, str]]:
        """Analyze sentiment of text"""
        if not self._initialized:
            await self.initialize()

        try:
            prompt = f"""
            Analyze sentiment of: {text}
            Return only JSON:
            {{"score": float (-1 to 1), "label": "positive/negative/neutral", "confidence": float (0-1)}}
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

    async def generate_content(self, 
                             template: str,
                             context: Optional[Dict[str, Any]] = None,
                             parameters: Optional[Dict[str, Any]] = None) -> str:
        """Generate content from template"""
        if not self._initialized:
            await self.initialize()

        try:
            # Fill template parameters if provided
            if parameters:
                template = template.format(**parameters)

            return await self.generate_response(
                prompt=template,
                context=context,
                temperature=0.7
            )

        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            self.clear_history()
            self._initialized = False
            logger.info("GroqAI cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up GroqAI: {e}")