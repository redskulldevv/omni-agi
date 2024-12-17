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

            response = await self.client.messages.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
            )

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
        try:
            prompt = (
                "Analyze the sentiment of the following text and provide a score "
                "from -1.0 (very negative) to 1.0 (very positive). "
                "Also provide a label (positive/negative/neutral).\n\n"
                f"Text: {text}\n\n"
                "Respond in JSON format:\n"
                "{\n"
                '    "score": float,\n'
                '    "label": string\n'
                "}"
            )

            response = await self.generate_response(
                prompt=prompt,
                temperature=0.1,
            )

            return json.loads(response)

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            raise

    async def analyze_market(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = (
                "Analyze the following market conditions and provide insights:\n\n"
                f"Context: {json.dumps(context, indent=2)}\n\n"
                "Provide:\n"
                "1. Overall market sentiment\n"
                "2. Key trends\n"
                "3. Risk assessment\n"
                "4. Recommendations\n\n"
                "Respond in JSON format."
            )

            response = await self.generate_response(
                prompt=prompt,
                temperature=0.3,
            )

            return json.loads(response)

        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            raise

    async def generate_social_post(
        self,
        topic: str,
        style: str,
        max_length: int = 280,
    ) -> str:
        try:
            prompt = (
                f"Generate a {style} social media post about: {topic}\n\n"
                "Requirements:\n"
                f"- Maximum length: {max_length} characters\n"
                f"- Style: {style}\n"
                "- Include relevant hashtags\n"
                "- Be engaging and informative"
            )

            response = await self.generate_response(
                prompt=prompt,
                max_tokens=max_length // 2,
            )

            if len(response) > max_length:
                response = response[: max_length - 3] + "..."

            return response

        except Exception as e:
            logger.error(f"Error generating social post: {e}")
            raise

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []

    async def get_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model="claude-3-embedding",
                input=text,
            )

            return response.embedding

        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise
