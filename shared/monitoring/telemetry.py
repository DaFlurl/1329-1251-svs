"""
OpenTelemetry Monitoring for AgentDaf1.1
Comprehensive observability with distributed tracing, metrics, and logging
"""

import os
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager, contextmanager
from functools import wraps
from datetime import datetime

from opentelemetry import trace, metrics, baggage, context
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
# from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.sampling import TraceIdRatioBasedSampler
from opentelemetry.sdk.trace.sampling import StaticSampler, Sampler, Decision
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
# from opentelemetry.semantic_conventions.resource import ResourceAttributes
# from opentelemetry.semantic_conventions.trace import SpanAttributes
# from opentelemetry.util.metrics import get_meter

logger = logging.getLogger(__name__)

class OpenTelemetryManager:
    """Central OpenTelemetry management"""
    
    def __init__(self, service_name: str = "agentdaf-service"):
        self.service_name = service_name
        self.tracer_provider: Optional[TracerProvider] = None
        self.meter_provider: Optional[MeterProvider] = None
        self.tracer = None
        self.meter = None
        self.metrics: Dict[str, Any] = {}
        self.is_initialized = False
    
    def initialize(self):
        """Initialize OpenTelemetry"""
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": os.getenv("ENVIRONMENT", "development"),
                "host.name": os.getenv("HOSTNAME", "localhost"),
            })
            
            # Initialize tracing
            self._setup_tracing(resource)
            
            # Initialize metrics
            self._setup_metrics(resource)
            
            # Initialize auto-instrumentation
            self._setup_auto_instrumentation()
            
            self.is_initialized = True
            logger.info(f"OpenTelemetry initialized for {self.service_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
    
    def _setup_tracing(self, resource: Resource):
        """Setup distributed tracing"""
        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
            agent_port=int(os.getenv("JAEGER_PORT", "6831")),
        )
        
        # Configure OTLP exporter as backup
        # otlp_exporter = OTLPSpanExporter(
        #     endpoint=os.getenv("OTLP_ENDPOINT", "http://localhost:4317"),
        #     insecure=True
        # )
        
        # Create tracer provider with sampling
        self.tracer_provider = TracerProvider(
            resource=resource
            # sampler=TraceIdRatioBasedSampler(0.1)  # Sample 10% of traces
        )
        
        # Register exporters
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        self.tracer_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        # self.tracer_provider.add_span_processor(
        #     BatchSpanProcessor(otlp_exporter)
        # )
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)
    
    def _setup_metrics(self, resource: Resource):
        """Setup metrics collection"""
        # Configure Prometheus exporter
        prometheus_reader = PrometheusMetricReader(
            endpoint=os.getenv("PROMETHEUS_ENDPOINT", "0.0.0.0:9464")
        )
        
        # Configure OTLP exporter
        # otlp_metric_exporter = OTLPMetricExporter(
        #     endpoint=os.getenv("OTLP_METRICS_ENDPOINT", "http://localhost:4317"),
        #     insecure=True
        # )
        
        # Create periodic exporter
        # periodic_reader = PeriodicExportingMetricReader(
        #     otlp_metric_exporter,
        #     export_interval_millis=30000  # Export every 30 seconds
        # )
        
        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader]  # , periodic_reader
        )
        
        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        
        # Get meter
        self.meter = self.meter_provider.get_meter(self.service_name)
        
        # Create common metrics
        self._create_common_metrics()
    
    def _create_common_metrics(self):
        """Create common application metrics"""
        # Counter for HTTP requests
        self.metrics["http_requests_total"] = self.meter.create_counter(
            "http_requests_total",
            description="Total number of HTTP requests"
        )
        
        # Histogram for request duration
        self.metrics["http_request_duration"] = self.meter.create_histogram(
            "http_request_duration_seconds",
            description="HTTP request duration in seconds"
        )
        
        # Counter for active users
        self.metrics["active_users"] = self.meter.create_up_down_counter(
            "active_users",
            description="Number of active users"
        )
        
        # Gauge for system metrics
        self.metrics["cpu_usage"] = self.meter.create_observable_gauge(
            "cpu_usage_percent",
            description="CPU usage percentage",
            callbacks=[self._get_cpu_usage]
        )
        
        self.metrics["memory_usage"] = self.meter.create_observable_gauge(
            "memory_usage_bytes",
            description="Memory usage in bytes",
            callbacks=[self._get_memory_usage]
        )
        
        # Business metrics
        self.metrics["files_processed"] = self.meter.create_counter(
            "files_processed_total",
            description="Total number of files processed"
        )
        
        self.metrics["dashboards_generated"] = self.meter.create_counter(
            "dashboards_generated_total",
            description="Total number of dashboards generated"
        )
        
        self.metrics["processing_errors"] = self.meter.create_counter(
            "processing_errors_total",
            description="Total number of processing errors"
        )
    
    def _get_cpu_usage(self, options):
        """Callback for CPU usage metric"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            yield (cpu_percent,)
        except ImportError:
            yield (0.0,)
        except Exception as e:
            logger.error(f"Error getting CPU usage: {e}")
            yield (0.0,)
    
    def _get_memory_usage(self, options):
        """Callback for memory usage metric"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            yield (memory.used,)
        except ImportError:
            yield (0.0,)
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            yield (0.0,)
    
    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation"""
        try:
            # Instrument FastAPI
            FastAPIInstrumentor.instrument()
            
            # Instrument HTTP clients
            # HTTPXClientInstrumentor.instrument()
            
            # Instrument databases
            SQLAlchemyInstrumentor.instrument()
            RedisInstrumentor.instrument()
            # AsyncPGInstrumentor.instrument()
            
            logger.info("Auto-instrumentation setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up auto-instrumentation: {e}")
    
    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float
    ):
        """Record HTTP request metrics"""
        if not self.is_initialized:
            return
        
        # Record request count
        self.metrics["http_requests_total"].add(
            1,
            {
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code)
            }
        )
        
        # Record request duration
        self.metrics["http_request_duration"].record(
            duration,
            {
                "method": method,
                "endpoint": endpoint
            }
        )
    
    def record_file_processed(self, file_type: str, success: bool = True):
        """Record file processing metrics"""
        if not self.is_initialized:
            return
        
        if success:
            self.metrics["files_processed"].add(
                1,
                {"file_type": file_type}
            )
        else:
            self.metrics["processing_errors"].add(
                1,
                {"file_type": file_type, "error_type": "processing"}
            )
    
    def record_dashboard_generated(self, dashboard_type: str):
        """Record dashboard generation metrics"""
        if not self.is_initialized:
            return
        
        self.metrics["dashboards_generated"].add(
            1,
            {"dashboard_type": dashboard_type}
        )
    
    def update_active_users(self, count: int):
        """Update active users count"""
        if not self.is_initialized:
            return
        
        self.metrics["active_users"].add(count)
    
    @contextmanager
    def trace_span(self, name: str, **attributes):
        """Create a trace span"""
        if not self.is_initialized:
            yield
            return
        
        with self.tracer.start_as_current_span(name) as span:
            # Set attributes
            for key, value in attributes.items():
                span.set_attribute(key, value)
            
            # Add baggage if provided
            for key, value in baggage.get_all().items():
                span.set_attribute(f"baggage.{key}", value)
            
            yield span
    
    @asynccontextmanager
    async def trace_async_span(self, name: str, **attributes):
        """Create an async trace span"""
        if not self.is_initialized:
            yield
            return
        
        with self.tracer.start_as_current_span(name) as span:
            # Set attributes
            for key, value in attributes.items():
                span.set_attribute(key, value)
            
            yield span
    
    def add_span_event(self, name: str, **attributes):
        """Add event to current span"""
        if not self.is_initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.add_event(name, attributes)
    
    def set_span_attribute(self, key: str, value: Any):
        """Set attribute on current span"""
        if not self.is_initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute(key, value)
    
    def record_exception(self, exception: Exception):
        """Record exception on current span"""
        if not self.is_initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span:
            current_span.record_exception(exception)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))

# Global telemetry manager
telemetry = OpenTelemetryManager()

# Decorators for automatic tracing
def traced(operation_name: str = None):
    """Decorator to trace function execution"""
    def decorator(func):
        name = operation_name or f"{func.__module__}.{func.__name__}"
        
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                async with telemetry.trace_async_span(name):
                    try:
                        result = await func(*args, **kwargs)
                        return result
                    except Exception as e:
                        telemetry.record_exception(e)
                        raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with telemetry.trace_span(name):
                    try:
                        result = func(*args, **kwargs)
                        return result
                    except Exception as e:
                        telemetry.record_exception(e)
                        raise
            return sync_wrapper
    
    return decorator

def trace_method(operation_name: str = None):
    """Decorator to trace class methods"""
    def decorator(method):
        name = operation_name or f"{method.__self__.__class__.__name__}.{method.__name__}"
        
        if asyncio.iscoroutinefunction(method):
            @wraps(method)
            async def async_wrapper(self, *args, **kwargs):
                async with telemetry.trace_async_span(
                    name,
                    class_name=self.__class__.__name__,
                    method_name=method.__name__
                ):
                    try:
                        result = await method(self, *args, **kwargs)
                        return result
                    except Exception as e:
                        telemetry.record_exception(e)
                        raise
            return async_wrapper
        else:
            @wraps(method)
            def sync_wrapper(self, *args, **kwargs):
                with telemetry.trace_span(
                    name,
                    class_name=self.__class__.__name__,
                    method_name=method.__name__
                ):
                    try:
                        result = method(self, *args, **kwargs)
                        return result
                    except Exception as e:
                        telemetry.record_exception(e)
                        raise
            return sync_wrapper
    
    return decorator

# Middleware for FastAPI
class TelemetryMiddleware:
    """FastAPI middleware for telemetry"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Start timing
        start_time = time.time()
        
        # Get request info
        method = scope["method"]
        path = scope["path"]
        
        # Create span for the request
        with telemetry.trace_span(
            "http_request",
            http_method=method,
            http_url=path,
            http_scheme=scope.get("scheme", "http"),
            http_host=scope.get("server", ["localhost"])[0],
            http_user_agent=scope.get("headers", {}).get("user-agent", ""),
        ) as span:
            try:
                # Process request
                await self.app(scope, receive, send)
                
                # Calculate duration
                duration = time.time() - start_time
                
                # Record metrics (status code would be available from response)
                telemetry.record_http_request(
                    method=method,
                    endpoint=path,
                    status_code=200,  # This would come from actual response
                    duration=duration
                )
                
                # Add span attributes
                span.set_attribute("http.method", method)
                span.set_attribute("http.url", path)
                span.set_attribute("http.status_code", 200)
                
            except Exception as e:
                duration = time.time() - start_time
                
                # Record error metrics
                telemetry.record_http_request(
                    method=method,
                    endpoint=path,
                    status_code=500,
                    duration=duration
                )
                
                # Record exception
                telemetry.record_exception(e)
                
                span.set_attribute("http.method", method)
                span.set_attribute("http.url", path)
                span.set_attribute("http.status_code", 500)
                
                raise

# Utility functions
def initialize_telemetry(service_name: str):
    """Initialize telemetry for a service"""
    global telemetry
    telemetry = OpenTelemetryManager(service_name)
    telemetry.initialize()
    return telemetry

def get_telemetry() -> OpenTelemetryManager:
    """Get the global telemetry manager"""
    return telemetry

def add_baggage(key: str, value: str):
    """Add baggage to current context"""
    baggage.set_baggage(key, value)

def get_baggage(key: str) -> Optional[str]:
    """Get baggage value from current context"""
    return baggage.get_baggage(key).value if baggage.get_baggage(key) else None