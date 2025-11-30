#!/usr/bin/env python3
"""
AgentDaf1.1 System Health Check
Monitors all services and reports system health
"""

import requests
import sys
import time
from typing import Dict, List

def check_service(name: str, url: str) -> Dict[str, any]:
    """Check individual service health"""
    try:
        response = requests.get(url, timeout=5)
        return {
            'name': name,
            'url': url,
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'response_time': response.elapsed.total_seconds(),
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'name': name,
            'url': url,
            'status': 'down',
            'error': str(e)
        }

def main():
    services = [
        ('Basic App', 'http://localhost:8080/api/health'),
        ('Enterprise Gateway', 'http://localhost:8000/health'),
        ('Data Service', 'http://localhost:8001/health'),
        ('Analytics Service', 'http://localhost:8002/health'),
        ('WebSocket Service', 'http://localhost:8004/health'),
        ('Prometheus', 'http://localhost:9090/-/healthy'),
        ('Grafana', 'http://localhost:3001/api/health')
    ]
    
    logger.info("AgentDaf1.1 System Health Check")
    logger.info("=" * 50)
    
    all_healthy = True
    for name, url in services:
        result = check_service(name, url)
        status_icon = "[OK]" if result['status'] == 'healthy' else "[FAIL]"
        logger.info(f"{status_icon} {name}: {result['status']}")
        
        if result['status'] != 'healthy':
            all_healthy = False
            if 'error' in result:
                logger.info(f"   Error: {result['error']}")
    
    logger.info("=" * 50)
    if all_healthy:
        logger.info("All systems are healthy!")
        sys.exit(0)
    else:
        logger.info("Some systems need attention!")
        sys.exit(1)

if __name__ == "__main__":
    main()
