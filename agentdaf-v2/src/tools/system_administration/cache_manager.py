#!/usr/bin/env python3
"""
AgentDaf1.1 - Cache Manager Tool
Redis/memory cache management and optimization
"""

import json
import time
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
import pickle
import sqlite3

class CacheManager:
    """Redis/memory cache management and optimization"""
    
    def __init__(self):
        self.name = "Cache Manager"
        self.version = "1.0.0"
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Project paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.cache_db_path = self.project_root / "data" / "cache.db"
        
        # Ensure data directory exists
        self.cache_db_path.parent.mkdir(exist_ok=True)
        
        # Initialize cache storage
        self.memory_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "evictions": 0
        }
        
        # Cache configuration
        self.config = {
            "max_memory_items": 10000,
            "default_ttl": 3600,  # 1 hour
            "cleanup_interval": 300,  # 5 minutes
            "max_memory_size": 100 * 1024 * 1024,  # 100MB
            "eviction_policy": "lru"  # lru, lfu, fifo
        }
        
        # Initialize persistent cache
        self._init_persistent_cache()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        self.logger.info(f"Cache Manager initialized: {self.name} v{self.version}")
    
    def _init_persistent_cache(self):
        """Initialize persistent cache storage"""
        conn = sqlite3.connect(str(self.cache_db_path))
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cache_store (
                key TEXT PRIMARY KEY,
                value BLOB,
                expires_at REAL,
                created_at REAL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL,
                size INTEGER
            )
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_store(expires_at)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_store(last_accessed)
        ''')
        
        conn.commit()
        conn.close()
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_expired():
            while True:
                try:
                    self._cleanup_expired()
                    time.sleep(self.config["cleanup_interval"])
                except Exception as e:
                    self.logger.error(f"Cache cleanup error: {str(e)}")
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()
    
    def _cleanup_expired(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        
        # Clean memory cache
        expired_keys = []
        for key, data in self.memory_cache.items():
            if data.get("expires_at") and data["expires_at"] < current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            with self.lock:
                self.cache_stats["evictions"] += 1
        
        # Clean persistent cache
        conn = sqlite3.connect(str(self.cache_db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache_store WHERE expires_at < ?", (current_time,))
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        with self.lock:
            self.cache_stats["evictions"] += deleted_count
    
    def _evict_memory_items(self):
        """Evict items from memory cache based on policy"""
        if len(self.memory_cache) <= self.config["max_memory_items"]:
            return
        
        policy = self.config["eviction_policy"]
        
        if policy == "lru":
            # Sort by last accessed time
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get("last_accessed", 0)
            )
        elif policy == "lfu":
            # Sort by access count
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get("access_count", 0)
            )
        else:  # fifo
            # Sort by creation time
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get("created_at", 0)
            )
        
        # Remove oldest items
        items_to_remove = len(self.memory_cache) - self.config["max_memory_items"] + 100
        for i in range(items_to_remove):
            if i < len(sorted_items):
                key = sorted_items[i][0]
                del self.memory_cache[key]
                with self.lock:
                    self.cache_stats["evictions"] += 1
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for storage"""
        try:
            return pickle.dumps(value)
        except Exception:
            return json.dumps(value).encode('utf-8')
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value from storage"""
        try:
            return pickle.loads(data)
        except Exception:
            try:
                return json.loads(data.decode('utf-8'))
            except Exception:
                return data.decode('utf-8', errors='ignore')
    
    def set(self, key: str, value: Any, ttl: int = None, persist: bool = False) -> Dict[str, Any]:
        """Set cache value"""
        current_time = time.time()
        ttl = ttl or self.config["default_ttl"]
        expires_at = current_time + ttl
        
        # Serialize value
        serialized_value = self._serialize_value(value)
        value_size = len(serialized_value)
        
        # Store in memory cache
        self.memory_cache[key] = {
            "value": value,
            "serialized": serialized_value,
            "expires_at": expires_at,
            "created_at": current_time,
            "last_accessed": current_time,
            "access_count": 0,
            "size": value_size
        }
        
        # Store in persistent cache if requested
        if persist:
            conn = sqlite3.connect(str(self.cache_db_path))
            conn.execute('''
                INSERT OR REPLACE INTO cache_store 
                (key, value, expires_at, created_at, access_count, last_accessed, size)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (key, serialized_value, expires_at, current_time, 0, current_time, value_size))
            conn.commit()
            conn.close()
        
        # Evict if necessary
        self._evict_memory_items()
        
        with self.lock:
            self.cache_stats["sets"] += 1
        
        return {
            "success": True,
            "key": key,
            "ttl": ttl,
            "size": value_size,
            "persisted": persist,
            "timestamp": datetime.now().isoformat()
        }
    
    def get(self, key: str) -> Dict[str, Any]:
        """Get cache value"""
        current_time = time.time()
        
        # Check memory cache first
        if key in self.memory_cache:
            data = self.memory_cache[key]
            
            # Check if expired
            if data.get("expires_at") and data["expires_at"] < current_time:
                del self.memory_cache[key]
                with self.lock:
                    self.cache_stats["misses"] += 1
                return {"success": False, "error": "Key expired"}
            
            # Update access stats
            data["last_accessed"] = current_time
            data["access_count"] = data.get("access_count", 0) + 1
            
            with self.lock:
                self.cache_stats["hits"] += 1
            
            return {
                "success": True,
                "value": data["value"],
                "source": "memory",
                "access_count": data["access_count"],
                "last_accessed": data["last_accessed"]
            }
        
        # Check persistent cache
        conn = sqlite3.connect(str(self.cache_db_path))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT value, expires_at, access_count FROM cache_store WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        
        if row:
            value_data, expires_at, access_count = row
            
            # Check if expired
            if expires_at and expires_at < current_time:
                cursor.execute("DELETE FROM cache_store WHERE key = ?", (key,))
                conn.commit()
                conn.close()
                with self.lock:
                    self.cache_stats["misses"] += 1
                return {"success": False, "error": "Key expired"}
            
            # Deserialize and update access stats
            value = self._deserialize_value(value_data)
            cursor.execute(
                "UPDATE cache_store SET access_count = access_count + 1, last_accessed = ? WHERE key = ?",
                (current_time, key)
            )
            conn.commit()
            conn.close()
            
            # Store in memory cache for faster access
            self.memory_cache[key] = {
                "value": value,
                "serialized": value_data,
                "expires_at": expires_at,
                "created_at": current_time,
                "last_accessed": current_time,
                "access_count": access_count + 1,
                "size": len(value_data)
            }
            
            with self.lock:
                self.cache_stats["hits"] += 1
            
            return {
                "success": True,
                "value": value,
                "source": "persistent",
                "access_count": access_count + 1,
                "last_accessed": current_time
            }
        
        conn.close()
        with self.lock:
            self.cache_stats["misses"] += 1
        
        return {"success": False, "error": "Key not found"}
    
    def delete(self, key: str) -> Dict[str, Any]:
        """Delete cache key"""
        deleted_from_memory = False
        deleted_from_persistent = False
        
        # Delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            deleted_from_memory = True
        
        # Delete from persistent cache
        conn = sqlite3.connect(str(self.cache_db_path))
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache_store WHERE key = ?", (key,))
        if cursor.rowcount > 0:
            deleted_from_persistent = True
        conn.commit()
        conn.close()
        
        if deleted_from_memory or deleted_from_persistent:
            with self.lock:
                self.cache_stats["deletes"] += 1
            return {
                "success": True,
                "key": key,
                "deleted_from_memory": deleted_from_memory,
                "deleted_from_persistent": deleted_from_persistent
            }
        
        return {"success": False, "error": "Key not found"}
    
    def clear(self, pattern: str = None) -> Dict[str, Any]:
        """Clear cache keys matching pattern"""
        import fnmatch
        
        keys_to_delete = []
        
        if pattern:
            # Find matching keys in memory cache
            for key in self.memory_cache.keys():
                if fnmatch.fnmatch(key, pattern):
                    keys_to_delete.append(key)
        else:
            # Clear all
            keys_to_delete = list(self.memory_cache.keys())
        
        # Delete from memory cache
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        # Delete from persistent cache
        conn = sqlite3.connect(str(self.cache_db_path))
        cursor = conn.cursor()
        
        if pattern:
            cursor.execute("DELETE FROM cache_store WHERE key LIKE ?", (pattern.replace('*', '%'),))
        else:
            cursor.execute("DELETE FROM cache_store")
        
        deleted_persistent = cursor.rowcount
        conn.commit()
        conn.close()
        
        with self.lock:
            self.cache_stats["deletes"] += len(keys_to_delete) + deleted_persistent
        
        return {
            "success": True,
            "pattern": pattern,
            "deleted_from_memory": len(keys_to_delete),
            "deleted_from_persistent": deleted_persistent,
            "total_deleted": len(keys_to_delete) + deleted_persistent
        }
    
    def warm_cache(self, warm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Warm cache with predefined data"""
        warmed_keys = []
        errors = []
        
        for key, data in warm_data.items():
            try:
                ttl = data.get("ttl", self.config["default_ttl"])
                persist = data.get("persist", False)
                value = data.get("value")
                
                result = self.set(key, value, ttl, persist)
                if result["success"]:
                    warmed_keys.append(key)
                else:
                    errors.append(f"Failed to warm key {key}: {result.get('error')}")
            except Exception as e:
                errors.append(f"Error warming key {key}: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "warmed_keys": warmed_keys,
            "error_count": len(errors),
            "errors": errors
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        current_time = time.time()
        
        # Calculate hit ratio
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_ratio = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        # Memory usage
        memory_size = sum(
            data.get("size", 0) for data in self.memory_cache.values()
        )
        
        # Persistent cache stats
        conn = sqlite3.connect(str(self.cache_db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(size) FROM cache_store")
        persistent_count, persistent_size = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM cache_store WHERE expires_at < ?", (current_time,))
        expired_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "memory_cache": {
                "items": len(self.memory_cache),
                "size_bytes": memory_size,
                "size_mb": memory_size / (1024 * 1024),
                "max_items": self.config["max_memory_items"],
                "max_size_mb": self.config["max_memory_size"] / (1024 * 1024)
            },
            "persistent_cache": {
                "items": persistent_count or 0,
                "size_bytes": persistent_size or 0,
                "size_mb": (persistent_size or 0) / (1024 * 1024),
                "expired_items": expired_count
            },
            "performance": {
                "hits": self.cache_stats["hits"],
                "misses": self.cache_stats["misses"],
                "sets": self.cache_stats["sets"],
                "deletes": self.cache_stats["deletes"],
                "evictions": self.cache_stats["evictions"],
                "hit_ratio_percent": round(hit_ratio, 2)
            },
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update cache configuration"""
        try:
            # Validate configuration
            valid_keys = set(self.config.keys())
            provided_keys = set(config.keys())
            invalid_keys = provided_keys - valid_keys
            
            if invalid_keys:
                return {
                    "success": False,
                    "error": f"Invalid configuration keys: {list(invalid_keys)}"
                }
            
            # Update configuration
            self.config.update(config)
            
            # Apply new limits immediately
            if "max_memory_items" in config:
                self._evict_memory_items()
            
            return {
                "success": True,
                "updated_config": config,
                "current_config": self.config
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get cache manager status"""
        return {
            "name": self.name,
            "version": self.version,
            "status": "active",
            "config": self.config,
            "memory_cache_items": len(self.memory_cache),
            "persistent_cache_path": str(self.cache_db_path),
            "timestamp": datetime.now().isoformat()
        }

# Global instance
cache_manager = CacheManager()