# -*- coding: utf-8 -*-
"""
Docker Desktop MCP Server Integration Tools
Advanced Docker container management and monitoring tools
"""

import json
import subprocess
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import threading
import requests

@dataclass
class ContainerInfo:
    """Container information structure"""
    id: str
    name: str
    image: str
    status: str
    ports: List[str]
    created: datetime
    labels: Dict[str, str]
    stats: Optional[Dict[str, Any]] = None

@dataclass
class ImageInfo:
    """Docker image information structure"""
    id: str
    repository: str
    tag: str
    size: int
    created: datetime
    labels: Dict[str, str]

@dataclass
class VolumeInfo:
    """Docker volume information structure"""
    name: str
    driver: str
    mountpoint: str
    created: datetime
    size: Optional[int] = None

class DockerDesktopMCPServer:
    """Docker Desktop MCP Server integration for advanced container management"""
    
    def __init__(self, docker_host: str = "unix:///var/run/docker.sock"):
        self.docker_host = docker_host
        self.containers_cache = {}
        self.images_cache = {}
        self.volumes_cache = {}
        self.monitoring_active = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        
    def _run_docker_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        """Execute Docker command and return parsed result"""
        try:
            result = subprocess.run(
                ['docker'] + command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'returncode': result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_containers(self, all_containers: bool = False) -> List[ContainerInfo]:
        """List Docker containers with detailed information"""
        command = ['ps', '--format', 'json']
        if all_containers:
            command.append('-a')
        
        result = self._run_docker_command(command)
        
        if not result['success']:
            self.logger.error(f"Failed to list containers: {result['error']}")
            return []
        
        containers = []
        for line in result['stdout'].strip().split('/n'):
            if line:
                try:
                    data = json.loads(line)
                    
                    # Parse creation time
                    created = datetime.fromisoformat(data.get('CreatedAt', '').replace('Z', '+00:00'))
                    
                    # Parse ports
                    ports = []
                    if data.get('Ports'):
                        port_mappings = data['Ports'].split(',')
                        for port_map in port_mappings:
                            ports.append(port_map.strip())
                    
                    # Parse labels
                    labels = {}
                    if data.get('Labels'):
                        try:
                            labels = json.loads(data['Labels'])
                        except:
                            # Handle non-JSON labels
                            for label in data['Labels'].split(','):
                                if '=' in label:
                                    key, value = label.split('=', 1)
                                    labels[key.strip()] = value.strip()
                    
                    container = ContainerInfo(
                        id=data.get('ID', ''),
                        name=data.get('Names', ''),
                        image=data.get('Image', ''),
                        status=data.get('Status', ''),
                        ports=ports,
                        created=created,
                        labels=labels
                    )
                    
                    containers.append(container)
                    self.containers_cache[container.id] = container
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse container JSON: {e}")
                    continue
        
        return containers
    
    def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get real-time container statistics"""
        result = self._run_docker_command(['stats', container_id, '--no-stream', '--format', 'json'])
        
        if not result['success']:
            self.logger.error(f"Failed to get container stats: {result['error']}")
            return None
        
        try:
            stats = json.loads(result['stdout'])
            return {
                'cpu_percent': float(stats.get('CPUPerc', '0%').replace('%', '')),
                'memory_usage': stats.get('MemUsage', '0B / 0B'),
                'memory_percent': float(stats.get('MemPerc', '0%').replace('%', '')),
                'net_io': stats.get('NetIO', '0B / 0B'),
                'block_io': stats.get('BlockIO', '0B / 0B'),
                'pids': stats.get('PIDs', '0')
            }
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse container stats: {e}")
            return None
    
    def list_images(self) -> List[ImageInfo]:
        """List Docker images with detailed information"""
        result = self._run_docker_command(['images', '--format', 'json'])
        
        if not result['success']:
            self.logger.error(f"Failed to list images: {result['error']}")
            return []
        
        images = []
        for line in result['stdout'].strip().split('/n'):
            if line:
                try:
                    data = json.loads(line)
                    
                    # Parse creation time
                    created = datetime.fromisoformat(data.get('CreatedAt', '').replace('Z', '+00:00'))
                    
                    # Parse size
                    size_str = data.get('Size', '0B')
                    size = self._parse_size(size_str)
                    
                    # Parse labels
                    labels = {}
                    if data.get('Labels'):
                        try:
                            labels = json.loads(data['Labels'])
                        except:
                            for label in data['Labels'].split(','):
                                if '=' in label:
                                    key, value = label.split('=', 1)
                                    labels[key.strip()] = value.strip()
                    
                    image = ImageInfo(
                        id=data.get('ID', ''),
                        repository=data.get('Repository', ''),
                        tag=data.get('Tag', ''),
                        size=size,
                        created=created,
                        labels=labels
                    )
                    
                    images.append(image)
                    self.images_cache[image.id] = image
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse image JSON: {e}")
                    continue
        
        return images
    
    def list_volumes(self) -> List[VolumeInfo]:
        """List Docker volumes with detailed information"""
        result = self._run_docker_command(['volume', 'ls', '--format', 'json'])
        
        if not result['success']:
            self.logger.error(f"Failed to list volumes: {result['error']}")
            return []
        
        volumes = []
        for line in result['stdout'].strip().split('/n'):
            if line:
                try:
                    data = json.loads(line)
                    
                    # Parse creation time
                    created = datetime.fromisoformat(data.get('CreatedAt', '').replace('Z', '+00:00'))
                    
                    volume = VolumeInfo(
                        name=data.get('Name', ''),
                        driver=data.get('Driver', ''),
                        mountpoint=data.get('Mountpoint', ''),
                        created=created
                    )
                    
                    volumes.append(volume)
                    self.volumes_cache[volume.name] = volume
                    
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse volume JSON: {e}")
                    continue
        
        return volumes
    
    def _parse_size(self, size_str: str) -> int:
        """Parse Docker size string to bytes"""
        size_str = size_str.strip().upper()
        if size_str.endswith('B'):
            size_str = size_str[:-1]
        
        multipliers = {
            'K': 1024,
            'M': 1024 ** 2,
            'G': 1024 ** 3,
            'T': 1024 ** 4
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                number = float(size_str[:-1])
                return int(number * multiplier)
        
        return int(float(size_str))
    
    def create_container(self, image: str, name: str = None, 
                       ports: Dict[str, str] = None, 
                       environment: Dict[str, str] = None,
                       volumes: Dict[str, str] = None,
                       command: str = None) -> Dict[str, Any]:
        """Create a new Docker container"""
        docker_cmd = ['run', '-d']
        
        if name:
            docker_cmd.extend(['--name', name])
        
        # Add port mappings
        if ports:
            for host_port, container_port in ports.items():
                docker_cmd.extend(['-p', f'{host_port}:{container_port}'])
        
        # Add environment variables
        if environment:
            for key, value in environment.items():
                docker_cmd.extend(['-e', f'{key}={value}'])
        
        # Add volume mappings
        if volumes:
            for host_path, container_path in volumes.items():
                docker_cmd.extend(['-v', f'{host_path}:{container_path}'])
        
        docker_cmd.append(image)
        
        if command:
            docker_cmd.extend(command.split())
        
        result = self._run_docker_command(docker_cmd)
        
        if result['success']:
            container_id = result['stdout'].strip()
            return {
                'success': True,
                'container_id': container_id,
                'message': f'Container created successfully with ID: {container_id}'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def start_container(self, container_id: str) -> Dict[str, Any]:
        """Start a Docker container"""
        result = self._run_docker_command(['start', container_id])
        
        if result['success']:
            return {
                'success': True,
                'message': f'Container {container_id} started successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def stop_container(self, container_id: str, timeout: int = 10) -> Dict[str, Any]:
        """Stop a Docker container"""
        result = self._run_docker_command(['stop', '-t', str(timeout), container_id])
        
        if result['success']:
            return {
                'success': True,
                'message': f'Container {container_id} stopped successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def remove_container(self, container_id: str, force: bool = False) -> Dict[str, Any]:
        """Remove a Docker container"""
        docker_cmd = ['rm']
        if force:
            docker_cmd.append('-f')
        docker_cmd.append(container_id)
        
        result = self._run_docker_command(docker_cmd)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Container {container_id} removed successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def pull_image(self, image: str) -> Dict[str, Any]:
        """Pull a Docker image from registry"""
        result = self._run_docker_command(['pull', image], timeout=300)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Image {image} pulled successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def remove_image(self, image_id: str, force: bool = False) -> Dict[str, Any]:
        """Remove a Docker image"""
        docker_cmd = ['rmi']
        if force:
            docker_cmd.append('-f')
        docker_cmd.append(image_id)
        
        result = self._run_docker_command(docker_cmd)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Image {image_id} removed successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def create_volume(self, name: str, driver: str = 'local') -> Dict[str, Any]:
        """Create a Docker volume"""
        result = self._run_docker_command(['volume', 'create', '--driver', driver, name])
        
        if result['success']:
            return {
                'success': True,
                'message': f'Volume {name} created successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def remove_volume(self, volume_name: str, force: bool = False) -> Dict[str, Any]:
        """Remove a Docker volume"""
        docker_cmd = ['volume', 'rm']
        if force:
            docker_cmd.append('-f')
        docker_cmd.append(volume_name)
        
        result = self._run_docker_command(docker_cmd)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Volume {volume_name} removed successfully'
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def get_container_logs(self, container_id: str, lines: int = 100, 
                         follow: bool = False) -> Dict[str, Any]:
        """Get container logs"""
        docker_cmd = ['logs']
        if lines:
            docker_cmd.extend(['--tail', str(lines)])
        if follow:
            docker_cmd.append('--follow')
        docker_cmd.append(container_id)
        
        result = self._run_docker_command(docker_cmd, timeout=10 if not follow else None)
        
        if result['success']:
            return {
                'success': True,
                'logs': result['stdout'],
                'error': result['stderr']
            }
        else:
            return {
                'success': False,
                'error': result['error']
            }
    
    def start_monitoring(self, interval: int = 5):
        """Start continuous monitoring of containers"""
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    containers = self.list_containers(all_containers=True)
                    
                    for container in containers:
                        if container.status.startswith('Up'):
                            stats = self.get_container_stats(container.id)
                            if stats:
                                container.stats = stats
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    self.logger.error(f"Monitoring error: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Container monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        self.logger.info("Container monitoring stopped")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get Docker system information"""
        result = self._run_docker_command(['info', '--format', 'json'])
        
        if not result['success']:
            return {'error': result['error']}
        
        try:
            info = json.loads(result['stdout'])
            return {
                'version': info.get('ServerVersion', ''),
                'containers': info.get('Containers', 0),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'images': info.get('Images', 0),
                'memory_total': info.get('MemTotal', 0),
                'cpu_count': info.get('NCPU', 0),
                'architecture': info.get('Architecture', ''),
                'os_type': info.get('OSType', ''),
                'kernel_version': info.get('KernelVersion', '')
            }
        except json.JSONDecodeError as e:
            return {'error': f"Failed to parse system info: {e}"}
    
    def cleanup_resources(self, prune_containers: bool = False, 
                        prune_images: bool = False, 
                        prune_volumes: bool = False,
                        prune_networks: bool = False) -> Dict[str, Any]:
        """Clean up unused Docker resources"""
        results = {}
        
        if prune_containers:
            result = self._run_docker_command(['container', 'prune', '-f'])
            results['containers'] = {
                'success': result['success'],
                'message': 'Container cleanup completed' if result['success'] else result['error']
            }
        
        if prune_images:
            result = self._run_docker_command(['image', 'prune', '-f'])
            results['images'] = {
                'success': result['success'],
                'message': 'Image cleanup completed' if result['success'] else result['error']
            }
        
        if prune_volumes:
            result = self._run_docker_command(['volume', 'prune', '-f'])
            results['volumes'] = {
                'success': result['success'],
                'message': 'Volume cleanup completed' if result['success'] else result['error']
            }
        
        if prune_networks:
            result = self._run_docker_command(['network', 'prune', '-f'])
            results['networks'] = {
                'success': result['success'],
                'message': 'Network cleanup completed' if result['success'] else result['error']
            }
        
        return results

class DockerMCPTools:
    """High-level interface for Docker MCP tools"""
    
    def __init__(self):
        self.mcp_server = DockerDesktopMCPServer()
        
    def quick_deploy(self, image: str, name: str = None, 
                   port_mapping: str = None) -> Dict[str, Any]:
        """Quick deployment of a container"""
        if not name:
            name = f"app_{int(time.time())}"
        
        ports = {}
        if port_mapping:
            if ':' in port_mapping:
                host_port, container_port = port_mapping.split(':')
                ports[host_port] = container_port
            else:
                ports[port_mapping] = port_mapping
        
        return self.mcp_server.create_container(
            image=image,
            name=name,
            ports=ports
        )
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        containers = self.mcp_server.list_containers(all_containers=True)
        images = self.mcp_server.list_images()
        volumes = self.mcp_server.list_volumes()
        system_info = self.mcp_server.get_system_info()
        
        # Calculate statistics
        running_containers = [c for c in containers if c.status.startswith('Up')]
        stopped_containers = [c for c in containers if not c.status.startswith('Up')]
        
        total_image_size = sum(img.size for img in images)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'containers': {
                'total': len(containers),
                'running': len(running_containers),
                'stopped': len(stopped_containers),
                'details': [
                    {
                        'id': c.id[:12],
                        'name': c.name,
                        'image': c.image,
                        'status': c.status,
                        'ports': c.ports,
                        'created': c.created.isoformat()
                    }
                    for c in containers
                ]
            },
            'images': {
                'total': len(images),
                'total_size': total_image_size,
                'details': [
                    {
                        'id': img.id[:12],
                        'repository': img.repository,
                        'tag': img.tag,
                        'size': img.size,
                        'created': img.created.isoformat()
                    }
                    for img in images
                ]
            },
            'volumes': {
                'total': len(volumes),
                'details': [
                    {
                        'name': v.name,
                        'driver': v.driver,
                        'mountpoint': v.mountpoint,
                        'created': v.created.isoformat()
                    }
                    for v in volumes
                ]
            },
            'system': system_info
        }
    
    def export_configuration(self, filepath: str):
        """Export Docker configuration to JSON file"""
        dashboard_data = self.get_dashboard_data()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        
        return f"Configuration exported to {filepath}"

if __name__ == "__main__":
    # Example usage
    docker_tools = DockerMCPTools()
    
    # Get dashboard data
    dashboard = docker_tools.get_dashboard_data()
    logger.info(f"Docker Dashboard: {dashboard['containers']['total']} containers, {dashboard['images']['total']} images")
    
    # Export configuration
    docker_tools.export_configuration("docker_config.json")
    logger.info("Docker configuration exported")
    
    # Quick deploy example
    # result = docker_tools.quick_deploy("nginx:latest", "test_nginx", "8080:80")
    # logger.info(f"Deploy result: {result}")