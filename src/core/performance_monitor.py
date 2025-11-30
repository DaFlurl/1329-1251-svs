#!/usr/bin/env python3
"""
Performance Monitor Module - Monitors system performance, metrics, and provides alerting
"""

import psutil
import platform
import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from pathlib import Path

# Import centralized logging
from src.config.logging_config import get_logger

# Get logger
logger = get_logger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_usage: float
    network_io: Dict[str, Any]
    process_count: int
    uptime: float
    load_average: List[float]
    temperature: Optional[float] = None

@dataclass
class SystemAlert:
    """System alert data structure"""
    id: str
    level: AlertLevel
    message: str
    timestamp: str
    source: str
    acknowledged: bool = False
    resolved: bool = False

class PerformanceMonitor:
    """Main performance monitoring class"""
    
    def __init__(self, db_path: str = "data/agentdaf1.db", check_interval: int = 60):
        """Initialize the performance monitor"""
        self.db_path = db_path
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread = None
        self.callbacks: Dict[str, List[Callable]] = {
            'cpu_high': [],
            'memory_high': [],
            'disk_low': [],
            'process_count_high': [],
            'system_load_high': [],
            'temperature_high': []
        }
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage': 90.0,
            'process_count': 300,
            'load_average': 2.0,
            'temperature': 70.0
        }
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        disk_usage REAL NOT NULL,
                        network_io TEXT NOT NULL,
                        process_count INTEGER NOT NULL,
                        uptime REAL NOT NULL,
                        load_average TEXT NOT NULL,
                        temperature REAL
                    )
                ''')
                
                # Create alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        source TEXT NOT NULL,
                        acknowledged BOOLEAN DEFAULT FALSE,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS monitor_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT NOT NULL
                    )
                ''')
                
                # Insert default settings
                default_settings = [
                    ('check_interval', str(self.check_interval)),
                    ('cpu_threshold', str(self.thresholds['cpu_percent'])),
                    ('memory_threshold', str(self.thresholds['memory_percent'])),
                    ('disk_threshold', str(self.thresholds['disk_usage'])),
                    ('process_threshold', str(self.thresholds['process_count'])),
                    ('load_threshold', str(self.thresholds['load_average'])),
                    ('temperature_threshold', str(self.thresholds['temperature']))
                ]
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO monitor_settings (setting_key, setting_value)
                    VALUES (?, ?)
                ''', default_settings)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            import platform
            if platform.system() == 'Windows':
                disk = psutil.disk_usage('C:\\')
            else:
                disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_io = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout
            }
            
            # Process count
            process_count = len(psutil.pids())
            
            # System uptime
            uptime = time.time() - psutil.boot_time()
            
            # Load average
            load_avg = psutil.getloadavg()
            load_average = list(load_avg[:3])  # 1min, 5min, 15min
            
            # Temperature (if available)
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        temp = max(temp.current for temp_list in temps.values() for temp in temp_list)
                    else:
                        temp = None
                else:
                    temp = None
            except:
                temp = None
            
            timestamp = datetime.now().isoformat()
            
            return PerformanceMetrics(
                timestamp=timestamp,
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage=disk_usage,
                network_io=network_io,
                process_count=process_count,
                uptime=uptime,
                load_average=load_average,
                temperature=temp
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            raise
    
    def _check_thresholds(self, metrics: PerformanceMetrics) -> List[SystemAlert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        
        # Check CPU threshold
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alert = SystemAlert(
                id=f"cpu_high_{int(time.time())}",
                level=AlertLevel.WARNING,
                message=f"High CPU usage: {metrics.cpu_percent:.1f}%",
                timestamp=metrics.timestamp,
                source="cpu_monitor"
            )
            alerts.append(alert)
            self.callbacks['cpu_high'].append(alert)
        
        # Check memory threshold
        if metrics.memory_percent > self.thresholds['memory_percent']:
            alert = SystemAlert(
                id=f"memory_high_{int(time.time())}",
                level=AlertLevel.WARNING,
                message=f"High memory usage: {metrics.memory_percent:.1f}%",
                timestamp=metrics.timestamp,
                source="memory_monitor"
            )
            alerts.append(alert)
            self.callbacks['memory_high'].append(alert)
        
        # Check disk threshold
        if metrics.disk_usage > self.thresholds['disk_usage']:
            alert = SystemAlert(
                id=f"disk_low_{int(time.time())}",
                level=AlertLevel.ERROR,
                message=f"Low disk space: {metrics.disk_usage:.1f}% free",
                timestamp=metrics.timestamp,
                source="disk_monitor"
            )
            alerts.append(alert)
            self.callbacks['disk_low'].append(alert)
        
        # Check process count threshold
        if metrics.process_count > self.thresholds['process_count']:
            alert = SystemAlert(
                id=f"process_count_high_{int(time.time())}",
                level=AlertLevel.WARNING,
                message=f"High process count: {metrics.process_count}",
                timestamp=metrics.timestamp,
                source="process_monitor"
            )
            alerts.append(alert)
            self.callbacks['process_count_high'].append(alert)
        
        # Check load average threshold
        if metrics.load_average and len(metrics.load_average) >= 3:
            if metrics.load_average[0] > self.thresholds['load_average']:
                alert = SystemAlert(
                    id=f"system_load_high_{int(time.time())}",
                    level=AlertLevel.WARNING,
                    message=f"High system load: {metrics.load_average[0]:.2f}",
                    timestamp=metrics.timestamp,
                    source="load_monitor"
                )
                alerts.append(alert)
                self.callbacks['system_load_high'].append(alert)
        
        # Check temperature threshold
        if metrics.temperature and metrics.temperature > self.thresholds['temperature']:
            alert = SystemAlert(
                id=f"temperature_high_{int(time.time())}",
                level=AlertLevel.CRITICAL,
                message=f"High system temperature: {metrics.temperature:.1f}°C",
                timestamp=metrics.timestamp,
                source="temperature_monitor"
            )
            alerts.append(alert)
            self.callbacks['temperature_high'].append(alert)
        
        return alerts
    
    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_usage, network_io, process_count, uptime, load_average, temperature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp,
                    metrics.cpu_percent,
                    metrics.memory_percent,
                    metrics.disk_usage,
                    json.dumps(metrics.network_io),
                    metrics.process_count,
                    metrics.uptime,
                    json.dumps(metrics.load_average),
                    metrics.temperature
                ))
                conn.commit()
                logger.debug(f"Metrics stored: {metrics.timestamp}")
                
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _store_alerts(self, alerts: List[SystemAlert]):
        """Store alerts in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for alert in alerts:
                    cursor.execute('''
                        INSERT INTO system_alerts 
                        (alert_id, level, message, timestamp, source, acknowledged, resolved)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        alert.id,
                        alert.level.value,
                        alert.message,
                        alert.timestamp,
                        alert.source,
                        alert.acknowledged,
                        alert.resolved
                    ))
                conn.commit()
                logger.info(f"Stored {len(alerts)} alerts")
                
        except Exception as e:
            logger.error(f"Failed to store alerts: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting performance monitoring loop")
        
        while self.running:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                
                # Store metrics
                self._store_metrics(metrics)
                
                # Check thresholds and generate alerts
                alerts = self._check_thresholds(metrics)
                
                if alerts:
                    self._store_alerts(alerts)
                    
                    # Trigger callbacks
                    for alert in alerts:
                        callback_list = self.callbacks.get(alert.source.replace('_monitor', ''), [])
                        for callback in callback_list:
                            try:
                                callback(alert)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                # Log summary
                logger.info(f"CPU: {metrics.cpu_percent:.1f}%, "
                           f"Memory: {metrics.memory_percent:.1f}%, "
                           f"Disk: {metrics.disk_usage:.1f}%, "
                           f"Processes: {metrics.process_count}, "
                           f"Uptime: {metrics.uptime/3600:.1f}h")
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Brief pause before retry
    
    def start(self):
        """Start performance monitoring"""
        if self.running:
            logger.warning("Monitor is already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"Performance monitor started (interval: {self.check_interval}s)")
    
    def stop(self):
        """Stop performance monitoring"""
        if not self.running:
            logger.warning("Monitor is not running")
            return
        
        logger.info("Stopping performance monitor")
        self.running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        
        logger.info("Performance monitor stopped")
    
    def register_callback(self, alert_type: str, callback: Callable[[SystemAlert], None]):
        """Register callback for specific alert type"""
        if alert_type not in self.callbacks:
            self.callbacks[alert_type] = []
        self.callbacks[alert_type].append(callback)
        logger.info(f"Registered callback for {alert_type}")
    
    def unregister_callback(self, alert_type: str, callback: Callable[[SystemAlert], None]):
        """Unregister callback for specific alert type"""
        if alert_type in self.callbacks:
            try:
                self.callbacks[alert_type].remove(callback)
                logger.info(f"Unregistered callback for {alert_type}")
            except ValueError:
                pass
        else:
            logger.warning(f"No callbacks registered for {alert_type}")
    
    def get_recent_metrics(self, hours: int = 24) -> List[PerformanceMetrics]:
        """Get recent metrics from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                since_time = (datetime.now() - timedelta(hours=hours)).isoformat()
                cursor.execute('''
                    SELECT timestamp, cpu_percent, memory_percent, disk_usage, network_io, 
                           process_count, uptime, load_average, temperature
                    FROM performance_metrics 
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (since_time,))
                
                rows = cursor.fetchall()
                metrics = []
                for row in rows:
                    metrics.append(PerformanceMetrics(
                        timestamp=row[0],
                        cpu_percent=row[1],
                        memory_percent=row[2],
                        disk_usage=row[3],
                        network_io=json.loads(row[4]) if row[4] else {},
                        process_count=row[5],
                        uptime=row[6],
                        load_average=json.loads(row[7]) if row[7] else [],
                        temperature=row[8]
                    ))
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    def get_active_alerts(self) -> List[SystemAlert]:
        """Get active (unresolved) alerts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT alert_id, level, message, timestamp, source, acknowledged, resolved
                    FROM system_alerts 
                    WHERE resolved = FALSE
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''')
                
                rows = cursor.fetchall()
                alerts = []
                for row in rows:
                    level = AlertLevel(row[1])
                    alerts.append(SystemAlert(
                        id=row[0],
                        level=level,
                        message=row[2],
                        timestamp=row[3],
                        source=row[4],
                        acknowledged=bool(row[5]),
                        resolved=bool(row[6])
                    ))
                return alerts
                
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE system_alerts 
                    SET acknowledged = TRUE 
                    WHERE alert_id = ?
                ''', (alert_id,))
                conn.commit()
                logger.info(f"Alert {alert_id} acknowledged")
                return True
                
        except Exception as e:
            logger.error(f"Failed to acknowledge alert: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            info = {
                'timestamp': datetime.now().isoformat(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': psutil.disk_usage('/').total,
                'disk_free': psutil.disk_usage('/').free,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'platform': platform.system(),
                'python_version': platform.python_version(),
            }
            
            # Add network interfaces
            if hasattr(psutil, 'net_if_addrs'):
                net_if_addrs = psutil.net_if_addrs()
                info['network_interfaces'] = list(net_if_addrs.keys())
            else:
                info['network_interfaces'] = []
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            return {}
    
    def update_threshold(self, metric: str, value: float) -> bool:
        """Update monitoring threshold"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE monitor_settings 
                    SET setting_value = ? 
                    WHERE setting_key = ?
                ''', (str(value), f"{metric}_threshold"))
                conn.commit()
                
                # Update in-memory threshold
                self.thresholds[metric] = value
                logger.info(f"Updated {metric} threshold to {value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to update threshold: {e}")
            return False
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get current threshold settings"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT setting_key, setting_value 
                    FROM monitor_settings 
                    WHERE setting_key LIKE '%_threshold'
                ''')
                
                rows = cursor.fetchall()
                thresholds = {}
                for row in rows:
                    metric = row[0].replace('_threshold', '')
                    thresholds[metric] = float(row[1])
                
                return thresholds
                
        except Exception as e:
            logger.error(f"Failed to get thresholds: {e}")
            return {}
    
    # Flask API compatibility methods
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics for API response"""
        try:
            # Get current metrics
            metrics = self._collect_metrics()
            
            # Get recent alerts
            active_alerts = self.get_active_alerts()
            
            # Get system info
            system_info = self.get_system_info()
            
            return {
                'timestamp': metrics.timestamp,
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'disk_usage': metrics.disk_usage,
                'process_count': metrics.process_count,
                'uptime_hours': metrics.uptime / 3600,
                'load_average': metrics.load_average,
                'temperature': metrics.temperature,
                'network_io': metrics.network_io,
                'active_alerts': len(active_alerts),
                'alerts': [
                    {
                        'id': alert.id,
                        'level': alert.level.value,
                        'message': alert.message,
                        'timestamp': alert.timestamp,
                        'source': alert.source
                    }
                    for alert in active_alerts[:5]  # Limit to 5 most recent
                ],
                'system_info': system_info,
                'thresholds': self.thresholds
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Set up alert callbacks
def setup_alert_callbacks(monitor: PerformanceMonitor):
    """Setup default alert callbacks"""
    
    def cpu_high_callback(alert: SystemAlert):
        logger.info(f"🔥 CPU ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check processes: Task Manager or 'top' command")
    
    def memory_high_callback(alert: SystemAlert):
        logger.info(f"💾 MEMORY ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check memory usage: 'free -h' or Task Manager")
    
    def disk_low_callback(alert: SystemAlert):
        logger.info(f"💿 DISK ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check disk space: 'df -h' or clean up files")
    
    def process_count_high_callback(alert: SystemAlert):
        logger.info(f"⚡ PROCESS ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check running processes: 'ps aux' or Task Manager")
    
    def system_load_high_callback(alert: SystemAlert):
        logger.info(f"⚖️ LOAD ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check system load: 'uptime' or 'top'")
    
    def temperature_high_callback(alert: SystemAlert):
        logger.info(f"🌡️ TEMPERATURE ALERT: {alert.message}")
        logger.info(f"Timestamp: {alert.timestamp}")
        logger.info(f"Check system temperature: 'sensors' command")
        logger.info("Consider improving cooling")

# Register callbacks
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    # Setup alert callbacks
    setup_alert_callbacks(monitor)
    
    # Register callbacks
    monitor.register_callback('cpu', cpu_high_callback)
    monitor.register_callback('memory', memory_high_callback)
    monitor.register_callback('disk', disk_low_callback)
    monitor.register_callback('process', process_count_high_callback)
    monitor.register_callback('load', system_load_high_callback)
    monitor.register_callback('temperature', temperature_high_callback)
    
    logger.info("🖥️ AgentDaf1.1 Performance Monitor")
    logger.info("=" * 50)
    logger.info(f"Database: {monitor.db_path}")
    logger.info(f"Check Interval: {monitor.check_interval}s")
    logger.info(f"Thresholds: {monitor.thresholds}")
    logger.info()
    logger.info("📊 Real-time Performance Monitoring")
    logger.info("📊 System Metrics Collection")
    logger.info("📊 Threshold-based Alerting")
    logger.info("📊 Database Storage")
    logger.info("📊 Callback System")
    logger.info()
    logger.info("🔧 Configuration Management")
    logger.info()
    logger.info("Press Ctrl+C to stop monitoring")
    logger.info("=" * 50)
    
    try:
        monitor.start()
        
        # Keep main thread alive
        while monitor.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("/n/n⏹️ Stopping performance monitor...")
        monitor.stop()
        logger.info("✅ Performance monitor stopped safely")