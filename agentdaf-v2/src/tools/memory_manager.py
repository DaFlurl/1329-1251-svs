"""
Memory Manager - Advanced memory management system for AgentDaf1.1
"""

import hashlib
import json
import logging
import os
import threading
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    id: str
    content: Any
    timestamp: datetime
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.expires_at:
            data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        if "timestamp" in data:
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if "expires_at" in data and data["expires_at"]:
            data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


@dataclass
class WorkingMemoryItem(MemoryItem):
    priority: int = 0
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)


@dataclass
class EpisodicMemoryItem(MemoryItem):
    context: str = ""
    importance: float = 1.0
    related_items: List[str] = field(default_factory=list)


@dataclass
class SemanticMemoryItem(MemoryItem):
    category: str = ""
    confidence: float = 1.0
    relationships: Dict[str, float] = field(default_factory=dict)


class MemoryManager:
    def __init__(self, storage_path: str = None):
        self.storage_path = storage_path or "data/memory"
        self.working_memory: Dict[str, WorkingMemoryItem] = {}
        self.episodic_memory: Dict[str, EpisodicMemoryItem] = {}
        self.semantic_memory: Dict[str, SemanticMemoryItem] = {}
        self.max_working_memory = 100
        self.max_episodic_memory = 1000
        self.max_semantic_memory = 500
        self._lock = threading.Lock()

        # Create storage directories
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "working"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "episodic"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "semantic"), exist_ok=True)

        # Load existing memories
        self.load_memories()

    def _generate_id(self, content: Any) -> str:
        """Generate unique ID for memory item"""
        content_str = json.dumps(content, sort_keys=True, default=str)
        return hashlib.md5(content_str.encode()).hexdigest()[:16]

    def add_working_memory(
        self,
        content: Any,
        priority: int = 0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None,
    ) -> str:
        """Add item to working memory"""
        with self._lock:
            item_id = self._generate_id(content)

            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)

            item = WorkingMemoryItem(
                id=item_id,
                content=content,
                timestamp=datetime.now(),
                tags=tags or [],
                metadata=metadata or {},
                expires_at=expires_at,
                priority=priority,
            )

            self.working_memory[item_id] = item

            # Cleanup if over limit
            if len(self.working_memory) > self.max_working_memory:
                self._cleanup_working_memory()

            logger.info(f"Added working memory item: {item_id}")
            return item_id

    def add_episodic_memory(
        self,
        content: Any,
        context: str = "",
        importance: float = 1.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add item to episodic memory"""
        with self._lock:
            item_id = self._generate_id(content)

            item = EpisodicMemoryItem(
                id=item_id,
                content=content,
                timestamp=datetime.now(),
                tags=tags or [],
                metadata=metadata or {},
                context=context,
                importance=importance,
            )

            self.episodic_memory[item_id] = item

            # Cleanup if over limit
            if len(self.episodic_memory) > self.max_episodic_memory:
                self._cleanup_episodic_memory()

            logger.info(f"Added episodic memory item: {item_id}")
            return item_id

    def add_semantic_memory(
        self,
        content: Any,
        category: str = "",
        confidence: float = 1.0,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Add item to semantic memory"""
        with self._lock:
            item_id = self._generate_id(content)

            item = SemanticMemoryItem(
                id=item_id,
                content=content,
                timestamp=datetime.now(),
                tags=tags or [],
                metadata=metadata or {},
                category=category,
                confidence=confidence,
            )

            self.semantic_memory[item_id] = item

            # Cleanup if over limit
            if len(self.semantic_memory) > self.max_semantic_memory:
                self._cleanup_semantic_memory()

            logger.info(f"Added semantic memory item: {item_id}")
            return item_id

    def get_working_memory(self, item_id: str) -> Optional[WorkingMemoryItem]:
        """Get item from working memory"""
        with self._lock:
            item = self.working_memory.get(item_id)
            if item:
                item.access_count += 1
                item.last_accessed = datetime.now()
            return item

    def get_episodic_memory(self, item_id: str) -> Optional[EpisodicMemoryItem]:
        """Get item from episodic memory"""
        with self._lock:
            return self.episodic_memory.get(item_id)

    def get_semantic_memory(self, item_id: str) -> Optional[SemanticMemoryItem]:
        """Get item from semantic memory"""
        with self._lock:
            return self.semantic_memory.get(item_id)

    def search_working_memory(
        self, query: str = "", tags: Optional[List[str]] = None, limit: int = 10
    ) -> List[WorkingMemoryItem]:
        """Search working memory"""
        with self._lock:
            results = []

            for item in self.working_memory.values():
                # Skip expired items
                if item.expires_at and item.expires_at < datetime.now():
                    continue

                # Check query match
                if query:
                    content_str = str(item.content).lower()
                    if query.lower() not in content_str:
                        continue

                # Check tags
                if tags and not any(tag in item.tags for tag in tags):
                    continue

                results.append(item)

            # Sort by priority and last accessed
            results.sort(key=lambda x: (-x.priority, -x.last_accessed.timestamp()))
            return results[:limit]

    def search_episodic_memory(
        self,
        query: str = "",
        context: str = "",
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[EpisodicMemoryItem]:
        """Search episodic memory"""
        with self._lock:
            results = []

            for item in self.episodic_memory.values():
                # Check query match
                if query:
                    content_str = str(item.content).lower()
                    if query.lower() not in content_str:
                        continue

                # Check context match
                if context and context.lower() not in item.context.lower():
                    continue

                # Check tags
                if tags and not any(tag in item.tags for tag in tags):
                    continue

                results.append(item)

            # Sort by importance and timestamp
            results.sort(key=lambda x: (-x.importance, -x.timestamp.timestamp()))
            return results[:limit]

    def search_semantic_memory(
        self,
        query: str = "",
        category: str = "",
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[SemanticMemoryItem]:
        """Search semantic memory"""
        with self._lock:
            results = []

            for item in self.semantic_memory.values():
                # Check query match
                if query:
                    content_str = str(item.content).lower()
                    if query.lower() not in content_str:
                        continue

                # Check category match
                if category and category.lower() != item.category.lower():
                    continue

                # Check tags
                if tags and not any(tag in item.tags for tag in tags):
                    continue

                results.append(item)

            # Sort by confidence and timestamp
            results.sort(key=lambda x: (-x.confidence, -x.timestamp.timestamp()))
            return results[:limit]

    def remove_working_memory(self, item_id: str) -> bool:
        """Remove item from working memory"""
        with self._lock:
            if item_id in self.working_memory:
                del self.working_memory[item_id]
                logger.info(f"Removed working memory item: {item_id}")
                return True
            return False

    def remove_episodic_memory(self, item_id: str) -> bool:
        """Remove item from episodic memory"""
        with self._lock:
            if item_id in self.episodic_memory:
                del self.episodic_memory[item_id]
                logger.info(f"Removed episodic memory item: {item_id}")
                return True
            return False

    def remove_semantic_memory(self, item_id: str) -> bool:
        """Remove item from semantic memory"""
        with self._lock:
            if item_id in self.semantic_memory:
                del self.semantic_memory[item_id]
                logger.info(f"Removed semantic memory item: {item_id}")
                return True
            return False

    def _cleanup_working_memory(self):
        """Remove old/expired items from working memory"""
        now = datetime.now()
        to_remove = []

        for item_id, item in self.working_memory.items():
            if item.expires_at and item.expires_at < now:
                to_remove.append(item_id)

        # If still over limit, remove lowest priority items
        if len(self.working_memory) - len(to_remove) > self.max_working_memory:
            sorted_items = sorted(
                [
                    (item_id, item)
                    for item_id, item in self.working_memory.items()
                    if item_id not in to_remove
                ],
                key=lambda x: (x[1].priority, x[1].last_accessed),
            )
            excess = len(self.working_memory) - len(to_remove) - self.max_working_memory
            to_remove.extend([item_id for item_id, _ in sorted_items[:excess]])

        for item_id in to_remove:
            del self.working_memory[item_id]

    def _cleanup_episodic_memory(self):
        """Remove old items from episodic memory"""
        # Remove oldest items beyond limit
        if len(self.episodic_memory) > self.max_episodic_memory:
            sorted_items = sorted(
                self.episodic_memory.items(),
                key=lambda x: (x[1].importance, x[1].timestamp),
            )
            excess = len(self.episodic_memory) - self.max_episodic_memory
            for item_id, _ in sorted_items[:excess]:
                del self.episodic_memory[item_id]

    def _cleanup_semantic_memory(self):
        """Remove old items from semantic memory"""
        # Remove lowest confidence items beyond limit
        if len(self.semantic_memory) > self.max_semantic_memory:
            sorted_items = sorted(
                self.semantic_memory.items(),
                key=lambda x: (x[1].confidence, x[1].timestamp),
            )
            excess = len(self.semantic_memory) - self.max_semantic_memory
            for item_id, _ in sorted_items[:excess]:
                del self.semantic_memory[item_id]

    def save_memories(self):
        """Save all memories to disk"""
        try:
            # Save working memory
            working_data = {
                item_id: item.to_dict() for item_id, item in self.working_memory.items()
            }
            with open(
                os.path.join(self.storage_path, "working", "memory.json"), "w"
            ) as f:
                json.dump(working_data, f, indent=2)

            # Save episodic memory
            episodic_data = {
                item_id: item.to_dict()
                for item_id, item in self.episodic_memory.items()
            }
            with open(
                os.path.join(self.storage_path, "episodic", "memory.json"), "w"
            ) as f:
                json.dump(episodic_data, f, indent=2)

            # Save semantic memory
            semantic_data = {
                item_id: item.to_dict()
                for item_id, item in self.semantic_memory.items()
            }
            with open(
                os.path.join(self.storage_path, "semantic", "memory.json"), "w"
            ) as f:
                json.dump(semantic_data, f, indent=2)

            logger.info("Memories saved to disk")

        except Exception as e:
            logger.error(f"Error saving memories: {e}")

    def load_memories(self):
        """Load memories from disk"""
        try:
            # Load working memory
            working_file = os.path.join(self.storage_path, "working", "memory.json")
            if os.path.exists(working_file):
                with open(working_file, "r") as f:
                    working_data = json.load(f)
                self.working_memory.update(
                    {
                        item_id: WorkingMemoryItem.from_dict(item_data)
                        for item_id, item_data in working_data.items()
                    }
                )

            # Load episodic memory
            episodic_file = os.path.join(self.storage_path, "episodic", "memory.json")
            if os.path.exists(episodic_file):
                with open(episodic_file, "r") as f:
                    episodic_data = json.load(f)
                self.episodic_memory.update(
                    {
                        item_id: EpisodicMemoryItem.from_dict(item_data)
                        for item_id, item_data in episodic_data.items()
                    }
                )

            # Load semantic memory
            semantic_file = os.path.join(self.storage_path, "semantic", "memory.json")
            if os.path.exists(semantic_file):
                with open(semantic_file, "r") as f:
                    semantic_data = json.load(f)
                self.semantic_memory.update(
                    {
                        item_id: SemanticMemoryItem.from_dict(item_data)
                        for item_id, item_data in semantic_data.items()
                    }
                )

            logger.info("Memories loaded from disk")

        except Exception as e:
            logger.error(f"Error loading memories: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with self._lock:
            return {
                "working_memory_count": len(self.working_memory),
                "episodic_memory_count": len(self.episodic_memory),
                "semantic_memory_count": len(self.semantic_memory),
                "max_working_memory": self.max_working_memory,
                "max_episodic_memory": self.max_episodic_memory,
                "max_semantic_memory": self.max_semantic_memory,
                "storage_path": self.storage_path,
            }

    def clear_all_memories(self):
        """Clear all memories"""
        with self._lock:
            self.working_memory.clear()
            self.episodic_memory.clear()
            self.semantic_memory.clear()
            logger.info("All memories cleared")

    # Backward-compatible monitoring & snapshot helpers expected by tests
    def get_memory_info(self) -> Dict[str, Any]:
        """Return a quick system memory/stat snapshot (process and counts)"""
        try:
            import psutil

            process = psutil.Process()
            mem = process.memory_info()
            info = {
                "process_memory_mb": mem.rss / (1024 * 1024),
                "working_memory_count": len(self.working_memory),
                "episodic_memory_count": len(self.episodic_memory),
                "semantic_memory_count": len(self.semantic_memory),
            }
            return info
        except Exception:
            # Fallback: return basic counts
            return {
                "process_memory_mb": 0.0,
                "working_memory_count": len(self.working_memory),
                "episodic_memory_count": len(self.episodic_memory),
                "semantic_memory_count": len(self.semantic_memory),
            }

    @dataclass
    class Snapshot:
        process_memory_mb: float
        timestamp: str

    def take_snapshot(self) -> "MemoryManager.Snapshot":
        """Take a memory snapshot for monitoring/testing"""
        info = self.get_memory_info()
        snapshot = MemoryManager.Snapshot(
            process_memory_mb=info.get("process_memory_mb", 0.0),
            timestamp=datetime.now().isoformat(),
        )
        return snapshot

    def optimize_memory(self) -> Dict[str, Any]:
        """Run basic optimizations/cleanup and return before/after stats"""
        before = self.get_stats()
        # Run cleanup routines
        self._cleanup_working_memory()
        self._cleanup_episodic_memory()
        self._cleanup_semantic_memory()
        after = self.get_stats()
        return {"before": before, "after": after}

    def get_memory_trend(self) -> Dict[str, Any]:
        """Return a simple trend analysis based on counts"""
        # For now, return a simple snapshot/trend of counts
        stats = self.get_stats()
        trend = "stable"
        # Basic heuristic: if working memory > 0 and large vs max -> 'increasing'
        if stats["working_memory_count"] > stats["max_working_memory"] * 0.8:
            trend = "increasing"
        return {"trend": trend, "stats": stats}


# Global memory manager instance
memory_manager = MemoryManager()


# Convenience functions
def add_working_memory(
    content: Any,
    priority: int = 0,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    expires_in: Optional[int] = None,
) -> str:
    """Add item to working memory"""
    return memory_manager.add_working_memory(
        content, priority, tags, metadata, expires_in
    )


def add_episodic_memory(
    content: Any,
    context: str = "",
    importance: float = 1.0,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Add item to episodic memory"""
    return memory_manager.add_episodic_memory(
        content, context, importance, tags, metadata
    )


def add_semantic_memory(
    content: Any,
    category: str = "",
    confidence: float = 1.0,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Add item to semantic memory"""
    return memory_manager.add_semantic_memory(
        content, category, confidence, tags, metadata
    )


def search_memory(
    query: str = "",
    memory_type: str = "all",
    tags: Optional[List[str]] = None,
    limit: int = 10,
) -> List[MemoryItem]:
    """Search across memory types"""
    results = []

    if memory_type in ["all", "working"]:
        results.extend(memory_manager.search_working_memory(query, tags, limit))
    if memory_type in ["all", "episodic"]:
        results.extend(
            memory_manager.search_episodic_memory(query, tags=tags, limit=limit)
        )
    if memory_type in ["all", "semantic"]:
        results.extend(
            memory_manager.search_semantic_memory(query, tags=tags, limit=limit)
        )

    # Sort by timestamp
    results.sort(key=lambda x: x.timestamp, reverse=True)
    return results[:limit]
