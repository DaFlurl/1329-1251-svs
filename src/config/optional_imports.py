"""
Centralized optional imports for AgentDaf1.1
"""

# WebSocket imports
try:
    import websockets
except ImportError:
    websockets = None

# Docker imports
try:
    import docker
    from docker.models.containers import Container
except ImportError:
    docker = None
    Container = None

# Export availability flags
WEBSOCKETS_AVAILABLE = websockets is not None
DOCKER_AVAILABLE = docker is not None