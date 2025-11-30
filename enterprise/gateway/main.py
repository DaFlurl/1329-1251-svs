"""
Enterprise API Gateway
Central entry point for all microservices with routing, authentication, and rate limiting
"""

import asyncio
import logging
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import redis
from prometheus_client import Counter, Histogram, generate_latest
import time
import jwt
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('gateway_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gateway_request_duration_seconds', 'Request duration')

class APIGateway:
    """Enterprise API Gateway with advanced features"""
    
    def __init__(self):
        self.app = FastAPI(
            title="AgentDaf1.1 API Gateway",
            description="Enterprise Gateway for Gaming Dashboard Microservices",
            version="3.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Service registry
        self.services = {
            "data": {"url": "http://data-service:8001", "health": "/health"},
            "analytics": {"url": "http://analytics-service:8002", "health": "/health"},
            "auth": {"url": "http://auth-service:8003", "health": "/health"},
            "websocket": {"url": "http://websocket-service:8004", "health": "/health"},
            "notifications": {"url": "http://notifications-service:8005", "health": "/health"},
            "files": {"url": "http://files-service:8006", "health": "/health"}
        }
        
        # Redis for caching and rate limiting
        self.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        
        # JWT Secret
        self.jwt_secret = "your-super-secret-jwt-key-change-in-production"
        
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """Setup enterprise middleware"""
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure properly for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Gzip compression
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom middleware for metrics and logging
        @self.app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            REQUEST_DURATION.observe(process_time)
            
            return response
    
    def setup_routes(self):
        """Setup gateway routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Gateway health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.0.0",
                "services": await self.check_services_health()
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            return Response(generate_latest(), media_type="text/plain")
        
        # Service routes
        @self.app.api_route("/api/data/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_data_service(request: Request, path: str):
            return await self.proxy_request("data", path, request)
        
        @self.app.api_route("/api/analytics/{path:path}", methods=["GET", "POST"])
        async def proxy_analytics_service(request: Request, path: str):
            return await self.proxy_request("analytics", path, request)
        
        @self.app.api_route("/api/auth/{path:path}", methods=["GET", "POST"])
        async def proxy_auth_service(request: Request, path: str):
            return await self.proxy_request("auth", path, request)
        
        @self.app.api_route("/api/files/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def proxy_files_service(request: Request, path: str):
            return await self.proxy_request("files", path, request, require_auth=True)
        
        # WebSocket upgrade
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await self.proxy_websocket(websocket)
    
    async def proxy_request(self, service_name: str, path: str, request: Request, require_auth: bool = False):
        """Proxy request to microservice"""
        
        # Rate limiting
        client_ip = request.client.host
        if not await self.check_rate_limit(client_ip):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Authentication check
        if require_auth:
            await self.verify_token(request)
        
        service = self.services.get(service_name)
        if not service:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        url = f"{service['url']}/{path}"
        
        # Prepare request data
        headers = dict(request.headers)
        headers.pop("host", None)  # Remove host header
        
        content = await request.body()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    headers=headers,
                    content=content,
                    timeout=30.0
                )
                
                return Response(
                    content=response.content,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
                
        except httpx.RequestError as e:
            logger.error(f"Error proxying to {service_name}: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")
    
    async def proxy_websocket(self, websocket):
        """Proxy WebSocket connection to WebSocket service"""
        # Implementation for WebSocket proxying
        pass
    
    async def check_rate_limit(self, client_ip: str, limit: int = 100, window: int = 60) -> bool:
        """Check rate limit using Redis"""
        key = f"rate_limit:{client_ip}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        self.redis_client.incr(key)
        return True
    
    async def verify_token(self, request: Request):
        """Verify JWT token"""
        authorization = request.headers.get("authorization")
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")
        
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid authorization scheme")
            
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def check_services_health(self) -> Dict[str, str]:
        """Check health of all microservices"""
        health_status = {}
        
        for service_name, service_config in self.services.items():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{service_config['url']}{service_config['health']}",
                        timeout=5.0
                    )
                    health_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
            except Exception:
                health_status[service_name] = "unreachable"
        
        return health_status

# Initialize gateway
gateway = APIGateway()
app = gateway.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)