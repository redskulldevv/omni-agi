from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    TEXT = "text"
    COMMAND = "command"
    SYSTEM = "system"
    ERROR = "error"
    ANALYSIS = "analysis"


@dataclass
class Message:
    """Message data structure"""

    content: str
    type: MessageType
    sender: str
    timestamp: datetime
    metadata: Optional[Dict] = None
    reply_to: Optional[str] = None


class Conversation:
    """Manages a single conversation session"""

    def __init__(self, conversation_id: str):
        self.id = conversation_id
        self.messages: List[Message] = []
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.last_activity = datetime.now()

    def add_message(self, message: Message):
        """Add message to conversation"""
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_context(self) -> Dict[str, Any]:
        """Get conversation context"""
        return {
            "messages": self.messages[-5:],  # Last 5 messages for context
            "context": self.context,
            "duration": (datetime.now() - self.created_at).seconds,
        }


class ChatInterface:
    """Main chat interface for the AGI agent"""

    def __init__(
        self,
        ai_service: Any,  # Your AI service
        command_handlers: Dict[str, Callable] = None,
    ):
        self.ai_service = ai_service
        self.conversations: Dict[str, Conversation] = {}
        self.command_handlers = command_handlers or {}
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.TEXT: self._handle_text,
            MessageType.COMMAND: self._handle_command,
            MessageType.SYSTEM: self._handle_system,
        }

    async def process_message(
        self,
        content: str,
        sender: str,
        conversation_id: Optional[str] = None,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict] = None,
    ) -> Message:
        """Process incoming message"""
        try:
            # Create or get conversation
            if not conversation_id:
                conversation_id = f"conv_{datetime.now().timestamp()}"

            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = Conversation(conversation_id)

            conversation = self.conversations[conversation_id]

            # Create message
            message = Message(
                content=content,
                type=message_type,
                sender=sender,
                timestamp=datetime.now(),
                metadata=metadata,
            )

            # Add to conversation
            conversation.add_message(message)

            # Process message
            handler = self.message_handlers.get(message_type)
            if handler:
                response = await handler(message, conversation)
                if response:
                    conversation.add_message(response)
                    return response

            return message

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return Message(
                content=f"Error processing message: {str(e)}",
                type=MessageType.ERROR,
                sender="system",
                timestamp=datetime.now(),
            )

    async def _handle_text(
        self, message: Message, conversation: Conversation
    ) -> Message:
        """Handle text messages"""
        try:
            # Get AI response
            response_content = await self.ai_service.generate_response(
                {
                    "message": message.content,
                    "context": conversation.get_context(),
                    "sender": message.sender,
                }
            )

            return Message(
                content=response_content,
                type=MessageType.TEXT,
                sender="agent",
                timestamp=datetime.now(),
                reply_to=message,
            )

        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            return self._create_error_message(str(e))

    async def _handle_command(
        self, message: Message, conversation: Conversation
    ) -> Message:
        """Handle command messages"""
        try:
            # Parse command
            command = message.content.split()[0]
            args = message.content.split()[1:]

            # Execute command
            if command in self.command_handlers:
                result = await self.command_handlers[command](*args)
                return Message(
                    content=str(result),
                    type=MessageType.TEXT,
                    sender="agent",
                    timestamp=datetime.now(),
                    metadata={"command": command},
                )
            else:
                return Message(
                    content=f"Unknown command: {command}",
                    type=MessageType.ERROR,
                    sender="system",
                    timestamp=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Error handling command: {e}")
            return self._create_error_message(str(e))

    async def _handle_system(
        self, message: Message, conversation: Conversation
    ) -> Optional[Message]:
        """Handle system messages"""
        try:
            # Update conversation context
            if message.metadata:
                conversation.context.update(message.metadata)
            return None
        except Exception as e:
            logger.error(f"Error handling system message: {e}")
            return self._create_error_message(str(e))

    def _create_error_message(self, error_text: str) -> Message:
        """Create error message"""
        return Message(
            content=f"Error: {error_text}",
            type=MessageType.ERROR,
            sender="system",
            timestamp=datetime.now(),
        )

    async def analyze_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """Analyze conversation patterns and metrics"""
        try:
            conversation = self.conversations.get(conversation_id)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            messages = conversation.messages

            analysis = {
                "message_count": len(messages),
                "user_messages": len([m for m in messages if m.sender != "agent"]),
                "agent_messages": len([m for m in messages if m.sender == "agent"]),
                "average_response_time": self._calculate_avg_response_time(messages),
                "command_usage": self._analyze_command_usage(messages),
                "sentiment": await self._analyze_sentiment(messages),
            }

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing conversation: {e}")
            raise

    def _calculate_avg_response_time(self, messages: List[Message]) -> float:
        """Calculate average response time"""
        response_times = []
        for i in range(1, len(messages)):
            if messages[i].sender == "agent" and messages[i - 1].sender != "agent":
                response_time = (
                    messages[i].timestamp - messages[i - 1].timestamp
                ).total_seconds()
                response_times.append(response_time)

        return sum(response_times) / len(response_times) if response_times else 0

    def _analyze_command_usage(self, messages: List[Message]) -> Dict[str, int]:
        """Analyze command usage patterns"""
        command_counts = {}
        for message in messages:
            if message.type == MessageType.COMMAND:
                command = message.content.split()[0]
                command_counts[command] = command_counts.get(command, 0) + 1
        return command_counts

    async def _analyze_sentiment(self, messages: List[Message]) -> Dict[str, float]:
        """Analyze conversation sentiment"""
        try:
            # Use AI service to analyze sentiment
            sentiment_scores = await self.ai_service.analyze_sentiment(
                [m.content for m in messages if m.type == MessageType.TEXT]
            )

            return {
                "average": sum(sentiment_scores) / len(sentiment_scores),
                "trend": "positive"
                if sentiment_scores[-1] > sentiment_scores[0]
                else "negative",
            }
        except Exception:
            return {"average": 0.0, "trend": "neutral"}
