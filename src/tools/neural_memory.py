# -*- coding: utf-8 -*-
"""
Neural Memory System for AgentDaf1.1
Advanced memory architecture with working memory, episodic memory, and semantic memory
"""

import hashlib
import json
import logging
import pickle
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np


@dataclass
class MemoryItem:
    """Base class for memory items"""

    id: str
    content: Any
    timestamp: datetime
    importance: float
    tags: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class WorkingMemoryItem(MemoryItem):
    """Working memory item with temporary storage"""

    decay_rate: float = 0.1
    activation: float = 1.0


@dataclass
class EpisodicMemoryItem(MemoryItem):
    """Episodic memory item with context"""

    context: Dict[str, Any] = field(default_factory=dict)
    emotional_valence: float = 0.0
    spatial_info: Optional[Dict[str, float]] = None


@dataclass
class SemanticMemoryItem(MemoryItem):
    """Semantic memory item with relationships"""

    relationships: List[str] = field(default_factory=list)
    category: str = ""
    confidence: float = 1.0


class NeuralMemorySystem:
    """Advanced neural memory system with multiple memory types"""

    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Initialize databases
        self.working_memory_db = self.storage_path / "working_memory.db"
        self.episodic_memory_db = self.storage_path / "episodic_memory.db"
        self.semantic_memory_db = self.storage_path / "semantic_memory.db"

        # Memory capacities
        self.working_memory_capacity = 50
        self.episodic_memory_capacity = 10000
        self.semantic_memory_capacity = 50000

        # Initialize databases
        self._init_databases()

        # Working memory cache
        self.working_memory: List[WorkingMemoryItem] = []
        self.working_memory_lock = threading.Lock()

        # Embedding model (simplified)
        self.embedding_dim = 128

        # Consolidation thread
        self.consolidation_thread = None
        self.consolidation_interval = 300  # 5 minutes
        self.running = True

        # Start consolidation thread
        self._start_consolidation_thread()

        logging.info("Neural Memory System initialized")

    def _init_databases(self):
        """Initialize SQLite databases for persistent storage"""
        # Working memory database
        conn = sqlite3.connect(self.working_memory_db)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS working_memory (
                id TEXT PRIMARY KEY,
                content BLOB,
                timestamp TEXT,
                importance REAL,
                tags TEXT,
                embedding BLOB,
                access_count INTEGER,
                last_accessed TEXT,
                decay_rate REAL,
                activation REAL
            )
        """
        )
        conn.commit()
        conn.close()

        # Episodic memory database
        conn = sqlite3.connect(self.episodic_memory_db)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id TEXT PRIMARY KEY,
                content BLOB,
                timestamp TEXT,
                importance REAL,
                tags TEXT,
                embedding BLOB,
                access_count INTEGER,
                last_accessed TEXT,
                context BLOB,
                emotional_valence REAL,
                spatial_info BLOB
            )
        """
        )
        conn.commit()
        conn.close()

        # Semantic memory database
        conn = sqlite3.connect(self.semantic_memory_db)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id TEXT PRIMARY KEY,
                content BLOB,
                timestamp TEXT,
                importance REAL,
                tags TEXT,
                embedding BLOB,
                access_count INTEGER,
                last_accessed TEXT,
                relationships TEXT,
                category TEXT,
                confidence REAL
            )
        """
        )
        conn.commit()
        conn.close()

    def _generate_embedding(self, content: Any) -> np.ndarray:
        """Generate embedding for content (simplified implementation)"""
        # In a real implementation, this would use a proper embedding model
        # For now, we'll create a simple hash-based embedding
        content_str = str(content)
        hash_obj = hashlib.md5(content_str.encode())
        hash_hex = hash_obj.hexdigest()

        # Convert hash to numeric embedding
        embedding = np.zeros(self.embedding_dim)
        for i, char in enumerate(hash_hex):
            if i < self.embedding_dim:
                embedding[i] = int(char, 16) / 15.0

        return embedding

    def add_to_working_memory(
        self,
        content: Any,
        importance: float = 0.5,
        tags: List[str] = None,
        decay_rate: float = 0.1,
    ) -> str:
        """Add item to working memory"""
        memory_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()

        item = WorkingMemoryItem(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or [],
            embedding=self._generate_embedding(content),
            decay_rate=decay_rate,
            activation=1.0,
        )

        with self.working_memory_lock:
            self.working_memory.append(item)

            # Maintain capacity
            if len(self.working_memory) > self.working_memory_capacity:
                # Remove least activated items
                self.working_memory.sort(key=lambda x: x.activation)
                self.working_memory = self.working_memory[
                    -self.working_memory_capacity :
                ]

        # Persist to database
        self._save_working_memory_item(item)

        logging.info(f"Added to working memory: {memory_id}")
        return memory_id

    def add_to_episodic_memory(
        self,
        content: Any,
        context: Dict[str, Any] = None,
        importance: float = 0.5,
        tags: List[str] = None,
        emotional_valence: float = 0.0,
    ) -> str:
        """Add item to episodic memory"""
        memory_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()

        item = EpisodicMemoryItem(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or [],
            embedding=self._generate_embedding(content),
            context=context or {},
            emotional_valence=emotional_valence,
        )

        # Save to database
        self._save_episodic_memory_item(item)

        logging.info(f"Added to episodic memory: {memory_id}")
        return memory_id

    def add_to_semantic_memory(
        self,
        content: Any,
        category: str,
        relationships: List[str] = None,
        importance: float = 0.5,
        tags: List[str] = None,
        confidence: float = 1.0,
    ) -> str:
        """Add item to semantic memory"""
        memory_id = hashlib.md5(
            f"{content}{category}{time.time()}".encode()
        ).hexdigest()

        item = SemanticMemoryItem(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or [],
            embedding=self._generate_embedding(content),
            relationships=relationships or [],
            category=category,
            confidence=confidence,
        )

        # Save to database
        self._save_semantic_memory_item(item)

        logging.info(f"Added to semantic memory: {memory_id}")
        return memory_id

    def _save_working_memory_item(self, item: WorkingMemoryItem):
        """Save working memory item to database"""
        conn = sqlite3.connect(self.working_memory_db)
        conn.execute(
            """
            INSERT OR REPLACE INTO working_memory 
            (id, content, timestamp, importance, tags, embedding, access_count, 
             last_accessed, decay_rate, activation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.id,
                pickle.dumps(item.content),
                item.timestamp.isoformat(),
                item.importance,
                json.dumps(item.tags),
                pickle.dumps(item.embedding) if item.embedding is not None else None,
                item.access_count,
                item.last_accessed.isoformat() if item.last_accessed else None,
                item.decay_rate,
                item.activation,
            ),
        )
        conn.commit()
        conn.close()

    def _save_episodic_memory_item(self, item: EpisodicMemoryItem):
        """Save episodic memory item to database"""
        conn = sqlite3.connect(self.episodic_memory_db)
        conn.execute(
            """
            INSERT OR REPLACE INTO episodic_memory 
            (id, content, timestamp, importance, tags, embedding, access_count, 
             last_accessed, context, emotional_valence, spatial_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.id,
                pickle.dumps(item.content),
                item.timestamp.isoformat(),
                item.importance,
                json.dumps(item.tags),
                pickle.dumps(item.embedding) if item.embedding is not None else None,
                item.access_count,
                item.last_accessed.isoformat() if item.last_accessed else None,
                pickle.dumps(item.context),
                item.emotional_valence,
                (
                    pickle.dumps(item.spatial_info)
                    if item.spatial_info is not None
                    else None
                ),
            ),
        )
        conn.commit()
        conn.close()

    def _save_semantic_memory_item(self, item: SemanticMemoryItem):
        """Save semantic memory item to database"""
        conn = sqlite3.connect(self.semantic_memory_db)
        conn.execute(
            """
            INSERT OR REPLACE INTO semantic_memory 
            (id, content, timestamp, importance, tags, embedding, access_count, 
             last_accessed, relationships, category, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                item.id,
                pickle.dumps(item.content),
                item.timestamp.isoformat(),
                item.importance,
                json.dumps(item.tags),
                pickle.dumps(item.embedding) if item.embedding is not None else None,
                item.access_count,
                item.last_accessed.isoformat() if item.last_accessed else None,
                json.dumps(item.relationships),
                item.category,
                item.confidence,
            ),
        )
        conn.commit()
        conn.close()

    def search_working_memory(
        self, query: str, limit: int = 10
    ) -> List[WorkingMemoryItem]:
        """Search working memory by content similarity"""
        query_embedding = self._generate_embedding(query)

        with self.working_memory_lock:
            results = []
            for item in self.working_memory:
                if item.embedding is not None:
                    similarity = np.dot(query_embedding, item.embedding)
                    results.append((item, similarity))

            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return [item for item, _ in results[:limit]]

    def search_episodic_memory(
        self, query: str, limit: int = 10
    ) -> List[EpisodicMemoryItem]:
        """Search episodic memory by content similarity"""
        query_embedding = self._generate_embedding(query)

        conn = sqlite3.connect(self.episodic_memory_db)
        cursor = conn.execute("SELECT * FROM episodic_memory")
        results = []

        for row in cursor.fetchall():
            item = self._row_to_episodic_item(row)
            if item.embedding is not None:
                similarity = np.dot(query_embedding, item.embedding)
                results.append((item, similarity))

        conn.close()

        # Sort by similarity and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in results[:limit]]

    def search_semantic_memory(
        self, query: str, category: str = None, limit: int = 10
    ) -> List[SemanticMemoryItem]:
        """Search semantic memory by content similarity and optionally category"""
        query_embedding = self._generate_embedding(query)

        conn = sqlite3.connect(self.semantic_memory_db)

        if category:
            cursor = conn.execute(
                "SELECT * FROM semantic_memory WHERE category = ?", (category,)
            )
        else:
            cursor = conn.execute("SELECT * FROM semantic_memory")

        results = []

        for row in cursor.fetchall():
            item = self._row_to_semantic_item(row)
            if item.embedding is not None:
                similarity = np.dot(query_embedding, item.embedding)
                results.append((item, similarity))

        conn.close()

        # Sort by similarity and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in results[:limit]]

    def _row_to_episodic_item(self, row) -> EpisodicMemoryItem:
        """Convert database row to EpisodicMemoryItem"""
        return EpisodicMemoryItem(
            id=row[0],
            content=pickle.loads(row[1]),
            timestamp=datetime.fromisoformat(row[2]),
            importance=row[3],
            tags=json.loads(row[4]),
            embedding=pickle.loads(row[5]) if row[5] else None,
            access_count=row[6],
            last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
            context=pickle.loads(row[8]),
            emotional_valence=row[9],
            spatial_info=pickle.loads(row[10]) if row[10] else None,
        )

    def _row_to_semantic_item(self, row) -> SemanticMemoryItem:
        """Convert database row to SemanticMemoryItem"""
        return SemanticMemoryItem(
            id=row[0],
            content=pickle.loads(row[1]),
            timestamp=datetime.fromisoformat(row[2]),
            importance=row[3],
            tags=json.loads(row[4]),
            embedding=pickle.loads(row[5]) if row[5] else None,
            access_count=row[6],
            last_accessed=datetime.fromisoformat(row[7]) if row[7] else None,
            relationships=json.loads(row[8]),
            category=row[9],
            confidence=row[10],
        )

    def update_working_memory_activations(self):
        """Update activation levels in working memory based on decay"""
        with self.working_memory_lock:
            for item in self.working_memory:
                item.activation *= 1 - item.decay_rate

            # Remove items with very low activation
            self.working_memory = [
                item for item in self.working_memory if item.activation > 0.01
            ]

    def consolidate_memories(self):
        """Consolidate working memory items to episodic or semantic memory"""
        with self.working_memory_lock:
            items_to_consolidate = []

            for item in self.working_memory:
                # Consolidate if item is important or has been accessed multiple times
                if item.importance > 0.7 or item.access_count > 3:
                    items_to_consolidate.append(item)

            for item in items_to_consolidate:
                # Determine if it should go to episodic or semantic memory
                if isinstance(item.content, dict) and "context" in item.content:
                    # Episodic memory
                    self.add_to_episodic_memory(
                        content=item.content,
                        context=item.content.get("context", {}),
                        importance=item.importance,
                        tags=item.tags,
                        emotional_valence=item.content.get("emotional_valence", 0.0),
                    )
                else:
                    # Semantic memory
                    self.add_to_semantic_memory(
                        content=item.content,
                        category=item.tags[0] if item.tags else "general",
                        relationships=item.tags,
                        importance=item.importance,
                        tags=item.tags,
                    )

                # Remove from working memory
                self.working_memory.remove(item)

        logging.info(f"Consolidated {len(items_to_consolidate)} memories")

    def _start_consolidation_thread(self):
        """Start background consolidation thread"""

        def consolidation_loop():
            while self.running:
                try:
                    time.sleep(self.consolidation_interval)
                    self.update_working_memory_activations()
                    self.consolidate_memories()
                except Exception as e:
                    logging.error(f"Consolidation error: {e}")

        self.consolidation_thread = threading.Thread(
            target=consolidation_loop, daemon=True
        )
        self.consolidation_thread.start()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        with self.working_memory_lock:
            working_count = len(self.working_memory)

        # Get counts from databases
        conn = sqlite3.connect(self.episodic_memory_db)
        episodic_count = conn.execute(
            "SELECT COUNT(*) FROM episodic_memory"
        ).fetchone()[0]
        conn.close()

        conn = sqlite3.connect(self.semantic_memory_db)
        semantic_count = conn.execute(
            "SELECT COUNT(*) FROM semantic_memory"
        ).fetchone()[0]
        conn.close()

        return {
            "working_memory_count": working_count,
            "working_memory_capacity": self.working_memory_capacity,
            "episodic_memory_count": episodic_count,
            "episodic_memory_capacity": self.episodic_memory_capacity,
            "semantic_memory_count": semantic_count,
            "semantic_memory_capacity": self.semantic_memory_capacity,
            "total_memories": working_count + episodic_count + semantic_count,
        }

    def export_memories(self, filepath: str):
        """Export all memories to JSON file"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "stats": self.get_memory_stats(),
            "working_memory": [],
            "episodic_memory": [],
            "semantic_memory": [],
        }

        # Export working memory
        with self.working_memory_lock:
            for item in self.working_memory:
                item_dict = asdict(item)
                item_dict["timestamp"] = item.timestamp.isoformat()
                if item.last_accessed:
                    item_dict["last_accessed"] = item.last_accessed.isoformat()
                if item.embedding is not None:
                    item_dict["embedding"] = item.embedding.tolist()
                export_data["working_memory"].append(item_dict)

        # Export episodic memory
        conn = sqlite3.connect(self.episodic_memory_db)
        cursor = conn.execute("SELECT * FROM episodic_memory")
        for row in cursor.fetchall():
            item = self._row_to_episodic_item(row)
            item_dict = asdict(item)
            item_dict["timestamp"] = item.timestamp.isoformat()
            if item.last_accessed:
                item_dict["last_accessed"] = item.last_accessed.isoformat()
            if item.embedding is not None:
                item_dict["embedding"] = item.embedding.tolist()
            export_data["episodic_memory"].append(item_dict)
        conn.close()

        # Export semantic memory
        conn = sqlite3.connect(self.semantic_memory_db)
        cursor = conn.execute("SELECT * FROM semantic_memory")
        for row in cursor.fetchall():
            item = self._row_to_semantic_item(row)
            item_dict = asdict(item)
            item_dict["timestamp"] = item.timestamp.isoformat()
            if item.last_accessed:
                item_dict["last_accessed"] = item.last_accessed.isoformat()
            if item.embedding is not None:
                item_dict["embedding"] = item.embedding.tolist()
            export_data["semantic_memory"].append(item_dict)
        conn.close()

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logging.info(f"Memories exported to {filepath}")

    def shutdown(self):
        """Shutdown the memory system"""
        self.running = False
        if self.consolidation_thread:
            self.consolidation_thread.join(timeout=5)
        logging.info("Neural Memory System shutdown")


# Memory Manager for easy access
class MemoryManager:
    """High-level interface for the neural memory system"""

    def __init__(self, storage_path: str = "data/memory"):
        self.memory_system = NeuralMemorySystem(storage_path)

    def remember(self, content: Any, memory_type: str = "working", **kwargs) -> str:
        """Store content in specified memory type"""
        if memory_type == "working":
            return self.memory_system.add_to_working_memory(content, **kwargs)
        elif memory_type == "episodic":
            return self.memory_system.add_to_episodic_memory(content, **kwargs)
        elif memory_type == "semantic":
            # Set default category if missing for compatibility
            if "category" not in kwargs or not kwargs.get("category"):
                kwargs["category"] = "general"
            return self.memory_system.add_to_semantic_memory(content, **kwargs)
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def recall(
        self, query: str, memory_type: str = "all", **kwargs
    ) -> List[MemoryItem]:
        """Recall memories matching query"""
        if memory_type == "working":
            return self.memory_system.search_working_memory(query, **kwargs)
        elif memory_type == "episodic":
            return self.memory_system.search_episodic_memory(query, **kwargs)
        elif memory_type == "semantic":
            return self.memory_system.search_semantic_memory(query, **kwargs)
        elif memory_type == "all":
            results = []
            results.extend(self.memory_system.search_working_memory(query, **kwargs))
            results.extend(self.memory_system.search_episodic_memory(query, **kwargs))
            results.extend(self.memory_system.search_semantic_memory(query, **kwargs))
            return results
        else:
            raise ValueError(f"Unknown memory type: {memory_type}")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return self.memory_system.get_memory_stats()

    def export(self, filepath: str):
        """Export memories"""
        self.memory_system.export_memories(filepath)

    def shutdown(self):
        """Shutdown memory system"""
        self.memory_system.shutdown()


if __name__ == "__main__":
    # Example usage
    memory_manager = MemoryManager()

    # Add some memories
    memory_manager.remember(
        "User asked about Python performance", "working", importance=0.8
    )
    memory_manager.remember(
        "System configuration completed",
        "episodic",
        context={"action": "config", "status": "success"},
    )
    memory_manager.remember(
        "Python is a high-level programming language",
        "semantic",
        category="programming",
        importance=0.9,
    )

    # Search memories
    results = memory_manager.recall("Python")
    logger.info(f"Found {len(results)} memories about Python")

    # Get stats
    stats = memory_manager.get_stats()
    logger.info(f"Memory stats: {stats}")

    # Export
    memory_manager.export("memory_export.json")

    # Shutdown
    memory_manager.shutdown()
