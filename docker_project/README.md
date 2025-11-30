# Docker Performance Monitor

An advanced Docker container performance monitoring system with real-time metrics, alerts, and web dashboard.

## Features

- **Real-time Monitoring**: CPU, memory, disk, network, and container metrics
- **Interactive Dashboard**: Web-based interface with live charts and statistics
- **Alert System**: Configurable thresholds with notifications
- **Data Management**: Automated backup, export, and cleanup utilities
- **Container Integration**: Seamless Docker deployment with compose orchestration

## Quick Start

1. **Build and Start**:
   ```bash
   docker-compose up --build
   ```

2. **Access Dashboard**:
   Open http://localhost:8080 in your browser

3. **View Metrics**:
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin123)

## Project Structure

```
docker_project/
├── src/                    # Python source code
│   ├── main.py                 # Application entry point
│   ├── performance_monitor.py   # Core monitoring functionality
│   ├── config/
│   │   └── settings.py        # Configuration management
│   └── file_manager.py         # File utilities
├── scripts/                 # Shell scripts
│   └── start.sh               # Container startup script
├── docker_files/             # Docker configuration files
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── configs/
│       ├── prometheus.yml
│       ├── grafana/
│       │   ├── provisioning/
│       │   │   └── datasources/
│       │   │       └── prometheus.yml
│       │   └── dashboards/
│       │       └── docker-performance.json
│       └── grafana.ini
│       └── docker_rules.yml
├── data/                    # Application data storage
├── logs/                    # Log files
├── backups/                  # Backup storage
└── configs/                  # Runtime configuration
```

## Configuration

The system uses environment variables and configuration files for flexible deployment:

- **CPU Threshold**: Default 80%, configurable via settings
- **Memory Threshold**: Default 80%, configurable via settings  
- **Disk Threshold**: Default 90%, configurable via settings
- **Update Interval**: Default 5 seconds, configurable via settings

## API Endpoints

- **Metrics**: `GET /metrics` - Prometheus-compatible metrics
- **Health**: `GET /health` - Health check endpoint
- **Dashboard**: `GET /` - Web interface

## Technologies Used

- **Python 3.12**: Core application with psutil for system monitoring
- **Flask**: Lightweight web framework for API and dashboard
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Data visualization and dashboard
- **Docker Compose**: Service orchestration

## Security Features

- Non-root user execution
- Read-only file system access where possible
- No hardcoded credentials
- Input validation and sanitization

## Performance Optimizations

- Efficient metric collection with psutil
- Configurable collection intervals
- Memory-efficient data structures
- Minimal dependency footprint
- Optimized Docker layer size