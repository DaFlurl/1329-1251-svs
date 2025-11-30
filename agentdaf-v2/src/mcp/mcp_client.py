#!/usr/bin/env python3
"""
MCP Client for AgentDaf1.1
Handles communication with MCP servers
"""

import json
import asyncio
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

class MCPClient:
    """Client for communicating with MCP servers"""
    
    def __init__(self):
        self.servers = {}
        self.logger = self._setup_logger()
        self.initialized = False
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for MCP client"""
        logger = logging.getLogger("MCPClient")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self) -> bool:
        """Initialize MCP client and discover servers"""
        try:
            self.logger.info("Initializing MCP Client...")
            
            # Discover available MCP servers
            await self._discover_servers()
            
            self.initialized = True
            self.logger.info("MCP Client initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP Client: {e}")
            return False
    
    async def _discover_servers(self):
        """Discover available MCP servers"""
        # Known MCP servers
        known_servers = {
            "sequential_thinking": {
                "url": "http://localhost:3010",
                "endpoints": {
                    "think": "/api/think",
                    "health": "/health"
                }
            },
            "code_interpreter": {
                "url": "http://localhost:3011",
                "endpoints": {
                    "analyze": "/api/analyze",
                    "execute": "/api/execute",
                    "health": "/health"
                }
            }
        }
        
        for name, config in known_servers.items():
            try:
                # Test server health
                response = requests.get(f"{config['url']}{config['endpoints']['health']}", timeout=5)
                if response.status_code == 200:
                    self.servers[name] = config
                    self.logger.info(f"Discovered MCP server: {name}")
                else:
                    self.logger.warning(f"MCP server {name} not healthy: {response.status_code}")
            except Exception as e:
                self.logger.warning(f"Failed to connect to MCP server {name}: {e}")
    
    async def sequential_thinking(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Execute sequential thinking on MCP server"""
        try:
            if "sequential_thinking" not in self.servers:
                return {"error": "Sequential thinking MCP server not available"}
            
            server = self.servers["sequential_thinking"]
            url = f"{server['url']}{server['endpoints']['think']}"
            
            payload = {
                "prompt": prompt,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Sequential thinking failed: {e}"}
    
    async def execute_command(self, server_name: str, command: str, args: Dict = None) -> Dict:
        """Execute command on MCP server"""
        try:
            if server_name not in self.servers:
                return {"error": f"MCP server {server_name} not available"}
            
            server = self.servers[server_name]
            
            # Determine endpoint based on command
            if command == "analyze":
                endpoint = server["endpoints"].get("analyze", "/api/analyze")
            elif command == "execute":
                endpoint = server["endpoints"].get("execute", "/api/execute")
            else:
                endpoint = f"/api/{command}"
            
            url = f"{server['url']}{endpoint}"
            
            payload = {
                "command": command,
                "args": args or {},
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            return {"error": f"Command execution failed: {e}"}
    
    async def get_server_status(self) -> Dict:
        """Get status of all MCP servers"""
        status = {}
        
        for name, config in self.servers.items():
            try:
                response = requests.get(f"{config['url']}{config['endpoints']['health']}", timeout=5)
                status[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "url": config['url']
                }
            except Exception as e:
                status[name] = {
                    "status": "error",
                    "error": str(e),
                    "url": config['url']
                }
        
        return status
    
    async def shutdown(self):
        """Shutdown MCP client"""
        try:
            self.logger.info("Shutting down MCP Client...")
            self.servers.clear()
            self.initialized = False
            self.logger.info("MCP Client shutdown complete")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")