from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of agent memories"""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


class MemoryPriority(Enum):
    """Memory priority levels"""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Memory:
    """Individual memory unit"""

    content: Any
    type: MemoryType
    priority: MemoryPriority
    timestamp: datetime
    tags: List[str]
    metadata: Dict[str, Any]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    decay_rate: float = 0.1  # Rate at which memory importance decays


class MemoryManager:
    """Manages agent memory system"""

    def __init__(
        self,
        short_term_limit: int = 100,
        long_term_limit: int = 1000,
        decay_interval: int = 3600,  # seconds
    ):
        self.short_term_limit = short_term_limit
        self.long_term_limit = long_term_limit
        self.decay_interval = decay_interval

        self.memories: Dict[MemoryType, List[Memory]] = {
            memory_type: [] for memory_type in MemoryType
        }

        self.index: Dict[str, List[Memory]] = defaultdict(list)

    async def store_memory(
        self,
        content: Any,
        memory_type: MemoryType,
        priority: MemoryPriority,
        tags: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """Store new memory"""
        try:
            memory = Memory(
                content=content,
                type=memory_type,
                priority=priority,
                timestamp=datetime.now(),
                tags=tags,
                metadata=metadata or {},
                last_accessed=datetime.now(),
            )

            # Add to memory store
            self.memories[memory_type].append(memory)

            # Index by tags
            for tag in tags:
                self.index[tag].append(memory)

            # Check memory limits
            await self._enforce_memory_limits(memory_type)

            return memory

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise

    async def retrieve_by_tags(
        self,
        tags: List[str],
        memory_type: Optional[MemoryType] = None,
        limit: Optional[int] = None,
    ) -> List[Memory]:
        """Retrieve memories by tags"""
        try:
            # Get memories matching any tag
            matching_memories = set()
            for tag in tags:
                if tag in self.index:
                    matching_memories.update(self.index[tag])

            # Filter by memory type if specified
            if memory_type:
                matching_memories = {
                    m for m in matching_memories if m.type == memory_type
                }

            # Sort by relevance (using priority and recency)
            memories = list(matching_memories)
            memories.sort(
                key=lambda x: (x.priority.value, x.timestamp.timestamp()), reverse=True
            )

            # Update access metrics
            for memory in memories[:limit]:
                memory.access_count += 1
                memory.last_accessed = datetime.now()

            return memories[:limit] if limit else memories

        except Exception as e:
            logger.error(f"Error retrieving memories: {e}")
            raise

    async def get_recent_memories(
        self,
        memory_type: Optional[MemoryType] = None,
        timeframe: Optional[timedelta] = None,
        limit: Optional[int] = None,
    ) -> List[Memory]:
        """Get recent memories"""
        try:
            memories = []
            current_time = datetime.now()

            for mtype, memory_list in self.memories.items():
                if memory_type and mtype != memory_type:
                    continue

                for memory in memory_list:
                    if timeframe and (current_time - memory.timestamp) > timeframe:
                        continue
                    memories.append(memory)

            # Sort by recency
            memories.sort(key=lambda x: x.timestamp, reverse=True)

            return memories[:limit] if limit else memories

        except Exception as e:
            logger.error(f"Error getting recent memories: {e}")
            raise

    async def consolidate_memories(
        self, memory_type: MemoryType = MemoryType.SHORT_TERM
    ):
        """Consolidate memories to long-term storage"""
        try:
            if memory_type == MemoryType.LONG_TERM:
                return

            memories_to_consolidate = []
            current_time = datetime.now()

            for memory in self.memories[memory_type]:
                # Check if memory should be consolidated
                if await self._should_consolidate(memory, current_time):
                    memories_to_consolidate.append(memory)

            # Move memories to long-term storage
            for memory in memories_to_consolidate:
                memory.type = MemoryType.LONG_TERM
                self.memories[MemoryType.LONG_TERM].append(memory)
                self.memories[memory_type].remove(memory)

            await self._enforce_memory_limits(MemoryType.LONG_TERM)

        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")
            raise

    async def clear_memory(self, memory_type: Optional[MemoryType] = None):
        """Clear memories of specified type"""
        if memory_type:
            self.memories[memory_type] = []
        else:
            for mtype in MemoryType:
                self.memories[mtype] = []

        # Clear index entries for removed memories
        self.index = defaultdict(list)

    async def _enforce_memory_limits(self, memory_type: MemoryType):
        """Enforce memory limits"""
        if memory_type == MemoryType.SHORT_TERM:
            limit = self.short_term_limit
        elif memory_type == MemoryType.LONG_TERM:
            limit = self.long_term_limit
        else:
            return

        memories = self.memories[memory_type]
        if len(memories) > limit:
            # Remove lowest priority memories
            memories.sort(
                key=lambda x: (
                    x.priority.value,
                    x.access_count,
                    x.timestamp.timestamp(),
                )
            )

            memories_to_remove = memories[:-limit]
            self.memories[memory_type] = memories[-limit:]

            # Update index
            for memory in memories_to_remove:
                for tag in memory.tags:
                    if memory in self.index[tag]:
                        self.index[tag].remove(memory)

    async def _should_consolidate(self, memory: Memory, current_time: datetime) -> bool:
        """Check if memory should be consolidated"""
        # Consider factors like:
        # - Age of memory
        # - Access frequency
        # - Priority
        # - Available capacity

        age = (current_time - memory.timestamp).total_seconds()

        if memory.priority == MemoryPriority.CRITICAL:
            return False  # Keep critical memories in current store

        if age > self.decay_interval:
            if memory.access_count == 0:
                return True

            access_rate = memory.access_count / (age / self.decay_interval)
            return access_rate < 0.1

        return False

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        stats = {
            "total_memories": sum(len(memories) for memories in self.memories.values()),
            "by_type": {
                mtype.value: len(memories) for mtype, memories in self.memories.items()
            },
            "by_priority": defaultdict(int),
            "avg_access_count": defaultdict(float),
            "total_tags": len(self.index),
        }

        # Calculate priority and access stats
        for memories in self.memories.values():
            for memory in memories:
                stats["by_priority"][memory.priority.value] += 1
                stats["avg_access_count"][memory.type.value] += memory.access_count

        # Calculate averages
        for mtype in MemoryType:
            count = len(self.memories[mtype])
            if count > 0:
                stats["avg_access_count"][mtype.value] /= count

        return stats
