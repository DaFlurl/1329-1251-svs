#!/usr/bin/env python3
"""
AgentDaf1.1 System Health Monitor
Real-time monitoring and alerting system
"""

import asyncio
import time
import json
import logging
import psutil
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Health metric data structure"""
    name: str
    value: float
    unit: str
    status: str  # healthy, warning, critical
    threshold_warning: float
    threshold_critical: float
    timestamp: datetime
    description: str

@dataclass
class ServiceHealth:
    """Service health status"""
    name: str
    status: str  # up, down, degraded
    response_time: Optional[float] = None
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    uptime_percentage: float = 100.0

class SystemHealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.metrics_history = []
        self.services_status = {}
        self.alerts = []
        self.check_interval = 30  # seconds
        self.session = None
        
        # Service endpoints to monitor
        self.service_endpoints = {
            "RabbitMQ": "http://localhost:15672/api/overview",
            "Redis": "http://localhost:6383",
            "PostgreSQL": "http://localhost:5435",
            "Elasticsearch": "http://localhost:9200/_cluster/health",
            "Kibana": "http://localhost:5601/api/status",
            "Prometheus": "http://localhost:9091/-/healthy",
            "Grafana": "http://localhost:3001/api/health",
            "Jaeger": "http://localhost:16686/"
        }
        
        # Metric thresholds
        self.thresholds = {
            "cpu_usage": {"warning": 70, "critical": 90},
            "memory_usage": {"warning": 75, "critical": 90},
            "disk_usage": {"warning": 80, "critical": 95},
            "response_time": {"warning": 1000, "critical": 5000}  # ms
        }
    
    async def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("🏥 Starting System Health Monitor...")
        
        # Create HTTP session
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
        
        try:
            while True:
                await self.collect_all_metrics()
                await self.check_all_services()
                await self.evaluate_alerts()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("⏹️ Health monitor stopped by user")
        finally:
            if self.session:
                await self.session.close()
    
    async def collect_all_metrics(self) -> List[HealthMetric]:
        """Collect all system metrics"""
        metrics = []
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(HealthMetric(
            name="cpu_usage",
            value=cpu_percent,
            unit="%",
            status=self.get_metric_status(cpu_percent, "cpu_usage"),
            threshold_warning=self.thresholds["cpu_usage"]["warning"],
            threshold_critical=self.thresholds["cpu_usage"]["critical"],
            timestamp=datetime.now(),
            description="CPU utilization percentage"
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(HealthMetric(
            name="memory_usage",
            value=memory.percent,
            unit="%",
            status=self.get_metric_status(memory.percent, "memory_usage"),
            threshold_warning=self.thresholds["memory_usage"]["warning"],
            threshold_critical=self.thresholds["memory_usage"]["critical"],
            timestamp=datetime.now(),
            description="Memory utilization percentage"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        metrics.append(HealthMetric(
            name="disk_usage",
            value=disk_percent,
            unit="%",
            status=self.get_metric_status(disk_percent, "disk_usage"),
            threshold_warning=self.thresholds["disk_usage"]["warning"],
            threshold_critical=self.thresholds["disk_usage"]["critical"],
            timestamp=datetime.now(),
            description="Disk utilization percentage"
        ))
        
        # Network metrics
        network = psutil.net_io_counters()
        metrics.append(HealthMetric(
            name="network_bytes_sent",
            value=network.bytes_sent,
            unit="bytes",
            status="healthy",
            threshold_warning=0,
            threshold_critical=0,
            timestamp=datetime.now(),
            description="Total bytes sent"
        ))
        
        metrics.append(HealthMetric(
            name="network_bytes_recv",
            value=network.bytes_recv,
            unit="bytes",
            status="healthy",
            threshold_warning=0,
            threshold_critical=0,
            timestamp=datetime.now(),
            description="Total bytes received"
        ))
        
        # Store metrics
        self.metrics_history.extend(metrics)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        return metrics
    
    async def check_all_services(self) -> Dict[str, ServiceHealth]:
        """Check health of all services"""
        for service_name, endpoint in self.service_endpoints.items():
            health = await self.check_service_health(service_name, endpoint)
            self.services_status[service_name] = health
        
        return self.services_status
    
    async def check_service_health(self, service_name: str, endpoint: str) -> ServiceHealth:
        """Check individual service health"""
        start_time = time.time()
        
        try:
            async with self.session.get(endpoint) as response:
                response_time = (time.time() - start_time) * 1000  # Convert to ms
                
                if response.status == 200:
                    status = "up"
                    error_message = None
                else:
                    status = "degraded"
                    error_message = f"HTTP {response.status}"
                
                return ServiceHealth(
                    name=service_name,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now(),
                    error_message=error_message,
                    uptime_percentage=self.calculate_uptime(service_name)
                )
        
        except Exception as e:
            return ServiceHealth(
                name=service_name,
                status="down",
                response_time=None,
                last_check=datetime.now(),
                error_message=str(e),
                uptime_percentage=self.calculate_uptime(service_name)
            )
    
    def calculate_uptime(self, service_name: str) -> float:
        """Calculate service uptime percentage"""
        # This is a simplified calculation
        # In a real implementation, you'd track historical data
        if service_name not in self.services_status:
            return 100.0
        
        current_status = self.services_status[service_name]
        if current_status.status == "up":
            return min(100.0, current_status.uptime_percentage + 0.1)
        else:
            return max(0.0, current_status.uptime_percentage - 1.0)
    
    def get_metric_status(self, value: float, metric_name: str) -> str:
        """Get metric status based on thresholds"""
        thresholds = self.thresholds.get(metric_name, {})
        
        if value >= thresholds.get("critical", 100):
            return "critical"
        elif value >= thresholds.get("warning", 80):
            return "warning"
        else:
            return "healthy"
    
    async def evaluate_alerts(self):
        """Evaluate conditions and generate alerts"""
        new_alerts = []
        
        # Check metrics for alerts
        recent_metrics = [m for m in self.metrics_history 
                         if m.timestamp > datetime.now() - timedelta(minutes=5)]
        
        for metric in recent_metrics:
            if metric.status in ["warning", "critical"]:
                alert = {
                    "type": "metric_alert",
                    "severity": metric.status,
                    "source": metric.name,
                    "message": f"{metric.name} is {metric.value}{metric.unit} ({metric.status})",
                    "timestamp": metric.timestamp,
                    "description": metric.description
                }
                new_alerts.append(alert)
        
        # Check services for alerts
        for service_name, service_health in self.services_status.items():
            if service_health.status in ["down", "degraded"]:
                alert = {
                    "type": "service_alert",
                    "severity": "critical" if service_health.status == "down" else "warning",
                    "source": service_name,
                    "message": f"Service {service_name} is {service_health.status}",
                    "timestamp": service_health.last_check,
                    "description": service_health.error_message
                }
                new_alerts.append(alert)
        
        # Add new alerts (avoid duplicates)
        for alert in new_alerts:
            if not self.is_duplicate_alert(alert):
                self.alerts.append(alert)
                await self.send_alert(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def is_duplicate_alert(self, new_alert: Dict[str, Any]) -> bool:
        """Check if alert is a duplicate of recent alert"""
        if not self.alerts:
            return False
        
        # Check last 10 alerts for duplicates
        recent_alerts = self.alerts[-10:]
        for alert in recent_alerts:
            if (alert["source"] == new_alert["source"] and 
                alert["type"] == new_alert["type"] and
                alert["message"] == new_alert["message"] and
                (new_alert["timestamp"] - alert["timestamp"]).seconds < 300):  # 5 minutes
                return True
        
        return False
    
    async def send_alert(self, alert: Dict[str, Any]):
        """Send alert notification"""
        logger.warning(f"🚨 ALERT: {alert['message']}")
        
        # Here you could add various notification methods:
        # - Email notifications
        # - Slack notifications
        # - Discord notifications
        # - SMS notifications
        # - etc.
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary"""
        # Calculate overall system status
        services_up = sum(1 for s in self.services_status.values() if s.status == "up")
        total_services = len(self.services_status)
        
        critical_metrics = sum(1 for m in self.metrics_history[-10:] if m.status == "critical")
        warning_metrics = sum(1 for m in self.metrics_history[-10:] if m.status == "warning")
        
        if services_up == total_services and critical_metrics == 0:
            overall_status = "healthy"
        elif critical_metrics > 0 or services_up < total_services * 0.8:
            overall_status = "critical"
        else:
            overall_status = "warning"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "services": {
                "up": services_up,
                "total": total_services,
                "percentage": (services_up / total_services * 100) if total_services > 0 else 0
            },
            "metrics": {
                "critical": critical_metrics,
                "warning": warning_metrics,
                "healthy": 10 - critical_metrics - warning_metrics
            },
            "active_alerts": len([a for a in self.alerts 
                                if a["timestamp"] > datetime.now() - timedelta(hours=1)]),
            "services_detail": {name: asdict(health) for name, health in self.services_status.items()},
            "recent_metrics": [asdict(m) for m in self.metrics_history[-20:]]
        }
    
    async def generate_health_report(self) -> str:
        """Generate detailed health report"""
        summary = self.get_health_summary()
        
        report = []
        report.append("# AgentDaf1.1 System Health Report")
        report.append(f"Generated: {summary['timestamp']}")
        report.append("")
        
        # Overall status
        status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}
        report.append(f"## Overall Status: {status_emoji[summary['overall_status']]} {summary['overall_status'].upper()}")
        report.append("")
        
        # Services status
        report.append("## 🏗️ Services Status")
        report.append(f"- Up: {summary['services']['up']}/{summary['services']['total']} ({summary['services']['percentage']:.1f}%)")
        report.append("")
        
        for name, health in summary['services_detail'].items():
            status_emoji = {"up": "🟢", "down": "🔴", "degraded": "🟡"}
            report.append(f"- {status_emoji[health['status']]} **{name}**: {health['status']}")
            if health.get('response_time'):
                report.append(f"  - Response time: {health['response_time']:.0f}ms")
            if health.get('error_message'):
                report.append(f"  - Error: {health['error_message']}")
        report.append("")
        
        # Recent metrics
        report.append("## 📊 Recent Metrics")
        for metric in summary['recent_metrics'][-10:]:
            status_emoji = {"healthy": "🟢", "warning": "🟡", "critical": "🔴"}
            report.append(f"- {status_emoji[metric['status']]} **{metric['name']}**: {metric['value']}{metric['unit']}")
        report.append("")
        
        # Active alerts
        active_alerts = [a for a in self.alerts 
                        if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)]
        
        if active_alerts:
            report.append("## 🚨 Active Alerts")
            for alert in active_alerts[-5:]:
                severity_emoji = {"warning": "🟡", "critical": "🔴"}
                report.append(f"- {severity_emoji[alert['severity']]} **{alert['source']}**: {alert['message']}")
            report.append("")
        else:
            report.append("## ✅ No Active Alerts")
            report.append("")
        
        return "/n".join(report)

async def main():
    """Main entry point"""
    logger.info("🏥 AgentDaf1.1 System Health Monitor")
    logger.info("=" * 50)
    
    monitor = SystemHealthMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("/n⏹️ Health monitor stopped")
    except Exception as e:
        logger.info(f"/n💥 Health monitor error: {e}")

if __name__ == "__main__":
    asyncio.run(main())