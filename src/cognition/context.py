from enum import Enum
from typing import Dict, List, Optional, Any, List
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context the agent can handle"""

    MARKET = "market"
    SOCIAL = "social"
    SYSTEM = "system"
    USER = "user"
    TRANSACTION = "transaction"
    ANALYSIS = "analysis"


@dataclass
class Memory:
    """Individual memory unit"""

    content: Any
    context_type: ContextType
    timestamp: datetime
    importance: float = 0.5  # 0.0 to 1.0
    metadata: Optional[Dict] = None
    references: List[str] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class Context:
    """Context container"""

    type: ContextType
    data: Dict[str, Any]
    timestamp: datetime
    expires: Optional[datetime] = None
    priority: float = 0.5  # 0.0 to 1.0


class ContextManager:
    """Manages agent's context and situational awareness"""
    
    def __init__(self):
        self._context = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the context manager"""
        try:
            self._context = {
                "start_time": datetime.now().isoformat(),
                "market_state": {},
                "portfolio_state": {},
                "system_state": {}
            }
            self._initialized = True
            logger.info("Context Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Context Manager: {e}")
            raise

    async def get_current_context(self) -> Dict[str, Any]:
        """Get current context state"""
        if not self._initialized:
            raise RuntimeError("Context Manager not initialized")
        return self._context.copy()

    async def update_context(self, updates: Dict[str, Any]) -> None:
        """Update context with new information"""
        if not self._initialized:
            raise RuntimeError("Context Manager not initialized")
        self._context.update(updates)
        self._context["last_updated"] = datetime.now().isoformat()

    async def cleanup(self) -> None:
        """Cleanup context manager resources"""
        try:
            self._context.clear()
            self._initialized = False
            logger.info("Context Manager cleaned up successfully")
        except Exception as e:
            logger.error(f"Error cleaning up Context Manager: {e}")
            raise

    async def update(self, new_context: Dict[str, Any]) -> Dict[str, Any]:
        """Update current context with new information"""
        if not self._initialized:
            await self.initialize()
            
        # Save current context to history
        if len(self.context_history) >= self.max_history_size:
            self.context_history.pop(0)  # Remove oldest context
        self.context_history.append(self.current_context.copy())
        
        # Update context
        self.current_context.update(new_context)
        self.current_context["timestamp"] = datetime.now().isoformat()
        
        return self.current_context

    async def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.current_context

    async def get_context_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get context history with optional limit"""
        if limit:
            return self.context_history[-limit:]
        return self.context_history

    async def clear_context(self):
        """Clear current context and history"""
        self.current_context = {}
        self.context_history = []

    async def add_context(
        self,
        context_type: ContextType,
        data: Dict[str, Any],
        priority: float = 0.5,
        ttl: Optional[int] = None,
    ) -> Context:
        """Add new context"""
        try:
            expires = None
            if ttl:
                expires = datetime.now() + timedelta(seconds=ttl)
            elif self.context_ttl:
                expires = datetime.now() + timedelta(seconds=self.context_ttl)

            context = Context(
                type=context_type,
                data=data,
                timestamp=datetime.now(),
                expires=expires,
                priority=priority,
            )

            self.current_context[context_type] = context
            self.context_history.append(context)
            await self._clean_expired_contexts()

            return context

        except Exception as e:
            logger.error(f"Error adding context: {e}")
            raise

    async def get_context(
        self,
        context_type: ContextType,
    ) -> Optional[Context]:
        """Get current context of specified type"""
        if context_type not in self.current_context:
            return None

        context = self.current_context[context_type]
        if context.expires and context.expires < datetime.now():
            del self.current_context[context_type]
            return None

        return context

    async def add_memory(
        self,
        content: Any,
        context_type: ContextType,
        importance: float = 0.5,
        metadata: Optional[Dict] = None,
        references: Optional[List[str]] = None,
    ) -> Memory:
        """Add new memory"""
        try:
            memory = Memory(
                content=content,
                context_type=context_type,
                timestamp=datetime.now(),
                importance=importance,
                metadata=metadata,
                references=references,
            )

            self.memory_store.append(memory)

            if len(self.memory_store) > self.memory_limit:
                self.memory_store.sort(key=lambda x: x.importance)
                # self.memory_store = self.memory_store[-self.memory_limit :]

            return memory

        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            raise

    async def get_relevant_memories(
        self,
        context_type: ContextType,
        timeframe: Optional[int] = None,  # seconds
        min_importance: float = 0.0,
    ) -> List[Memory]:
        """Get relevant memories"""
        memories = []
        now = datetime.now()

        for memory in self.memory_store:
            if (
                memory.context_type == context_type
                and memory.importance >= min_importance
            ):
                if timeframe:
                    age = (now - memory.timestamp).total_seconds()
                    if age <= timeframe:
                        memories.append(memory)
                else:
                    memories.append(memory)

        return memories

    async def merge_contexts(
        self,
        context_types: List[ContextType],
    ) -> Dict[str, Any]:
        """Merge multiple contexts"""
        merged = {}
        for context_type in context_types:
            context = await self.get_context(context_type)
            if context:
                merged.update(context.data)

        return merged

    async def _clean_expired_contexts(self) -> None:
        """Remove expired contexts"""
        now = datetime.now()
        expired = []

        for context_type, context in self.current_context.items():
            if context.expires and context.expires < now:
                expired.append(context_type)

        for context_type in expired:
            del self.current_context[context_type]

    async def summarize_context(
        self,
        context_type: Optional[ContextType] = None,
    ) -> Dict[str, Any]:
        """Get context summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "active_contexts": len(self.current_context),
            "memory_count": len(self.memory_store),
        }

        if context_type:
            context = await self.get_context(context_type)
            if context:
                summary["context"] = {
                    "type": context_type.value,
                    "data": context.data,
                    "age": (datetime.now() - context.timestamp).total_seconds(),
                    "priority": context.priority,
                }

        return summary

    async def get_context_history(
        self,
        context_type: Optional[ContextType] = None,
        limit: Optional[int] = None,
    ) -> List[Context]:
        """Get context history"""
        history = self.context_history

        if context_type:
            history = [ctx for ctx in history if ctx.type == context_type]

        if limit:
            history = history[-limit:]

        return history
