"""
Enterprise Analytics Service
Advanced analytics and AI-powered insights for gaming data
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import redis
from prometheus_client import Counter, Histogram, Gauge
import time
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
ANALYTICS_REQUESTS = Counter('analytics_requests_total', 'Total analytics requests', ['type'])
ANALYSIS_DURATION = Histogram('analysis_duration_seconds', 'Analysis duration')
ML_MODEL_ACCURACY = Gauge('ml_model_accuracy', 'ML Model accuracy score')

class AnalyticsRequest(BaseModel):
    analysis_type: str
    parameters: Dict[str, Any] = {}
    time_range: Optional[str] = "7d"

class PredictionRequest(BaseModel):
    player_name: str
    prediction_type: str
    horizon_days: int = 7

class AnalyticsEngine:
    """Advanced analytics engine with ML capabilities"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        self.models = {}
        self.scalers = {}
        self.load_models()
        
    def load_models(self):
        """Load pre-trained ML models"""
        try:
            # Load anomaly detection model
            self.models['anomaly'] = joblib.load('models/anomaly_detector.pkl')
            self.scalers['anomaly'] = joblib.load('models/anomaly_scaler.pkl')
            
            # Load clustering model
            self.models['clustering'] = joblib.load('models/player_clustering.pkl')
            self.scalers['clustering'] = joblib.load('models/clustering_scaler.pkl')
            
            logger.info("ML models loaded successfully")
        except FileNotFoundError:
            logger.warning("ML models not found, training new ones...")
            self.train_models()
    
    def train_models(self):
        """Train ML models with current data"""
        try:
            # Get training data
            training_data = self.get_training_data()
            
            if len(training_data) < 50:
                logger.warning("Insufficient data for training models")
                return
            
            df = pd.DataFrame(training_data)
            
            # Train anomaly detection model
            self.train_anomaly_detector(df)
            
            # Train clustering model
            self.train_clustering_model(df)
            
            # Save models
            self.save_models()
            
            logger.info("ML models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
    
    def get_training_data(self) -> List[Dict[str, Any]]:
        """Get training data from database"""
        # This would normally query the database
        # For now, return mock data
        return [
            {"score": np.random.randint(1000, 50000), "change": np.random.randint(-500, 500), 
             "alliance_size": np.random.randint(5, 50), "activity_level": np.random.random()}
            for _ in range(200)
        ]
    
    def train_anomaly_detector(self, df: pd.DataFrame):
        """Train isolation forest for anomaly detection"""
        features = ['score', 'change', 'alliance_size', 'activity_level']
        X = df[features].fillna(0)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X_scaled)
        
        self.models['anomaly'] = model
        self.scalers['anomaly'] = scaler
        
        # Calculate accuracy
        predictions = model.predict(X_scaled)
        accuracy = (predictions == 1).mean()  # Normal data points
        ML_MODEL_ACCURACY.set(accuracy)
    
    def train_clustering_model(self, df: pd.DataFrame):
        """Train K-means clustering for player segmentation"""
        features = ['score', 'change', 'alliance_size', 'activity_level']
        X = df[features].fillna(0)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Find optimal number of clusters
        silhouette_scores = []
        K_range = range(2, 8)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42)
            cluster_labels = kmeans.fit_predict(X_scaled)
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)
        
        optimal_k = K_range[np.argmax(silhouette_scores)]
        
        # Train final model
        model = KMeans(n_clusters=optimal_k, random_state=42)
        model.fit(X_scaled)
        
        self.models['clustering'] = model
        self.scalers['clustering'] = scaler
    
    def save_models(self):
        """Save trained models to disk"""
        import os
        os.makedirs('models', exist_ok=True)
        
        joblib.dump(self.models['anomaly'], 'models/anomaly_detector.pkl')
        joblib.dump(self.scalers['anomaly'], 'models/anomaly_scaler.pkl')
        joblib.dump(self.models['clustering'], 'models/player_clustering.pkl')
        joblib.dump(self.scalers['clustering'], 'models/clustering_scaler.pkl')
    
    async def detect_anomalies(self, players_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalous player behavior"""
        if 'anomaly' not in self.models:
            return []
        
        df = pd.DataFrame(players_data)
        features = ['score', 'change', 'alliance_size', 'activity_level']
        
        # Ensure all features exist
        for feature in features:
            if feature not in df.columns:
                df[feature] = 0
        
        X = df[features].fillna(0)
        X_scaled = self.scalers['anomaly'].transform(X)
        
        predictions = self.models['anomaly'].predict(X_scaled)
        anomaly_scores = self.models['anomaly'].decision_function(X_scaled)
        
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
            if pred == -1:  # Anomaly
                anomalies.append({
                    "player_index": i,
                    "player_name": players_data[i].get('name', f'Player_{i}'),
                    "anomaly_score": float(score),
                    "severity": "high" if score < -0.5 else "medium",
                    "reasons": self.analyze_anomaly_reasons(players_data[i], score)
                })
        
        return anomalies
    
    def analyze_anomaly_reasons(self, player: Dict[str, Any], score: float) -> List[str]:
        """Analyze reasons for anomaly detection"""
        reasons = []
        
        if player.get('score', 0) > 40000:
            reasons.append("Extremely high score")
        
        if abs(player.get('change', 0)) > 300:
            reasons.append("Unusual score change")
        
        if player.get('activity_level', 0) < 0.1:
            reasons.append("Low activity level")
        
        if player.get('alliance_size', 0) > 40:
            reasons.append("Unusually large alliance")
        
        return reasons if reasons else ["Unusual pattern detected"]
    
    async def segment_players(self, players_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Segment players into behavioral clusters"""
        if 'clustering' not in self.models:
            return {"segments": [], "insights": []}
        
        df = pd.DataFrame(players_data)
        features = ['score', 'change', 'alliance_size', 'activity_level']
        
        # Ensure all features exist
        for feature in features:
            if feature not in df.columns:
                df[feature] = 0
        
        X = df[features].fillna(0)
        X_scaled = self.scalers['clustering'].transform(X)
        
        cluster_labels = self.models['clustering'].predict(X_scaled)
        
        segments = {}
        for i, label in enumerate(cluster_labels):
            segment_name = f"Segment_{label}"
            if segment_name not in segments:
                segments[segment_name] = {
                    "players": [],
                    "characteristics": self.get_segment_characteristics(label, X_scaled[cluster_labels == label])
                }
            
            segments[segment_name]["players"].append({
                "name": players_data[i].get('name', f'Player_{i}'),
                "score": players_data[i].get('score', 0),
                "cluster_confidence": float(np.linalg.norm(X_scaled[i] - self.models['clustering'].cluster_centers_[label]))
            })
        
        # Generate insights
        insights = self.generate_segment_insights(segments)
        
        return {
            "segments": segments,
            "insights": insights,
            "total_segments": len(segments)
        }
    
    def get_segment_characteristics(self, label: int, segment_data: np.ndarray) -> Dict[str, str]:
        """Get characteristics for a player segment"""
        center = self.models['clustering'].cluster_centers_[label]
        
        characteristics = []
        
        if center[0] > 0.5:  # High score
            characteristics.append("High performers")
        elif center[0] < -0.5:  # Low score
            characteristics.append("Developing players")
        
        if center[1] > 0.3:  # Positive change
            characteristics.append("Rapid growth")
        elif center[1] < -0.3:  # Negative change
            characteristics.append("Declining performance")
        
        if center[3] > 0.5:  # High activity
            characteristics.append("Highly active")
        elif center[3] < -0.5:  # Low activity
            characteristics.append("Low engagement")
        
        return {
            "name": f"Segment {label}",
            "traits": characteristics,
            "size": len(segment_data),
            "avg_score": float(np.mean(segment_data[:, 0])),
            "avg_change": float(np.mean(segment_data[:, 1]))
        }
    
    def generate_segment_insights(self, segments: Dict[str, Any]) -> List[str]:
        """Generate insights from player segmentation"""
        insights = []
        
        total_players = sum(len(seg["players"]) for seg in segments.values())
        
        # Find largest segment
        largest_segment = max(segments.values(), key=lambda x: len(x["players"]))
        insights.append(f"Largest segment represents {len(largest_segment['players'])/total_players*100:.1f}% of players")
        
        # Find high-value segment
        high_value_segments = [seg for seg in segments.values() 
                             if seg["characteristics"]["avg_score"] > 20000]
        if high_value_segments:
            insights.append(f"{len(high_value_segments)} segments contain high-value players")
        
        # Growth segments
        growth_segments = [seg for seg in segments.values() 
                          if "Rapid growth" in seg["characteristics"]["traits"]]
        if growth_segments:
            insights.append(f"{len(growth_segments)} segments show rapid growth")
        
        return insights
    
    async def predict_player_performance(self, player_data: Dict[str, Any], horizon_days: int = 7) -> Dict[str, Any]:
        """Predict player performance using time series analysis"""
        # Simple linear trend prediction (in production, use more sophisticated models)
        current_score = player_data.get('score', 0)
        recent_changes = player_data.get('recent_changes', [0])
        
        if not recent_changes:
            recent_changes = [0]
        
        avg_change = np.mean(recent_changes)
        trend = np.polyfit(range(len(recent_changes)), recent_changes, 1)[0] if len(recent_changes) > 1 else 0
        
        # Predict future scores
        predicted_scores = []
        score = current_score
        
        for day in range(horizon_days):
            daily_change = avg_change + (trend * day)
            score += daily_change
            predicted_scores.append(max(0, int(score)))  # Ensure non-negative
        
        # Calculate confidence intervals
        std_change = np.std(recent_changes) if len(recent_changes) > 1 else 100
        confidence_interval = std_change * np.sqrt(horizon_days)
        
        return {
            "player_name": player_data.get('name', 'Unknown'),
            "current_score": current_score,
            "predicted_scores": predicted_scores,
            "final_prediction": predicted_scores[-1],
            "confidence_interval": {
                "lower": max(0, predicted_scores[-1] - confidence_interval),
                "upper": predicted_scores[-1] + confidence_interval
            },
            "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
            "confidence": "high" if len(recent_changes) > 5 else "medium" if len(recent_changes) > 2 else "low"
        }
    
    async def generate_alliance_insights(self, alliances_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate AI-powered insights for alliances"""
        if not alliances_data:
            return {"insights": [], "recommendations": []}
        
        df = pd.DataFrame(alliances_data)
        
        insights = []
        recommendations = []
        
        # Performance analysis
        top_alliance = df.loc[df['total_score'].idxmax()]
        insights.append(f"Top alliance '{top_alliance['name']}' leads with {top_alliance['total_score']:,} points")
        
        # Balance analysis
        score_std = df['total_score'].std()
        if score_std > df['total_score'].mean() * 0.5:
            insights.append("High score variance between alliances indicates competitive imbalance")
            recommendations.append("Consider balancing mechanisms to ensure fair competition")
        
        # Size vs performance correlation
        if len(df) > 3:
            correlation = df['member_count'].corr(df['total_score'])
            if correlation > 0.7:
                insights.append("Strong correlation between alliance size and performance")
                recommendations.append("Smaller alliances may need advantages to compete effectively")
        
        # Growth opportunities
        underperforming = df[df['average_score'] < df['average_score'].quantile(0.25)]
        if len(underperforming) > 0:
            recommendations.append(f"{len(underperforming)} alliances show below-average performance and may benefit from training resources")
        
        return {
            "insights": insights,
            "recommendations": recommendations,
            "metrics": {
                "total_alliances": len(alliances_data),
                "average_score": float(df['total_score'].mean()),
                "score_variance": float(score_std),
                "performance_correlation": float(correlation) if len(df) > 3 else 0
            }
        }

class AnalyticsService:
    """Enterprise Analytics Service API"""
    
    def __init__(self):
        self.app = FastAPI(
            title="AgentDaf1.1 Analytics Service",
            description="Advanced analytics and AI-powered insights",
            version="3.0.0"
        )
        self.analytics_engine = AnalyticsEngine()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            # Retrain models periodically
            asyncio.create_task(self.periodic_model_training())
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "analytics"}
        
        @self.app.post("/analyze")
        async def perform_analysis(request: AnalyticsRequest):
            """Perform advanced analytics analysis"""
            start_time = time.time()
            
            try:
                ANALYTICS_REQUESTS.labels(type=request.analysis_type).inc()
                
                if request.analysis_type == "anomaly_detection":
                    players_data = await self.get_players_data()
                    result = await self.analytics_engine.detect_anomalies(players_data)
                
                elif request.analysis_type == "player_segmentation":
                    players_data = await self.get_players_data()
                    result = await self.analytics_engine.segment_players(players_data)
                
                elif request.analysis_type == "alliance_insights":
                    alliances_data = await self.get_alliances_data()
                    result = await self.analytics_engine.generate_alliance_insights(alliances_data)
                
                else:
                    raise HTTPException(status_code=400, detail="Invalid analysis type")
                
                ANALYSIS_DURATION.observe(time.time() - start_time)
                
                return {
                    "analysis_type": request.analysis_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "result": result
                }
                
            except Exception as e:
                logger.error(f"Analysis error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/predict")
        async def predict_performance(request: PredictionRequest):
            """Predict player performance"""
            try:
                player_data = await self.get_player_data(request.player_name)
                if not player_data:
                    raise HTTPException(status_code=404, detail="Player not found")
                
                result = await self.analytics_engine.predict_player_performance(
                    player_data, request.horizon_days
                )
                
                return {
                    "prediction_type": request.prediction_type,
                    "horizon_days": request.horizon_days,
                    "timestamp": datetime.utcnow().isoformat(),
                    "prediction": result
                }
                
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/insights/summary")
        async def get_insights_summary():
            """Get comprehensive insights summary"""
            try:
                players_data = await self.get_players_data()
                alliances_data = await self.get_alliances_data()
                
                # Generate all insights
                anomalies = await self.analytics_engine.detect_anomalies(players_data)
                segments = await self.analytics_engine.segment_players(players_data)
                alliance_insights = await self.analytics_engine.generate_alliance_insights(alliances_data)
                
                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "summary": {
                        "total_players": len(players_data),
                        "total_alliances": len(alliances_data),
                        "anomalies_detected": len(anomalies),
                        "player_segments": segments.get("total_segments", 0),
                        "key_insights": alliance_insights.get("insights", [])[:3]
                    },
                    "details": {
                        "anomalies": anomalies[:5],  # Top 5 anomalies
                        "segments": {k: v["characteristics"] for k, v in segments.get("segments", {}).items()},
                        "alliance_insights": alliance_insights
                    }
                }
                
            except Exception as e:
                logger.error(f"Insights summary error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def periodic_model_training(self):
        """Periodically retrain ML models"""
        while True:
            try:
                await asyncio.sleep(86400)  # Train daily
                logger.info("Starting periodic model training...")
                self.analytics_engine.train_models()
                logger.info("Model training completed")
            except Exception as e:
                logger.error(f"Periodic training error: {e}")
    
    async def get_players_data(self) -> List[Dict[str, Any]]:
        """Get players data from data service"""
        try:
            # This would normally call the data service API
            # For now, return mock data
            return [
                {
                    "name": f"Player_{i}",
                    "score": np.random.randint(1000, 50000),
                    "change": np.random.randint(-500, 500),
                    "alliance_size": np.random.randint(5, 50),
                    "activity_level": np.random.random(),
                    "recent_changes": [np.random.randint(-100, 100) for _ in range(np.random.randint(3, 10))]
                }
                for i in range(100)
            ]
        except Exception as e:
            logger.error(f"Error getting players data: {e}")
            return []
    
    async def get_alliances_data(self) -> List[Dict[str, Any]]:
        """Get alliances data from data service"""
        try:
            # This would normally call the data service API
            return [
                {
                    "name": f"Alliance_{chr(65+i)}",
                    "total_score": np.random.randint(50000, 500000),
                    "member_count": np.random.randint(10, 100),
                    "average_score": np.random.randint(1000, 10000)
                }
                for i in range(12)
            ]
        except Exception as e:
            logger.error(f"Error getting alliances data: {e}")
            return []
    
    async def get_player_data(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get specific player data"""
        players = await self.get_players_data()
        for player in players:
            if player.get('name') == player_name:
                return player
        return None

# Initialize service
analytics_service = AnalyticsService()
app = analytics_service.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)