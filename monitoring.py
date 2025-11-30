#!/usr/bin/env python3
"""
AgentDaf1.1 Monitoring and Alerting System
Real-time system monitoring with alerting capabilities
"""

import psutil
import time
import json
import smtplib
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MimeMultipart
import logging
from dataclasses import dataclass
from enum import Enum

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class MetricThreshold:
    """Metric threshold configuration"""
    name: str
    warning_threshold: float
    critical_threshold: float
    operator: str = ">"  # >, <, >=, <=, ==, !=
    unit: str = ""

class MonitoringSystem:
    """Main monitoring and alerting system"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self.alerts: List[Alert] = []
        self.metrics_history: List[Dict] = []
        self.logger = self._setup_logger()
        self.alert_handlers: Dict[AlertLevel, List[Callable]] = {
            AlertLevel.INFO: [],
            AlertLevel.WARNING: [],
            AlertLevel.ERROR: [],
            AlertLevel.CRITICAL: []
        }
        
    def _load_config(self) -> Dict:
        """Load monitoring configuration"""
        default_config = {
            "monitoring": {
                "interval_seconds": 60,
                "metrics_retention_hours": 24,
                "alerts_retention_days": 7
            },
            "thresholds": {
                "cpu_usage": {"warning": 70, "critical": 90, "unit": "%"},
                "memory_usage": {"warning": 75, "critical": 90, "unit": "%"},
                "disk_usage": {"warning": 80, "critical": 95, "unit": "%"},
                "response_time": {"warning": 2000, "critical": 5000, "unit": "ms"},
                "error_rate": {"warning": 5, "critical": 10, "unit": "%"}
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "from_email": "",
                    "to_emails": []
                },
                "webhook": {
                    "enabled": False,
                    "url": "",
                    "headers": {}
                }
            },
            "health_checks": {
                "enabled": True,
                "endpoints": [
                    {"name": "main_app", "url": "http://localhost:8080/api/health", "timeout": 10}
                ]
            }
        }
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in loaded_config:
                        loaded_config[key] = value
                return loaded_config
            except Exception as e:
                logger.info(f"Error loading config: {e}")
                return default_config
        else:
            # Create default config file
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """Setup monitoring logger"""
        logger = logging.getLogger('monitoring_system')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler('logs/monitoring.log')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        return logger
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "used": psutil.virtual_memory().used,
                "usage_percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "usage_percent": (psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv,
                "packets_sent": psutil.net_io_counters().packets_sent,
                "packets_recv": psutil.net_io_counters().packets_recv
            }
        }
        
        # Add process-specific metrics
        try:
            process = psutil.Process()
            metrics["process"] = {
                "pid": process.pid,
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
        except psutil.NoSuchProcess:
            pass
        
        return metrics
    
    def check_health_endpoints(self) -> Dict[str, Any]:
        """Check application health endpoints"""
        results = {}
        
        for endpoint in self.config["health_checks"]["endpoints"]:
            name = endpoint["name"]
            url = endpoint["url"]
            timeout = endpoint.get("timeout", 10)
            
            try:
                start_time = time.time()
                response = requests.get(url, timeout=timeout)
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                results[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Check response content if available
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        if data.get('status') == 'healthy':
                            results[name]["app_status"] = "healthy"
                        else:
                            results[name]["app_status"] = "degraded"
                    except:
                        pass
                        
            except requests.exceptions.Timeout:
                results[name] = {
                    "status": "timeout",
                    "error": f"Request timeout after {timeout}s",
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return results
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        thresholds = self.config["thresholds"]
        
        # CPU usage check
        cpu_usage = metrics["cpu"]["usage_percent"]
        if cpu_usage >= thresholds["cpu_usage"]["critical_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.CRITICAL,
                "High CPU Usage",
                f"CPU usage is {cpu_usage:.1f}%",
                "system",
                {"cpu_usage": cpu_usage, "threshold": thresholds["cpu_usage"]["critical_threshold"]}
            ))
        elif cpu_usage >= thresholds["cpu_usage"]["warning_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.WARNING,
                "Elevated CPU Usage",
                f"CPU usage is {cpu_usage:.1f}%",
                "system",
                {"cpu_usage": cpu_usage, "threshold": thresholds["cpu_usage"]["warning_threshold"]}
            ))
        
        # Memory usage check
        memory_usage = metrics["memory"]["usage_percent"]
        if memory_usage >= thresholds["memory_usage"]["critical_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.CRITICAL,
                "High Memory Usage",
                f"Memory usage is {memory_usage:.1f}%",
                "system",
                {"memory_usage": memory_usage, "threshold": thresholds["memory_usage"]["critical_threshold"]}
            ))
        elif memory_usage >= thresholds["memory_usage"]["warning_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.WARNING,
                "Elevated Memory Usage",
                f"Memory usage is {memory_usage:.1f}%",
                "system",
                {"memory_usage": memory_usage, "threshold": thresholds["memory_usage"]["warning_threshold"]}
            ))
        
        # Disk usage check
        disk_usage = metrics["disk"]["usage_percent"]
        if disk_usage >= thresholds["disk_usage"]["critical_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.CRITICAL,
                "High Disk Usage",
                f"Disk usage is {disk_usage:.1f}%",
                "system",
                {"disk_usage": disk_usage, "threshold": thresholds["disk_usage"]["critical_threshold"]}
            ))
        elif disk_usage >= thresholds["disk_usage"]["warning_threshold"]:
            alerts.append(self._create_alert(
                AlertLevel.WARNING,
                "Elevated Disk Usage",
                f"Disk usage is {disk_usage:.1f}%",
                "system",
                {"disk_usage": disk_usage, "threshold": thresholds["disk_usage"]["warning_threshold"]}
            ))
        
        return alerts
    
    def _create_alert(self, level: AlertLevel, title: str, message: str, 
                     source: str, metadata: Dict[str, Any]) -> Alert:
        """Create a new alert"""
        alert_id = f"{int(time.time())}_{hash(title)}"
        alert = Alert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            timestamp=datetime.now(),
            source=source,
            metadata=metadata
        )
        
        # Add to alerts list
        self.alerts.append(alert)
        
        # Log alert
        self.logger.warning(f"ALERT [{level.value.upper()}] {title}: {message}")
        
        # Trigger alert handlers
        self._trigger_alert_handlers(alert)
        
        return alert
    
    def _trigger_alert_handlers(self, alert: Alert):
        """Trigger all alert handlers for the alert level"""
        handlers = self.alert_handlers.get(alert.level, [])
        
        # Email notification
        if self.config["notifications"]["email"]["enabled"]:
            self._send_email_alert(alert)
        
        # Webhook notification
        if self.config["notifications"]["webhook"]["enabled"]:
            self._send_webhook_alert(alert)
        
        # Custom handlers
        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert"""
        try:
            email_config = self.config["notifications"]["email"]
            
            msg = MimeMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = f"[AgentDaf1.1 ALERT] {alert.title}"
            
            body = f"""
Alert Level: {alert.level.value.upper()}
Title: {alert.title}
Message: {alert.message}
Source: {alert.source}
Timestamp: {alert.timestamp}

Metadata:
{json.dumps(alert.metadata, indent=2)}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email alert sent: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def _send_webhook_alert(self, alert: Alert):
        """Send webhook alert"""
        try:
            webhook_config = self.config["notifications"]["webhook"]
            
            payload = {
                "alert_id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata
            }
            
            response = requests.post(
                webhook_config["url"],
                json=payload,
                headers=webhook_config.get("headers", {}),
                timeout=10
            )
            
            response.raise_for_status()
            self.logger.info(f"Webhook alert sent: {alert.title}")
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")
    
    def add_alert_handler(self, level: AlertLevel, handler: Callable[[Alert], None]):
        """Add custom alert handler"""
        if level not in self.alert_handlers:
            self.alert_handlers[level] = []
        self.alert_handlers[level].append(handler)
    
    def get_active_alerts(self, level: AlertLevel = None) -> List[Alert]:
        """Get active (unresolved) alerts"""
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        
        if level:
            active_alerts = [alert for alert in active_alerts if alert.level == level]
        
        return sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                self.logger.info(f"Alert resolved: {alert.title}")
                return True
        return False
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics data available"}
        
        # Calculate averages and maxes
        cpu_values = [m["cpu"]["usage_percent"] for m in recent_metrics]
        memory_values = [m["memory"]["usage_percent"] for m in recent_metrics]
        disk_values = [m["disk"]["usage_percent"] for m in recent_metrics]
        
        return {
            "period_hours": hours,
            "data_points": len(recent_metrics),
            "cpu": {
                "avg": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values)
            },
            "memory": {
                "avg": sum(memory_values) / len(memory_values),
                "max": max(memory_values),
                "min": min(memory_values)
            },
            "disk": {
                "avg": sum(disk_values) / len(disk_values),
                "max": max(disk_values),
                "min": min(disk_values)
            }
        }
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        interval = self.config["monitoring"]["interval_seconds"]
        
        self.logger.info(f"Starting monitoring with {interval}s interval")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Check health endpoints
                if self.config["health_checks"]["enabled"]:
                    health_results = self.check_health_endpoints()
                    metrics["health_checks"] = health_results
                
                # Check thresholds
                alerts = self.check_thresholds(metrics)
                
                # Cleanup old data
                self._cleanup_old_data()
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _cleanup_old_data(self):
        """Clean up old metrics and alerts"""
        # Clean old metrics
        retention_hours = self.config["monitoring"]["metrics_retention_hours"]
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        self.metrics_history = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]
        
        # Clean old resolved alerts
        retention_days = self.config["monitoring"]["alerts_retention_days"]
        alert_cutoff = datetime.now() - timedelta(days=retention_days)
        
        self.alerts = [
            alert for alert in self.alerts 
            if not alert.resolved or (alert.resolved_at and alert.resolved_at > alert_cutoff)
        ]
    
    def get_status_dashboard(self) -> Dict[str, Any]:
        """Get current system status for dashboard"""
        current_metrics = self.collect_system_metrics()
        active_alerts = self.get_active_alerts()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy" if len([a for a in active_alerts if a.level in [AlertLevel.ERROR, AlertLevel.CRITICAL]]) == 0 else "degraded",
            "metrics": current_metrics,
            "active_alerts": len(active_alerts),
            "critical_alerts": len([a for a in active_alerts if a.level == AlertLevel.CRITICAL]),
            "warning_alerts": len([a for a in active_alerts if a.level == AlertLevel.WARNING]),
            "recent_alerts": [
                {
                    "id": alert.id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "timestamp": alert.timestamp.isoformat()
                }
                for alert in active_alerts[:10]
            ]
        }

# Global monitoring instance
monitoring_system = MonitoringSystem()

def get_monitoring_system() -> MonitoringSystem:
    """Get global monitoring system instance"""
    return monitoring_system

# Flask routes for monitoring
def create_monitoring_routes(app):
    """Create monitoring routes for Flask app"""
    
    @app.route('/api/monitoring/status')
    def monitoring_status():
        """Get current monitoring status"""
        return jsonify({
            'status': 'success',
            'data': monitoring_system.get_status_dashboard()
        })
    
    @app.route('/api/monitoring/metrics')
    def monitoring_metrics():
        """Get metrics summary"""
        hours = request.args.get('hours', 24, type=int)
        return jsonify({
            'status': 'success',
            'data': monitoring_system.get_metrics_summary(hours)
        })
    
    @app.route('/api/monitoring/alerts')
    def monitoring_alerts():
        """Get active alerts"""
        level = request.args.get('level')
        alert_level = AlertLevel(level) if level else None
        
        alerts = monitoring_system.get_active_alerts(alert_level)
        return jsonify({
            'status': 'success',
            'data': [
                {
                    'id': alert.id,
                    'level': alert.level.value,
                    'title': alert.title,
                    'message': alert.message,
                    'source': alert.source,
                    'timestamp': alert.timestamp.isoformat(),
                    'metadata': alert.metadata
                }
                for alert in alerts
            ]
        })
    
    @app.route('/api/monitoring/alerts/<alert_id>/resolve', methods=['POST'])
    def resolve_alert(alert_id):
        """Resolve an alert"""
        success = monitoring_system.resolve_alert(alert_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Alert {alert_id} resolved'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Alert {alert_id} not found or already resolved'
            }), 404

if __name__ == "__main__":
    # Start monitoring standalone
    monitoring_system.start_monitoring()