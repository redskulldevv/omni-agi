from anthropic import Anthropic
from typing import Dict, List, Optional, Any, Union
import logging
import json

logger = logging.getLogger(__name__)


class ClaudeAI:
    """Claude API integration for the AI agent"""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ):
        """Initialize Claude API client

        Args:
            api_key: Anthropic API key
            model: Model name to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.conversation_history: List[Dict[str, Any]] = []

    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response from Claude

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
                messages.append({"role": "system", "content": system_prompt})

            # Add context if provided
            if context:
                messages.append(
                    {"role": "system", "content": f"Context: {json.dumps(context)}"}
                )

            # Add conversation history
            messages.extend(self.conversation_history[-5:])  # Last 5 messages

            # Add current prompt
            messages.append({"role": "user", "content": prompt})

            # Generate response
            response = await self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

            # Store in history
            self.conversation_history.extend(
                [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": response.content},
                ]
            )

            return response.content

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Union[float, str]]:
        """Analyze text sentiment

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment score and label
        """
        try:
            prompt = f"""
            Analyze the sentiment of the following text and provide a score from -1.0 (very negative) to 1.0 (very positive).
            Also provide a label (positive/negative/neutral).

            Text: {text}

            Respond in JSON format:
            {{
                "score": float,
                "label": string
            }}
            """

            response = await self.generate_response(
                prompt=prompt,
                temperature=0.1,  # Lower temperature for more consistent analysis
            )

            return json.loads(response)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise

    async def analyze_market(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions

        Args:
            context: Market context information

        Returns:
            Analysis results
        """
        try:
            # Create market analysis prompt
            prompt = f"""
            Analyze the following market conditions and provide insights:

            Context: {json.dumps(context, indent=2)}

            Provide:
            1. Overall market sentiment
            2. Key trends
            3. Risk assessment
            4. Recommendations

            Respond in JSON format.
            """

            response = await self.generate_response(
                prompt=prompt, temperature=0.3  # Lower temperature for analysis
            )

            return json.loads(response)

        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            raise

    async def generate_social_post(
        self, topic: str, style: str, max_length: int = 280
    ) -> str:
        """Generate social media post

        Args:
            topic: Post topic
            style: Writing style
            max_length: Maximum length

        Returns:
            Generated post text
        """
        try:
            prompt = f"""
            Generate a {style} social media post about: {topic}

            Requirements:
            - Maximum length: {max_length} characters
            - Style: {style}
            - Include relevant hashtags
            - Be engaging and informative
            """

            response = await self.generate_response(
                prompt=prompt, max_tokens=max_length // 2  # Conservative token limit
            )

            # Ensure length limit
            if len(response) > max_length:
                response = response[: max_length - 3] + "..."

            return response

        except Exception as e:
            logger.error(f"Error generating social post: {e}")
            raise

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    async def get_embedding(self, text: str) -> List[float]:
        """Get text embedding

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = await self.client.embeddings.create(
                model="claude-3-embedding", input=text
            )

            return response.embedding

        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
