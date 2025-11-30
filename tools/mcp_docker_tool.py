#!/usr/bin/env python3
"""
MCP Docker Tool - Model Context Protocol Docker Integration
Manages Docker containers for MCP services and development environments
"""

import os
import sys
import json
import docker
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional

class MCPDockerTool:
    def __init__(self):
        self.client = None
        self.config_file = "mcp_docker_config.json"
        self.config = self.load_config()
        self.init_docker()
    
    def load_config(self):
        """Load MCP Docker configuration"""
        default_config = {
            "containers": {
                "mcp-server": {
                    "image": "python:3.11-slim",
                    "ports": {"8000/tcp": 8000},
                    "volumes": {
                        "/app": {
                            "bind": os.getcwd(),
                            "mode": "rw"
                        }
                    },
                    "environment": {
                        "PYTHONPATH": "/app",
                        "MCP_SERVER_PORT": "8000"
                    },
                    "command": "python -m mcp.server",
                    "auto_start": False
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": {"6379/tcp": 6379},
                    "auto_start": False
                },
                "postgres": {
                    "image": "postgres:15-alpine",
                    "ports": {"5432/tcp": 5432},
                    "environment": {
                        "POSTGRES_DB": "agentdaf1",
                        "POSTGRES_USER": "postgres",
                        "POSTGRES_PASSWORD": "password"
                    },
                    "volumes": {
                        "postgres_data": {
                            "bind": "/var/lib/postgresql/data",
                            "mode": "rw"
                        }
                    },
                    "auto_start": False
                }
            },
            "networks": {
                "mcp-network": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "postgres_data": {}
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save MCP Docker configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def init_docker(self):
        """Initialize Docker client"""
        try:
            self.client = docker.from_env()
            self.client.ping()
            print("✅ Docker client initialized")
            return True
        except Exception as e:
            print(f"❌ Docker initialization failed: {e}")
            print("Please ensure Docker is running and accessible")
            return False
    
    def create_networks(self):
        """Create Docker networks"""
        try:
            for network_name, network_config in self.config["networks"].items():
                try:
                    network = self.client.networks.create(
                        network_name,
                        driver=network_config.get("driver", "bridge")
                    )
                    print(f"✅ Created network: {network_name}")
                except docker.errors.APIError as e:
                    if "already exists" in str(e):
                        print(f"ℹ️ Network already exists: {network_name}")
                    else:
                        print(f"❌ Error creating network {network_name}: {e}")
        except Exception as e:
            print(f"❌ Error creating networks: {e}")
    
    def create_volumes(self):
        """Create Docker volumes"""
        try:
            for volume_name in self.config["volumes"]:
                try:
                    volume = self.client.volumes.create(volume_name)
                    print(f"✅ Created volume: {volume_name}")
                except docker.errors.APIError as e:
                    if "already exists" in str(e):
                        print(f"ℹ️ Volume already exists: {volume_name}")
                    else:
                        print(f"❌ Error creating volume {volume_name}: {e}")
        except Exception as e:
            print(f"❌ Error creating volumes: {e}")
    
    def start_container(self, container_name: str) -> bool:
        """Start a specific container"""
        if container_name not in self.config["containers"]:
            print(f"❌ Container '{container_name}' not found in configuration")
            return False
        
        container_config = self.config["containers"][container_name]
        
        try:
            # Check if container already exists
            existing_containers = self.client.containers.list(
                all=True, 
                filters={"name": container_name}
            )
            
            if existing_containers:
                container = existing_containers[0]
                if container.status == "running":
                    print(f"ℹ️ Container '{container_name}' is already running")
                    return True
                else:
                    container.start()
                    print(f"✅ Started existing container: {container_name}")
                    return True
            
            # Create new container
            ports = container_config.get("ports", {})
            volumes = container_config.get("volumes", {})
            environment = container_config.get("environment", {})
            command = container_config.get("command")
            
            # Convert volumes format
            volume_binds = {}
            for host_path, volume_config in volumes.items():
                if isinstance(volume_config, dict):
                    volume_binds[volume_config["bind"]] = {
                        "bind": volume_config["bind"],
                        "mode": volume_config.get("mode", "rw")
                    }
                else:
                    volume_binds[host_path] = {"bind": host_path, "mode": "rw"}
            
            container = self.client.containers.run(
                container_config["image"],
                name=container_name,
                ports=ports,
                volumes=volume_binds,
                environment=environment,
                command=command,
                detach=True,
                network="mcp-network" if "mcp-network" in self.config["networks"] else None
            )
            
            print(f"✅ Started container: {container_name}")
            print(f"   Container ID: {container.id[:12]}")
            
            # Wait a moment for container to be ready
            time.sleep(2)
            
            # Show container status
            self.show_container_status(container_name)
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting container '{container_name}': {e}")
            return False
    
    def stop_container(self, container_name: str) -> bool:
        """Stop a specific container"""
        try:
            containers = self.client.containers.list(
                all=True, 
                filters={"name": container_name}
            )
            
            if not containers:
                print(f"ℹ️ Container '{container_name}' not found")
                return False
            
            container = containers[0]
            
            if container.status != "running":
                print(f"ℹ️ Container '{container_name}' is not running")
                return True
            
            container.stop()
            print(f"✅ Stopped container: {container_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping container '{container_name}': {e}")
            return False
    
    def remove_container(self, container_name: str) -> bool:
        """Remove a specific container"""
        try:
            containers = self.client.containers.list(
                all=True, 
                filters={"name": container_name}
            )
            
            if not containers:
                print(f"ℹ️ Container '{container_name}' not found")
                return False
            
            container = containers[0]
            
            if container.status == "running":
                container.stop()
            
            container.remove()
            print(f"✅ Removed container: {container_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error removing container '{container_name}': {e}")
            return False
    
    def show_container_status(self, container_name: str = None):
        """Show status of containers"""
        try:
            containers = self.client.containers.list(all=True)
            
            if container_name:
                containers = [c for c in containers if container_name in c.name]
            
            if not containers:
                print("ℹ️ No containers found")
                return
            
            print("\n📊 Container Status:")
            print("-" * 80)
            print(f"{'Name':<20} {'Status':<15} {'Image':<25} {'Ports':<20}")
            print("-" * 80)
            
            for container in containers:
                name = container.name
                status = container.status
                image = container.image.tags[0] if container.image.tags else "unknown"
                ports = ", ".join([f"{p['HostPort']}->{p['PrivatePort']}" 
                                 for p in container.ports.values() 
                                 for p in container.ports.values() if p]) or "none"
                
                print(f"{name:<20} {status:<15} {image:<25} {ports:<20}")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ Error getting container status: {e}")
    
    def show_logs(self, container_name: str, lines: int = 50):
        """Show container logs"""
        try:
            containers = self.client.containers.list(
                all=True, 
                filters={"name": container_name}
            )
            
            if not containers:
                print(f"❌ Container '{container_name}' not found")
                return
            
            container = containers[0]
            logs = container.logs(tail=lines).decode('utf-8')
            
            print(f"\n📋 Logs for '{container_name}':")
            print("-" * 50)
            print(logs)
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error getting logs for '{container_name}': {e}")
    
    def exec_command(self, container_name: str, command: str):
        """Execute command in container"""
        try:
            containers = self.client.containers.list(
                filters={"name": container_name}
            )
            
            if not containers:
                print(f"❌ Container '{container_name}' not found or not running")
                return
            
            container = containers[0]
            
            # Execute command
            result = container.exec_run(command, stdout=True, stderr=True)
            
            print(f"\n🔧 Command executed in '{container_name}': {command}")
            print("-" * 50)
            if result.output:
                print(result.output.decode('utf-8'))
            if result.exit_code != 0:
                print(f"❌ Command failed with exit code: {result.exit_code}")
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error executing command in '{container_name}': {e}")
    
    def setup_mcp_environment(self):
        """Setup complete MCP development environment"""
        print("🚀 Setting up MCP Docker Environment...")
        print("=" * 50)
        
        # Create networks
        self.create_networks()
        
        # Create volumes
        self.create_volumes()
        
        # Start auto-start containers
        for container_name, config in self.config["containers"].items():
            if config.get("auto_start", False):
                print(f"\n🔄 Starting auto-start container: {container_name}")
                self.start_container(container_name)
        
        print("\n✅ MCP Docker environment setup complete!")
        print("\n📋 Available containers:")
        for name in self.config["containers"]:
            print(f"  - {name}")
        
        print("\n🔧 Usage:")
        print("  python mcp_docker_tool.py start <container>")
        print("  python mcp_docker_tool.py stop <container>")
        print("  python mcp_docker_tool.py status")
        print("  python mcp_docker_tool.py logs <container>")
    
    def cleanup(self):
        """Clean up all MCP containers and resources"""
        print("🧹 Cleaning up MCP Docker Environment...")
        
        # Stop and remove all containers
        for container_name in self.config["containers"]:
            self.stop_container(container_name)
            self.remove_container(container_name)
        
        # Remove networks
        try:
            for network_name in self.config["networks"]:
                networks = self.client.networks.list(filters={"name": network_name})
                for network in networks:
                    network.remove()
                    print(f"✅ Removed network: {network_name}")
        except Exception as e:
            print(f"❌ Error removing networks: {e}")
        
        print("✅ Cleanup complete!")

def main():
    if len(sys.argv) < 2:
        print("MCP Docker Tool - Model Context Protocol Docker Management")
        print("\nUsage:")
        print("  python mcp_docker_tool.py setup                    - Setup MCP environment")
        print("  python mcp_docker_tool.py start <container>         - Start container")
        print("  python mcp_docker_tool.py stop <container>          - Stop container")
        print("  python mcp_docker_tool.py remove <container>        - Remove container")
        print("  python mcp_docker_tool.py status [container]        - Show status")
        print("  python mcp_docker_tool.py logs <container> [lines]  - Show logs")
        print("  python mcp_docker_tool.py exec <container> <cmd>   - Execute command")
        print("  python mcp_docker_tool.py cleanup                  - Clean up everything")
        print("\nAvailable containers:")
        print("  - mcp-server")
        print("  - redis")
        print("  - postgres")
        return
    
    tool = MCPDockerTool()
    
    if not tool.client:
        print("❌ Docker client not available. Please check Docker installation.")
        return
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        tool.setup_mcp_environment()
    elif command == "start":
        if len(sys.argv) < 3:
            print("❌ Please specify container name")
            return
        tool.start_container(sys.argv[2])
    elif command == "stop":
        if len(sys.argv) < 3:
            print("❌ Please specify container name")
            return
        tool.stop_container(sys.argv[2])
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Please specify container name")
            return
        tool.remove_container(sys.argv[2])
    elif command == "status":
        container = sys.argv[2] if len(sys.argv) > 2 else None
        tool.show_container_status(container)
    elif command == "logs":
        if len(sys.argv) < 3:
            print("❌ Please specify container name")
            return
        lines = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        tool.show_logs(sys.argv[2], lines)
    elif command == "exec":
        if len(sys.argv) < 4:
            print("❌ Please specify container name and command")
            return
        tool.exec_command(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "cleanup":
        tool.cleanup()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()