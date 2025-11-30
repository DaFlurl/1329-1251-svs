#!/usr/bin/env python3
"""
AgentDaf1.1 Database Integration
SQLite database for persistent data storage
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class DatabaseManager:
    """Database manager for AgentDaf1.1"""
    
    def __init__(self, db_path: str = "data/agentdaf1.db"):
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Ensure database directory and file exist"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def create_tables(self):
        """Create database tables"""
        with self.get_connection() as conn:
            # Players table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    score INTEGER DEFAULT 0,
                    alliance TEXT,
                    level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Alliances table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alliances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    total_score INTEGER DEFAULT 0,
                    members INTEGER DEFAULT 0,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Game sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    session_type TEXT,
                    score_change INTEGER,
                    duration_seconds INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            """)
            
            # System logs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    preferences TEXT,
                    theme TEXT DEFAULT 'default',
                    language TEXT DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def add_player(self, name: str, score: int = 0, alliance: str = None, level: int = 1) -> int:
        """Add a new player"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO players (name, score, alliance, level, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, score, alliance, level))
            conn.commit()
            return cursor.lastrowid
    
    def get_player(self, name: str) -> Optional[Dict]:
        """Get player by name"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM players WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_players(self) -> List[Dict]:
        """Get all players ordered by score"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM players 
                ORDER BY score DESC, created_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_player_score(self, name: str, new_score: int) -> bool:
        """Update player score"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                UPDATE players 
                SET score = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE name = ?
            """, (new_score, name))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_alliance(self, name: str, total_score: int = 0, members: int = 0, description: str = None) -> int:
        """Add a new alliance"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO alliances (name, total_score, members, description, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, total_score, members, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_alliance(self, name: str) -> Optional[Dict]:
        """Get alliance by name"""
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM alliances WHERE name = ?", (name,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_alliances(self) -> List[Dict]:
        """Get all alliances ordered by total score"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM alliances 
                ORDER BY total_score DESC, created_at ASC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_alliance_stats(self, name: str, total_score: int = None, members: int = None) -> bool:
        """Update alliance statistics"""
        updates = []
        params = []
        
        if total_score is not None:
            updates.append("total_score = ?")
            params.append(total_score)
        
        if members is not None:
            updates.append("members = ?")
            params.append(members)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(name)
        
        with self.get_connection() as conn:
            cursor = conn.execute(f"""
                UPDATE alliances 
                SET {', '.join(updates)}
                WHERE name = ?
            """, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def log_game_session(self, player_name: str, session_type: str, score_change: int, duration_seconds: int):
        """Log a game session"""
        player = self.get_player(player_name)
        if not player:
            return False
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO game_sessions (player_id, session_type, score_change, duration_seconds)
                VALUES (?, ?, ?, ?)
            """, (player['id'], session_type, score_change, duration_seconds))
            conn.commit()
            return True
    
    def get_player_sessions(self, player_name: str, limit: int = 10) -> List[Dict]:
        """Get recent game sessions for a player"""
        player = self.get_player(player_name)
        if not player:
            return []
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM game_sessions 
                WHERE player_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (player['id'], limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def log_system_event(self, level: str, message: str, module: str = None):
        """Log a system event"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO system_logs (level, message, module)
                VALUES (?, ?, ?)
            """, (level, message, module))
            conn.commit()
    
    def get_system_logs(self, level: str = None, limit: int = 100) -> List[Dict]:
        """Get system logs"""
        with self.get_connection() as conn:
            if level:
                cursor = conn.execute("""
                    SELECT * FROM system_logs 
                    WHERE level = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (level, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM system_logs 
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    def save_user_preferences(self, user_id: str, preferences: Dict, theme: str = 'default', language: str = 'en'):
        """Save user preferences"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_preferences (user_id, preferences, theme, language, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, json.dumps(preferences), theme, language))
            conn.commit()
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['preferences'] = json.loads(result['preferences'])
                return result
            return None
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            # Count tables
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            stats['tables'] = [row[0] for row in cursor.fetchall()]
            
            # Count records in each table
            for table in stats['tables']:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f'{table}_count'] = cursor.fetchone()[0]
            
            # Database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            stats['database_size_bytes'] = db_size
            stats['database_size_mb'] = round(db_size / (1024 * 1024), 2)
            
            return stats
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backups/agentdaf1_backup_{timestamp}.db"
        
        backup_dir = Path(backup_path).parent
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup
        with self.get_connection() as source:
            backup = sqlite3.connect(backup_path)
            source.backup(backup)
            backup.close()
        
        return backup_path
    
    def initialize_sample_data(self):
        """Initialize with sample data"""
        # Add sample players
        players = [
            ("AlphaPlayer", 1500, "Alpha Alliance", 15),
            ("BetaPlayer", 1200, "Beta Alliance", 12),
            ("GammaPlayer", 1800, "Gamma Alliance", 18),
            ("DeltaPlayer", 900, "Delta Alliance", 9),
            ("EpsilonPlayer", 1350, "Epsilon Alliance", 14)
        ]
        
        for name, score, alliance, level in players:
            self.add_player(name, score, alliance, level)
        
        # Add sample alliances
        alliances = [
            ("Alpha Alliance", 4500, 3, "Elite gaming alliance"),
            ("Beta Alliance", 3600, 3, "Competitive gaming group"),
            ("Gamma Alliance", 5400, 3, "Top tier alliance")
        ]
        
        for name, total_score, members, description in alliances:
            self.add_alliance(name, total_score, members, description)
        
        # Log system events
        self.log_system_event("INFO", "Database initialized with sample data", "database")
        self.log_system_event("INFO", "AgentDaf1.1 system started", "system")

# Global database instance
db_manager = DatabaseManager()

def get_db_manager() -> DatabaseManager:
    """Get global database manager instance"""
    return db_manager