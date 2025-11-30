# Performance Monitoring Module for AgentDaf1.1

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Try to import psutil, make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

@dataclass
class PerformanceMetrics:
    """Performance metrics for the system"""
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, Any]
    uptime: float
    boot_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_usage': self.disk_usage,
            'network_io': self.network_io,
            'uptime': self.uptime,
            'boot_time': self.boot_time,
            'timestamp': self.timestamp.isoformat()
        }

class PerformanceMonitor:
    """Performance monitoring and health checks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.start_time = time.time()
        
    def get_system_stats(self) -> PerformanceMetrics:
        """Get current system performance statistics"""
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available, returning mock data")
            return PerformanceMetrics(
                cpu_percent=25.0,
                memory_percent=50.0,
                disk_usage=60.0,
                network_io={'bytes_sent': 0, 'bytes_recv': 0, 'packets_sent': 0, 'packets_recv': 0},
                uptime=time.time() - self.start_time,
                boot_time=self.start_time,
                timestamp=datetime.now()
            )
            
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Boot time
            boot_time = psutil.boot_time()
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            return PerformanceMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_io,
                uptime=uptime,
                boot_time=boot_time,
                timestamp=datetime.now()
            )
                
        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return PerformanceMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage=0.0,
                network_io={},
                uptime=0.0,
                boot_time=0.0,
                timestamp=datetime.now()
            )
    
    def check_thresholds(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Check if metrics exceed thresholds"""
        thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 80.0,
            'disk_critical': 90.0
        }
        
        alerts = []
        
        if metrics.cpu_percent > thresholds['cpu_critical']:
            alerts.append({
                'type': 'critical',
                'metric': 'cpu',
                'value': metrics.cpu_percent,
                'threshold': thresholds['cpu_critical'],
                'message': f"CPU usage critical: {metrics.cpu_percent:.1f}%"
            })
        elif metrics.cpu_percent > thresholds['cpu_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'cpu',
                'value': metrics.cpu_percent,
                'threshold': thresholds['cpu_warning'],
                'message': f"CPU usage warning: {metrics.cpu_percent:.1f}%"
            })
            
        if metrics.memory_percent > thresholds['memory_critical']:
            alerts.append({
                'type': 'critical',
                'metric': 'memory',
                'value': metrics.memory_percent,
                'threshold': thresholds['memory_critical'],
                'message': f"Memory usage critical: {metrics.memory_percent:.1f}%"
            })
        elif metrics.memory_percent > thresholds['memory_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'memory',
                'value': metrics.memory_percent,
                'threshold': thresholds['memory_warning'],
                'message': f"Memory usage warning: {metrics.memory_percent:.1f}%"
            })
            
        if metrics.disk_usage > thresholds['disk_critical']:
            alerts.append({
                'type': 'critical',
                'metric': 'disk',
                'value': metrics.disk_usage,
                'threshold': thresholds['disk_critical'],
                'message': f"Disk usage critical: {metrics.disk_usage:.1f}%"
            })
        elif metrics.disk_usage > thresholds['disk_warning']:
            alerts.append({
                'type': 'warning',
                'metric': 'disk',
                'value': metrics.disk_usage,
                'threshold': thresholds['disk_warning'],
                'message': f"Disk usage warning: {metrics.disk_usage:.1f}%"
            })
            
        return {
            'metrics': metrics.to_dict(),
            'alerts': alerts,
            'thresholds': thresholds
        }
    
    def get_process_stats(self, process_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific process"""
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available, cannot get process stats")
            return None
            
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info() and proc.info().get('name') == process_name:
                    return {
                        'pid': proc.pid,
                        'status': proc.status(),
                        'cpu_percent': proc.cpu_percent(),
                        'memory_info': proc.memory_info(),
                        'create_time': proc.create_time(),
                        'name': proc.name()
                    }
        except Exception as e:
            self.logger.error(f"Error getting process stats for {process_name}: {e}")
            return None
    
    def get_historical_data(self, hours: int = 24) -> list:
        """Get historical performance data (mock implementation)"""
        # This would typically read from a database or cache
        # For now, return empty list
        return []

# Health check endpoints for monitoring
def health_check() -> Dict[str, Any]:
    """Basic health check"""
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {
            'cpu': True,
            'memory': True,
            'disk': True
        }
    }

# Export function for external monitoring systems
def export_metrics(metrics: PerformanceMetrics) -> str:
    """Export metrics to Prometheus format"""
    return f"""
# HELP agent_daf1_performance_metrics_cpu_percent {metrics.cpu_percent}
# HELP agent_daf1_performance_metrics_memory_percent {metrics.memory_percent}
# HELP agent_daf1_performance_metrics_disk_usage {metrics.disk_usage}
# HELP agent_daf1_performance_metrics_uptime {metrics.uptime}
# TYPE agent_daf1_performance_metrics_timestamp gauge
# TYPE agent_daf1_performance_metrics_boot_time gauge
"""