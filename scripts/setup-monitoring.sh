#!/bin/bash

# AgentDaf1 Monitoring and Logging Setup Script
# Configures comprehensive monitoring and logging for all containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="agentdaf1"
LOG_DIR="./logs"
MONITORING_DIR="./infrastructure/monitoring"
LOG_FILE="./logs/monitoring-setup.log"

# Create necessary directories
mkdir -p $LOG_DIR
mkdir -p $MONITORING_DIR/prometheus
mkdir -p $MONITORING_DIR/grafana/dashboards
mkdir -p $MONITORING_DIR/grafana/datasources
mkdir -p $MONITORING_DIR/elasticsearch
mkdir -p $MONITORING_DIR/kibana

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a $LOG_FILE
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a $LOG_FILE
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a $LOG_FILE
}

# Setup Prometheus configuration
setup_prometheus() {
    log "Setting up Prometheus configuration..."
    
    cat > $MONITORING_DIR/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'agentdaf1-app'
    static_configs:
      - targets: ['agentdaf1-app:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'data-service'
    static_configs:
      - targets: ['data-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'analytics-service'
    static_configs:
      - targets: ['analytics-service:8002']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'websocket-service'
    static_configs:
      - targets: ['websocket-service:8004']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
    scrape_interval: 30s
EOF

    # Create Prometheus rules
    mkdir -p $MONITORING_DIR/prometheus/rules
    
    cat > $MONITORING_DIR/prometheus/rules/alerts.yml << 'EOF'
groups:
  - name: agentdaf1_alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "Service {{ $labels.job }} has been down for more than 1 minute."

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 5 minutes."

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is above 90% for more than 5 minutes."

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has more than 80 active connections."

      - alert: RedisMemoryHigh
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Redis memory usage"
          description: "Redis memory usage is above 90%."
EOF

    log "Prometheus configuration created"
}

# Setup Grafana configuration
setup_grafana() {
    log "Setting up Grafana configuration..."
    
    # Grafana datasources
    cat > $MONITORING_DIR/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: "logstash-*"
    editable: true
EOF

    # Grafana dashboard for AgentDaf1
    cat > $MONITORING_DIR/grafana/dashboards/agentdaf1-dashboard.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "AgentDaf1 System Overview",
    "tags": ["agentdaf1"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Service Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{ job }}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "mappings": [
              {
                "options": {
                  "0": {
                    "text": "DOWN",
                    "color": "red"
                  },
                  "1": {
                    "text": "UP",
                    "color": "green"
                  }
                },
                "type": "value"
              }
            ]
          }
        },
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 0
        }
      },
      {
        "id": 2,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{ instance }}"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 0
        }
      },
      {
        "id": 3,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{ instance }}"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 0,
          "y": 8
        }
      },
      {
        "id": 4,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{ method }} {{ status }}"
          }
        ],
        "gridPos": {
          "h": 8,
          "w": 12,
          "x": 12,
          "y": 8
        }
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

    log "Grafana configuration created"
}

