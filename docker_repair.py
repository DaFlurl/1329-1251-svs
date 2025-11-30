#!/usr/bin/env python3
"""
Docker Repair Script for AgentDaf1.1
Fixes Docker configuration and deployment issues
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class DockerRepair:
    """Docker configuration repair utility"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_docker_setup(self):
        """Analyze current Docker configuration"""
        logger.info("Analyzing Docker setup...")
        
        # Check for Docker files
        docker_files = [
            "docker-compose.yml",
            "Dockerfile", 
            "docker-compose.simple.yml",
            "docker-compose.fixed.yml"
        ]
        
        for docker_file in docker_files:
            if (self.project_root / docker_file).exists():
                logger.info(f"Found: {docker_file}")
            else:
                logger.info(f"Missing: {docker_file}")
                self.issues_found.append(f"Missing {docker_file}")
        
        # Check for required directories
        required_dirs = ["uploads", "logs", "data", "gitsitestylewebseite"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                logger.info(f"Missing directory: {dir_name}")
                self.issues_found.append(f"Missing directory: {dir_name}")
                # Create directory
                dir_path.mkdir(exist_ok=True)
                logger.info(f"Created directory: {dir_name}")
                self.fixes_applied.append(f"Created {dir_name} directory")
    
    def fix_docker_compose(self):
        """Fix docker-compose configuration"""
        logger.info("/nFixing docker-compose configuration...")
        
        # Create simplified docker-compose
        simple_compose = """version: '3.8'

services:
  # Simple Working Application
  agentdaf1-app:
    build: 
      context: .
      dockerfile: Dockerfile.fixed
    container_name: agentdaf1-simple
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - DEBUG=false
      - DATABASE_URL=sqlite:///data/agentdaf1.db
      - PYTHONPATH=/app
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
      - ./data:/app/data
      - ./gitsitestylewebseite:/app/web
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - agentdaf-network

  # Static Website Server
  web-server:
    image: nginx:alpine
    container_name: agentdaf1-web-server
    ports:
      - "80:80"
    volumes:
      - ./gitsitestylewebseite:/usr/share/nginx/html:ro
      - ./nginx-simple.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - agentdaf1-app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - agentdaf-network

volumes:
  agentdaf_data:
    driver: local

networks:
  agentdaf-network:
    driver: bridge
"""
        
        compose_file = self.project_root / "docker-compose.working.yml"
        with open(compose_file, 'w') as f:
            f.write(simple_compose)
        
        logger.info(f"Created working docker-compose: {compose_file}")
        self.fixes_applied.append("Created docker-compose.working.yml")
    
    def fix_requirements(self):
        """Fix requirements.txt for Docker"""
        logger.info("/nFixing requirements.txt...")
        
        # Check if requirements.txt exists
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            # Create minimal requirements
            minimal_req = """flask==2.3.3
flask-cors==4.0.0
pandas==2.1.3
openpyxl==3.1.2
requests==2.31.0
gunicorn==21.2.0
python-dotenv==1.0.0
"""
            with open(req_file, 'w') as f:
                f.write(minimal_req)
            
            logger.info("Created minimal requirements.txt")
            self.fixes_applied.append("Created requirements.txt")
        else:
            logger.info("requirements.txt exists")
    
    def create_nginx_config(self):
        """Create simple nginx configuration"""
        logger.info("/nCreating nginx configuration...")
        
        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream app {
        server agentdaf1-app:8080;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
        
        nginx_file = self.project_root / "nginx-simple.conf"
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)
        
        logger.info("Created nginx-simple.conf")
        self.fixes_applied.append("Created nginx-simple.conf")
    
    def test_docker_build(self):
        """Test Docker build"""
        logger.info("/nTesting Docker build...")
        
        try:
            # Check if Docker is running
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"Docker available: {result.stdout.strip()}")
                
                # Test build
                logger.info("Building Docker image...")
                build_result = subprocess.run(
                    ["docker", "build", "-f", "Dockerfile.fixed", "-t", "agentdaf1-fixed", "."],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes
                )
                
                if build_result.returncode == 0:
                    logger.info("Docker build successful")
                    self.fixes_applied.append("Docker build successful")
                    return True
                else:
                    logger.info(f"Docker build failed: {build_result.stderr}")
                    self.issues_found.append(f"Docker build failed: {build_result.stderr}")
                    return False
            else:
                logger.info("Docker not available")
                self.issues_found.append("Docker not installed or not running")
                return False
                
        except subprocess.TimeoutExpired:
            logger.info("Docker build timed out")
            self.issues_found.append("Docker build timed out")
            return False
        except Exception as e:
            print(f"Docker test failed: {e}")
            self.issues_found.append(f"Docker test failed: {e}")
            return False
    
    def create_deployment_script(self):
        """Create deployment script"""
        logger.info("/nCreating deployment script...")
        
        deploy_script = """#!/bin/bash
# AgentDaf1.1 Docker Deployment Script

echo "Starting AgentDaf1.1 Docker deployment..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.working.yml down --remove-orphans

# Build and start services
echo "Building and starting services..."
docker-compose -f docker-compose.working.yml up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check service status
echo "Checking service status..."
docker-compose -f docker-compose.working.yml ps

# Show logs
echo "Showing recent logs..."
docker-compose -f docker-compose.working.yml logs --tail=50

echo "Deployment complete!"
echo "Application available at: http://localhost"
echo "API available at: http://localhost/api/"
echo "Health check: http://localhost/health"
"""
        
        script_file = self.project_root / "deploy-docker.sh"
        with open(script_file, 'w') as f:
            f.write(deploy_script)
        
        # Make executable
        os.chmod(script_file, 0o755)
        
        logger.info("Created deploy-docker.sh")
        self.fixes_applied.append("Created deploy-docker.sh")
    
    def generate_report(self):
        """Generate repair report"""
        logger.info("/n" + "="*60)
        logger.info("DOCKER REPAIR REPORT")
        logger.info("="*60)
        
        logger.info(f"/nIssues Found: {len(self.issues_found)}")
        for issue in self.issues_found:
            logger.info(f"  [ISSUE] {issue}")
        
        logger.info(f"/nFixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            logger.info(f"  [FIXED] {fix}")
        
        if not self.issues_found:
            logger.info("/nAll issues resolved!")
        else:
            logger.info(f"/n{len(self.issues_found)} issues remaining")
        
        # Save report
        report = {
            "timestamp": str(Path.ctime(Path.now())),
            "issues_found": self.issues_found,
            "fixes_applied": self.fixes_applied,
            "status": "success" if not self.issues_found else "partial"
        }
        
        report_file = self.project_root / "docker_repair_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"/nReport saved to: {report_file}")
    
    def run_repair(self):
        """Run complete Docker repair process"""
        logger.info("Starting Docker repair process...")
        
        # Step 1: Analyze setup
        self.analyze_docker_setup()
        
        # Step 2: Fix configurations
        self.fix_docker_compose()
        self.fix_requirements()
        self.create_nginx_config()
        
        # Step 3: Test build (if Docker available)
        self.test_docker_build()
        
        # Step 4: Create deployment script
        self.create_deployment_script()
        
        # Step 5: Generate report
        self.generate_report()
        
        logger.info("/nNext steps:")
        logger.info("1. Run: ./deploy-docker.sh")
        logger.info("2. Access: http://localhost")
        logger.info("3. Check: http://localhost/health")

def main():
    """Main function"""
    repair = DockerRepair()
    repair.run_repair()

if __name__ == "__main__":
    main()