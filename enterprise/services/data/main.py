"""
Enterprise Data Service
Handles all data operations, validation, processing, and storage
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, validator
import asyncpg
import redis
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
import io
import openpyxl
from prometheus_client import Counter, Histogram, Gauge
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
DATA_OPERATIONS = Counter('data_operations_total', 'Total data operations', ['operation', 'status'])
DATA_PROCESSING_TIME = Histogram('data_processing_seconds', 'Data processing time')
ACTIVE_CONNECTIONS = Gauge('data_active_connections', 'Active database connections')

# Pydantic models
class Player(BaseModel):
    name: str
    alliance: str
    score: int
    rank: Optional[int] = None
    change: Optional[int] = None
    last_active: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Player name cannot be empty')
        return v.strip()
    
    @validator('score')
    def validate_score(cls, v):
        if v < 0:
            raise ValueError('Score cannot be negative')
        return v

class Alliance(BaseModel):
    name: str
    total_score: int
    member_count: int
    average_score: float
    rank: Optional[int] = None

class DataBatch(BaseModel):
    players: List[Player]
    timestamp: datetime
    source: str
    metadata: Optional[Dict[str, Any]] = {}

class DatabaseManager:
    """Enterprise database manager with connection pooling"""
    
    def __init__(self):
        self.pool = None
        self.redis_client = None
        self.engine = None
        self.SessionLocal = None
    
    async def initialize(self):
        """Initialize database connections"""
        # PostgreSQL connection pool
        self.pool = await asyncpg.create_pool(
            host='postgres',
            port=5432,
            database='agentdaf',
            user='agentdaf_user',
            password='secure_password',
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Redis connection
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        # SQLAlchemy for complex operations
        self.engine = create_engine('postgresql://agentdaf_user:secure_password@postgres:5432/agentdaf')
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        await self.create_tables()
        
        logger.info("Database connections initialized")
    
    async def create_tables(self):
        """Create database tables"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    alliance VARCHAR(255),
                    score INTEGER DEFAULT 0,
                    rank INTEGER,
                    change INTEGER DEFAULT 0,
                    last_active TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS alliances (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    total_score INTEGER DEFAULT 0,
                    member_count INTEGER DEFAULT 0,
                    average_score FLOAT DEFAULT 0,
                    rank INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS data_snapshots (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP NOT NULL,
                    player_count INTEGER,
                    alliance_count INTEGER,
                    total_score BIGINT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_players_name ON players(name)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_players_alliance ON players(alliance)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_players_score ON players(score DESC)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_alliances_name ON alliances(name)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_alliances_score ON alliances(total_score DESC)')
            await conn.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON data_snapshots(timestamp DESC)')

class DataProcessor:
    """Advanced data processing with analytics"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def process_excel_file(self, file_content: bytes, source: str = "upload") -> Dict[str, Any]:
        """Process Excel file with advanced validation"""
        start_time = time.time()
        
        try:
            # Read Excel file
            df = pd.read_excel(io.BytesIO(file_content))
            
            # Data validation and cleaning
            df = self.validate_and_clean_data(df)
            
            # Convert to player objects
            players = []
            for _, row in df.iterrows():
                player = Player(
                    name=str(row.get('name', '')).strip(),
                    alliance=str(row.get('alliance', '')).strip(),
                    score=int(row.get('score', 0)),
                    rank=int(row.get('rank', 0)) if pd.notna(row.get('rank')) else None,
                    change=int(row.get('change', 0)) if pd.notna(row.get('change')) else None
                )
                players.append(player)
            
            # Process batch
            result = await self.process_player_batch(players, source)
            
            # Record metrics
            DATA_PROCESSING_TIME.observe(time.time() - start_time)
            DATA_OPERATIONS.labels(operation='excel_import', status='success').inc()
            
            return result
            
        except Exception as e:
            DATA_OPERATIONS.labels(operation='excel_import', status='error').inc()
            logger.error(f"Error processing Excel file: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
    
    def validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean DataFrame"""
        # Required columns
        required_columns = ['name', 'score']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean data
        df = df.dropna(subset=['name', 'score'])
        df['name'] = df['name'].astype(str).str.strip()
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
        
        if 'alliance' in df.columns:
            df['alliance'] = df['alliance'].astype(str).str.strip()
        else:
            df['alliance'] = ''
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['name'], keep='last')
        
        return df
    
    async def process_player_batch(self, players: List[Player], source: str) -> Dict[str, Any]:
        """Process batch of player data with analytics"""
        async with self.db_manager.pool.acquire() as conn:
            ACTIVE_CONNECTIONS.inc()
            
            try:
                # Start transaction
                async with conn.transaction():
                    # Update players
                    updated_players = 0
                    new_players = 0
                    
                    for player in players:
                        # Check if player exists
                        existing = await conn.fetchrow(
                            'SELECT id FROM players WHERE name = $1', player.name
                        )
                        
                        if existing:
                            # Update existing player
                            await conn.execute('''
                                UPDATE players 
                                SET alliance = $1, score = $2, rank = $3, change = $4, 
                                    last_active = $5, updated_at = CURRENT_TIMESTAMP
                                WHERE name = $6
                            ''', player.alliance, player.score, player.rank, 
                                player.change, datetime.utcnow(), player.name)
                            updated_players += 1
                        else:
                            # Insert new player
                            await conn.execute('''
                                INSERT INTO players (name, alliance, score, rank, change, last_active)
                                VALUES ($1, $2, $3, $4, $5, $6)
                            ''', player.name, player.alliance, player.score, 
                                player.rank, player.change, datetime.utcnow())
                            new_players += 1
                    
                    # Update alliances
                    await self.update_alliance_stats(conn)
                    
                    # Create snapshot
                    await self.create_snapshot(conn, players, source)
                    
                    # Cache data in Redis
                    await self.cache_current_data(conn)
                
                return {
                    "status": "success",
                    "players_processed": len(players),
                    "new_players": new_players,
                    "updated_players": updated_players,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
            finally:
                ACTIVE_CONNECTIONS.dec()
    
    async def update_alliance_stats(self, conn):
        """Update alliance statistics"""
        await conn.execute('''
            INSERT INTO alliances (name, total_score, member_count, average_score)
            SELECT 
                alliance,
                SUM(score) as total_score,
                COUNT(*) as member_count,
                AVG(score) as average_score
            FROM players 
            WHERE alliance IS NOT NULL AND alliance != ''
            GROUP BY alliance
            ON CONFLICT (name) DO UPDATE SET
                total_score = EXCLUDED.total_score,
                member_count = EXCLUDED.member_count,
                average_score = EXCLUDED.average_score,
                updated_at = CURRENT_TIMESTAMP
        ''')
    
    async def create_snapshot(self, conn, players: List[Player], source: str):
        """Create data snapshot for historical analysis"""
        player_count = len(players)
        alliance_count = len(set(p.alliance for p in players if p.alliance))
        total_score = sum(p.score for p in players)
        
        await conn.execute('''
            INSERT INTO data_snapshots (timestamp, player_count, alliance_count, total_score, metadata)
            VALUES ($1, $2, $3, $4, $5)
        ''', datetime.utcnow(), player_count, alliance_count, total_score, 
            {"source": source, "players": len(players)})
    
    async def cache_current_data(self, conn):
        """Cache current data in Redis for fast access"""
        # Get current player data
        players = await conn.fetch('''
            SELECT name, alliance, score, rank, change, last_active
            FROM players 
            ORDER BY score DESC
        ''')
        
        # Get alliance data
        alliances = await conn.fetch('''
            SELECT name, total_score, member_count, average_score, rank
            FROM alliances 
            ORDER BY total_score DESC
        ''')
        
        # Cache in Redis
        player_data = [dict(p) for p in players]
        alliance_data = [dict(a) for a in alliances]
        
        self.db_manager.redis_client.setex(
            'current_players', 300,  # 5 minutes TTL
            json.dumps(player_data)
        )
        
        self.db_manager.redis_client.setex(
            'current_alliances', 300,
            json.dumps(alliance_data)
        )

class DataService:
    """Enterprise Data Service API"""
    
    def __init__(self):
        self.app = FastAPI(
            title="AgentDaf1.1 Data Service",
            description="Enterprise Data Processing Service",
            version="3.0.0"
        )
        self.db_manager = DatabaseManager()
        self.data_processor = DataProcessor(self.db_manager)
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.db_manager.initialize()
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "data"}
        
        @self.app.post("/upload/excel")
        async def upload_excel(file_content: bytes = b"", background_tasks: BackgroundTasks = BackgroundTasks()):
            """Upload and process Excel file"""
            if not file_content:
                raise HTTPException(status_code=400, detail="No file content provided")
            
            result = await self.data_processor.process_excel_file(file_content)
            return result
        
        @self.app.get("/players")
        async def get_players(limit: int = 100, offset: int = 0, alliance: Optional[str] = None):
            """Get players with pagination and filtering"""
            cache_key = f"players:{limit}:{offset}:{alliance}"
            cached = self.db_manager.redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            async with self.db_manager.pool.acquire() as conn:
                query = 'SELECT * FROM players'
                params = []
                
                if alliance:
                    query += ' WHERE alliance = $1'
                    params.append(alliance)
                
                query += ' ORDER BY score DESC LIMIT $%d OFFSET $%d' % (len(params) + 1, len(params) + 2)
                params.extend([limit, offset])
                
                players = await conn.fetch(query, *params)
                result = [dict(p) for p in players]
                
                # Cache for 1 minute
                self.db_manager.redis_client.setex(cache_key, 60, json.dumps(result))
                
                return result
        
        @self.app.get("/alliances")
        async def get_alliances(limit: int = 50, offset: int = 0):
            """Get alliances with pagination"""
            cache_key = f"alliances:{limit}:{offset}"
            cached = self.db_manager.redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            async with self.db_manager.pool.acquire() as conn:
                alliances = await conn.fetch('''
                    SELECT * FROM alliances 
                    ORDER BY total_score DESC 
                    LIMIT $1 OFFSET $2
                ''', limit, offset)
                
                result = [dict(a) for a in alliances]
                self.db_manager.redis_client.setex(cache_key, 60, json.dumps(result))
                
                return result
        
        @self.app.get("/statistics")
        async def get_statistics():
            """Get comprehensive statistics"""
            cache_key = "statistics"
            cached = self.db_manager.redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            async with self.db_manager.pool.acquire() as conn:
                stats = await conn.fetchrow('''
                    SELECT 
                        COUNT(*) as total_players,
                        COUNT(DISTINCT alliance) as total_alliances,
                        SUM(score) as total_score,
                        AVG(score) as avg_score,
                        MAX(score) as max_score,
                        MIN(score) as min_score
                    FROM players
                ''')
                
                result = dict(stats)
                self.db_manager.redis_client.setex(cache_key, 30, json.dumps(result))
                
                return result

# Initialize service
data_service = DataService()
app = data_service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)