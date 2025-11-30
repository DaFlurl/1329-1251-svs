-- AgentDaf1.1 Database Initialization
-- Create database schema

-- Players table
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    score INTEGER DEFAULT 0,
    alliance VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alliances table
CREATE TABLE IF NOT EXISTS alliances (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    total_score INTEGER DEFAULT 0,
    member_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Game sessions table
CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    session_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Score history table
CREATE TABLE IF NOT EXISTS score_history (
    id SERIAL PRIMARY KEY,
    player_id INTEGER REFERENCES players(id),
    score INTEGER NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
CREATE INDEX IF NOT EXISTS idx_players_alliance ON players(alliance);
CREATE INDEX IF NOT EXISTS idx_score_history_player ON score_history(player_id);
CREATE INDEX IF NOT EXISTS idx_score_history_recorded ON score_history(recorded_at);

-- Insert sample data
INSERT INTO players (name, score, alliance) VALUES 
('AlphaPlayer', 1500, 'Alpha Alliance'),
('BetaPlayer', 1200, 'Beta Alliance'),
('GammaPlayer', 1800, 'Gamma Alliance')
ON CONFLICT DO NOTHING;

INSERT INTO alliances (name, total_score, member_count) VALUES 
('Alpha Alliance', 4500, 3),
('Beta Alliance', 3600, 3),
('Gamma Alliance', 5400, 3)
ON CONFLICT DO NOTHING;