# Setup Elasticsearch configuration
setup_elasticsearch() {
    log "Setting up Elasticsearch configuration..."
    
    cat > $MONITORING_DIR/elasticsearch/elasticsearch.yml << 'EOF'
cluster.name: "agentdaf1-logs"
node.name: "agentdaf1-es-node"
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: false
xpack.monitoring.collection.enabled: true
EOF

    # Logstash configuration
    cat > $MONITORING_DIR/elasticsearch/logstash.conf << 'EOF'
input {
  beats {
    port => 5044
  }
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  if [fields][service] {
    mutate {
      add_field => { "service_name" => "%{[fields][service]}" }
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "agentdaf1-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
EOF

    log "Elasticsearch configuration created"
}

# Setup Kibana configuration
setup_kibana() {
    log "Setting up Kibana configuration..."
    
    cat > $MONITORING_DIR/kibana/kibana.yml << 'EOF'
server.name: "agentdaf1-kibana"
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://elasticsearch:9200"]
monitoring.ui.container.elasticsearch.enabled: true
EOF

    log "Kibana configuration created"
}

# Setup Filebeat configuration
setup_filebeat() {
    log "Setting up Filebeat configuration..."
    
    cat > $MONITORING_DIR/filebeat.yml << 'EOF'
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/agentdaf1/*.log
  fields:
    service: agentdaf1-app
  fields_under_root: true

- type: docker
  containers.ids:
    - "*"
  processors:
    - add_docker_metadata:
        host: "unix:///var/run/docker.sock"

output.logstash:
  hosts: ["logstash:5044"]

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
EOF

    log "Filebeat configuration created"
}

# Setup monitoring docker-compose override
setup_monitoring_compose() {
    log "Setting up monitoring docker-compose override..."
    
    cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  # Node Exporter
  node-exporter:
    image: prom/node-exporter:latest
    container_name: agentdaf1-node-exporter
    ports:
      - "9100:9100"
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    restart: unless-stopped
    networks:
      - agentdaf-network

  # PostgreSQL Exporter
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: agentdaf1-postgres-exporter
    ports:
      - "9187:9187"
    environment:
      DATA_SOURCE_NAME: "postgresql://agentdaf1:${DB_PASSWORD:-password}@postgres:5432/agentdaf1?sslmode=disable"
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - agentdaf-network

  # Redis Exporter
  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: agentdaf1-redis-exporter
    ports:
      - "9121:9121"
    environment:
      REDIS_ADDR: "redis://redis:6379"
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - agentdaf-network

  # Nginx Exporter
  nginx-exporter:
    image: nginx/nginx-prometheus-exporter:latest
    container_name: agentdaf1-nginx-exporter
    ports:
      - "9113:9113"
    command:
      - -nginx.scrape-uri=http://nginx:80/nginx_status
    depends_on:
      - nginx
    restart: unless-stopped
    networks:
      - agentdaf-network

  # Alertmanager
  alertmanager:
    image: prom/alertmanager:latest
    container_name: agentdaf1-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./infrastructure/monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    restart: unless-stopped
    networks:
      - agentdaf-network

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: agentdaf1-logstash
    ports:
      - "5044:5044"
      - "5000:5000"
    volumes:
      - ./infrastructure/monitoring/elasticsearch/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    environment:
      LS_JAVA_OPTS: "-Xmx512m -Xms512m"
    depends_on:
      - elasticsearch
    restart: unless-stopped
    networks:
      - agentdaf-network

  # Filebeat
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: agentdaf1-filebeat
    user: root
    volumes:
      - ./infrastructure/monitoring/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/log/agentdaf1:/var/log/agentdaf1:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - output.elasticsearch.hosts=["elasticsearch:9200"]
    depends_on:
      - logstash
    restart: unless-stopped
    networks:
      - agentdaf-network

networks:
  agentdaf-network:
    external: true
EOF

    # Create Alertmanager configuration
    cat > $MONITORING_DIR/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@agentdaf1.local'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
EOF

    log "Monitoring docker-compose configuration created"
}

# Setup log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    cat > /etc/logrotate.d/agentdaf1 << 'EOF'
/var/log/agentdaf1/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker kill -s USR1 agentdaf1-filebeat 2>/dev/null || true
    endscript
}
EOF

    log "Log rotation configured"
}

# Create monitoring startup script
create_monitoring_script() {
    log "Creating monitoring startup script..."
    
    cat > scripts/start-monitoring.sh << 'EOF'
#!/bin/bash

# AgentDaf1 Monitoring Startup Script

set -e

GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log "Starting monitoring services..."

# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d

log "Waiting for services to be ready..."
sleep 30

log "Monitoring services started!"
echo ""
echo "Access URLs:"
echo "  Prometheus:  http://localhost:9090"
echo "  Grafana:     http://localhost:3001 (admin/admin)"
echo "  Alertmanager: http://localhost:9093"
echo "  Elasticsearch: http://localhost:9200"
echo "  Kibana:      http://localhost:5601"
echo ""
echo "Grafana dashboards will be automatically imported."
EOF

    chmod +x scripts/start-monitoring.sh
    log "Monitoring startup script created"
}

# Main setup function
main() {
    log "Starting AgentDaf1 monitoring and logging setup..."
    
    setup_prometheus
    setup_grafana
    setup_elasticsearch
    setup_kibana
    setup_filebeat
    setup_monitoring_compose
    setup_log_rotation
    create_monitoring_script
    
    log "Monitoring and logging setup completed successfully!"
    echo ""
    echo "To start the monitoring stack, run:"
    echo "  ./scripts/start-monitoring.sh"
    echo ""
    echo "To start with the main application:"
    echo "  docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d"
}

# Run main function
main "$@"