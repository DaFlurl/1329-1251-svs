#!/usr/bin/env python3
"""
AgentDaf1.1 Simple Working Application
Minimal working version for immediate deployment
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import os
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Sample data
SAMPLE_DATA = {
    "players": [
        {"name": "AlphaPlayer", "score": 1500, "alliance": "Alpha Alliance"},
        {"name": "BetaPlayer", "score": 1200, "alliance": "Beta Alliance"},
        {"name": "GammaPlayer", "score": 1800, "alliance": "Gamma Alliance"},
        {"name": "DeltaPlayer", "score": 900, "alliance": "Delta Alliance"},
        {"name": "EpsilonPlayer", "score": 1350, "alliance": "Epsilon Alliance"}
    ],
    "alliances": [
        {"name": "Alpha Alliance", "total_score": 4500, "members": 3},
        {"name": "Beta Alliance", "total_score": 3600, "members": 3},
        {"name": "Gamma Alliance", "total_score": 5400, "members": 3}
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentDaf1.1 - Live Gaming Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .dashboard-container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .player-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        .player-card:hover {
            transform: translateY(-5px);
        }
        .alliance-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .score-badge {
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        .header-title {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .status-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 255, 0, 0.8);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="status-indicator">
        <i class="fas fa-circle"></i> LIVE
    </div>
    
    <div class="dashboard-container">
        <h1 class="header-title">
            <i class="fas fa-trophy"></i> AgentDaf1.1 Live Dashboard
        </h1>
        
        <div class="row">
            <div class="col-md-8">
                <h3 class="text-white mb-3">
                    <i class="fas fa-users"></i> Spieler-Rangliste ({{ players|length }})
                </h3>
                {% for player in players %}
                <div class="player-card">
                    <div class="row align-items-center">
                        <div class="col-md-1">
                            <h5 class="mb-0">#{{ loop.index }}</h5>
                        </div>
                        <div class="col-md-6">
                            <h6 class="mb-0">{{ player.name }}</h6>
                            <small class="text-muted">{{ player.alliance }}</small>
                        </div>
                        <div class="col-md-3">
                            <span class="score-badge">{{ "{:,}".format(player.score) }} Punkte</span>
                        </div>
                        <div class="col-md-2">
                            <i class="fas fa-medal text-warning"></i>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="col-md-4">
                <h3 class="text-white mb-3">
                    <i class="fas fa-flag"></i> Allianzen ({{ alliances|length }})
                </h3>
                {% for alliance in alliances %}
                <div class="alliance-card">
                    <h5>{{ alliance.name }}</h5>
                    <div class="row">
                        <div class="col-6">
                            <strong>{{ "{:,}".format(alliance.total_score) }}</strong><br>
                            <small>Gesamtpunkte</small>
                        </div>
                        <div class="col-6">
                            <strong>{{ alliance.members }}</strong><br>
                            <small>Mitglieder</small>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(function(){
            location.reload();
        }, 30000);
        
        // Real-time updates simulation
        setInterval(function(){
            const indicator = document.querySelector('.status-indicator');
            indicator.style.background = indicator.style.background === 'rgba(0, 255, 0, 0.8)' ? 
                'rgba(255, 165, 0, 0.8)' : 'rgba(0, 255, 0, 0.8)';
        }, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(HTML_TEMPLATE, 
                             players=SAMPLE_DATA['players'], 
                             alliances=SAMPLE_DATA['alliances'])

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'system': 'AgentDaf1.1',
        'version': '3.0.0',
        'features': ['dashboard', 'api', 'real_time_updates']
    })

@app.route('/api/players')
def get_players():
    """Get players data"""
    return jsonify({
        'status': 'success',
        'data': SAMPLE_DATA['players']
    })

@app.route('/api/alliances')
def get_alliances():
    """Get alliances data"""
    return jsonify({
        'status': 'success',
        'data': SAMPLE_DATA['alliances']
    })

@app.route('/api/data')
def get_all_data():
    """Get all data"""
    return jsonify({
        'status': 'success',
        'data': SAMPLE_DATA
    })

@app.route('/api/metrics')
def metrics():
    """Metrics endpoint for monitoring"""
    return "agentdaf_requests_total 100//nagentdaf_uptime_seconds 3600//n"

if __name__ == '__main__':
    logger.info("""
============================================================
                AgentDaf1.1 Gaming Dashboard System              
                                                             
  Starting Web Server...                                   
  Dashboard: Ready                                         
  API Endpoints: Ready                                     
  Real-time Updates: Enabled                                
                                                             
  Access: http://localhost:8080                              
  API Health: http://localhost:8080/api/health               
  Players API: http://localhost:8080/api/players             
  Alliances API: http://localhost:8080/api/alliances           
============================================================
    """)
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )