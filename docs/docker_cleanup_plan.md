# Docker Cleanup Plan for AgentDaf1.1

## Current Docker Environment Analysis

### Containers Related to AgentDaf1.1 (KEEP):
- `agentdaf1-excel-dashboard` - Main application container
- `agentdaf1-simple` - Simple test container
- `agentdaf1-test` - Test container
- `excel-dashboard-mcp` - MCP server for Excel dashboard
- `excel-dashboard-redis` - Redis for Excel dashboard

### Containers from Other Projects (REMOVE):
- All `agent30-*` containers (Agent30 project)
- All `n8n*` containers (n8n workflow automation)
- All `staging-*` containers (staging environments)
- All `*-production` containers (production environments)
- All monitoring stack containers not related to AgentDaf1.1
- `mcp-sequential-thinking` - MCP tool not related to this project

### Images Related to AgentDaf1.1 (KEEP):
- `agentdaf1-excel-dashboard:latest`
- `python:3.11-slim` (base image)
- `redis:alpine` and `redis:7-alpine` (required)

### Images to Remove:
- All `agent30-*` images
- All `staging-*` images  
- All `docker-*` images not related to AgentDaf1.1
- All `n8n*` images
- All monitoring images not used by AgentDaf1.1
- All MCP tool images not related to Excel processing

### Volumes Related to AgentDaf1.1 (KEEP):
- `agentdaf1_redis_data`
- `agentdaf11_*` volumes (monitoring for this project)

### Volumes to Remove:
- All `agent30_*` volumes
- All `docker_*` volumes not related to AgentDaf1.1
- All `staging_*` volumes
- All `n8n_*` volumes
- All `github-dashboard_*` volumes
- All random hash-named volumes

## Cleanup Commands

### Step 1: Stop and Remove Non-AgentDaf1.1 Containers
```bash
# Stop all containers except AgentDaf1.1 related ones
docker ps -a --filter "name=agent30" -q | xargs -r docker stop
docker ps -a --filter "name=n8n" -q | xargs -r docker stop  
docker ps -a --filter "name=staging" -q | xargs -r docker stop
docker ps -a --filter "name=production" -q | xargs -r docker stop
docker ps -a --filter "name=mcp-sequential-thinking" -q | xargs -r docker stop

# Remove the stopped containers
docker ps -a --filter "name=agent30" -q | xargs -r docker rm
docker ps -a --filter "name=n8n" -q | xargs -r docker rm
docker ps -a --filter "name=staging" -q | xargs -r docker rm  
docker ps -a --filter "name=production" -q | xargs -r docker rm
docker ps -a --filter "name=mcp-sequential-thinking" -q | xargs -r docker rm
```

### Step 2: Remove Unused Images
```bash
# Remove Agent30 project images
docker rmi agent30-web-manager agent30-web-manager-app agent30-mcp-server agent30-mcp-dockerhub-server agent30-api-marketplace agent30-collaboration-service agent30-analytics-dashboard agent30-ai-service

# Remove staging images
docker rmi staging-web-manager-staging staging-mcp-server-staging

# Remove docker project images (not AgentDaf1.1)
docker rmi docker-mcp-server docker-web-manager docker-collaboration-service docker-api-marketplace docker-ai-service docker-analytics-dashboard

# Remove n8n images
docker rmi n8nio/n8n:latest n8nio/n8n:1.50.1 docker.n8n.io/n8nio/n8n:latest

# Remove monitoring images (keep basic ones for AgentDaf1.1)
docker rmi prom/prometheus:latest grafana/grafana:latest grafana/loki:latest grafana/promtail:2.8.0 prom/alertmanager:latest

# Remove MCP tool images not related to Excel processing
docker rmi mcp/sequentialthinking mcp/playwright mcp/grafana mcp/postman mcp/dockerhub mcp/desktop-commander mcp/brave-search mcp/filesystem mcp/memory mcp/time mcp/api-gateway mcp/duckduckgo mcp/sqlite mcp/puppeteer

# Remove other project images
docker rmi github-dashboard-dashboard deployment-mcp-server mein-projekt-mcp-server n8n-mcp-server strucktur-n8n-mcp-server strucktur-tools
```

### Step 3: Remove Unused Volumes
```bash
# Remove Agent30 project volumes
docker volume rm agent30_alertmanager_data agent30_backups agent30_grafana_data agent30_loki_data agent30_n8n_1_data agent30_n8n_2_data agent30_n8n_agent_data agent30_n8n_data agent30_n8n_data_2 agent30_n8n_staging_data agent30_postgres_agent_data agent30_postgres_data agent30_postgres_staging_data agent30_prometheus_data agent30_redis_agent_data agent30_redis_data agent30_redis_staging_data agent30_web_logs agent30_web_manager_data agent30_web_manager_logs

# Remove docker project volumes
docker volume rm docker_analytics_data docker_backup_data docker_collaboration_data docker_grafana_data docker_loki_data docker_marketplace_data docker_marketplace_templates docker_n8n_data docker_postgres_data docker_prometheus_data docker_redis_data

# Remove staging volumes
docker volume rm staging_n8n_staging_data staging_postgres_staging_data staging_redis_staging_data

# Remove n8n volumes
docker volume rm n8n_data n8n_n8n_node_modules n8n_postgres_data n8n_redis_data

# Remove github-dashboard volumes
docker volume rm github-dashboard_grafana_data github-dashboard_postgres_data github-dashboard_prometheus_data github-dashboard_redis_data

# Remove other project volumes
docker volume rm docker-lsp docker-prompts mcp-sqlite portainer_portainer-docker-extension-desktop-extension_portainer_data postgres_data redis_data strucktur_postgres_data_fresh

# Remove random hash volumes (carefully - only if not used)
# List them first and verify they're not needed
```

### Step 4: Clean Up System
```bash
# Remove all dangling images
docker image prune -f

# Remove all unused containers, networks, images (both dangling and unreferenced)
docker system prune -a -f

# Remove all unused volumes
docker volume prune -f
```

## Expected Results After Cleanup

### Remaining Containers (AgentDaf1.1 only):
- `agentdaf1-excel-dashboard` - Main application
- `agentdaf1-simple` - Simple test
- `agentdaf1-test` - Test container  
- `excel-dashboard-mcp` - MCP server
- `excel-dashboard-redis` - Redis service

### Remaining Images:
- `agentdaf1-excel-dashboard:latest`
- `python:3.11-slim`
- `redis:alpine`, `redis:7-alpine`
- Basic system images (hello-world, alpine, etc.)

### Remaining Volumes:
- `agentdaf1_redis_data`
- `agentdaf11_*` volumes (monitoring for this project)
- Essential system volumes

### Space Savings:
- Expected to free up 10-15GB of disk space
- Reduce container count from ~50 to ~5
- Reduce image count from ~80 to ~10
- Reduce volume count from ~70 to ~10

## Safety Notes:
1. Always stop containers before removing them
2. Images cannot be removed if containers are using them
3. Volumes cannot be removed if containers are using them
4. Some volumes may contain important data - verify before deletion
5. Run `docker system df` before and after to see space savings