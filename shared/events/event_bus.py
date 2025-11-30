"""
Event Bus for AgentDaf1.1
Central event management with RabbitMQ integration
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import aio_pika
from aio_pika import ExchangeType, Message, DeliveryMode
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """Event types for the system"""
    FILE_UPLOADED = "file.uploaded"
    FILE_PROCESSED = "file.processed"
    FILE_PROCESSING_FAILED = "file.processing_failed"
    DASHBOARD_GENERATED = "dashboard.generated"
    USER_REGISTERED = "user.registered"
    USER_LOGIN = "user.login"
    ANALYTICS_COMPLETED = "analytics.completed"
    NOTIFICATION_SENT = "notification.sent"
    SYSTEM_ERROR = "system.error"
    PERFORMANCE_ALERT = "performance.alert"

@dataclass
class EventMetadata:
    """Event metadata"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source_service: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    version: str = "1.0"

class BaseEvent(BaseModel):
    """Base event model"""
    metadata: EventMetadata
    data: Dict[str, Any] = Field(default_factory=dict)

class EventBus:
    """Central event bus for microservices communication"""
    
    def __init__(self, connection_url: str = "amqp://localhost:5672"):
        self.connection_url = connection_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchanges: Dict[str, aio_pika.Exchange] = {}
        self.queues: Dict[str, aio_pika.Queue] = {}
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.is_connected = False
    
    async def connect(self) -> bool:
        """Connect to RabbitMQ"""
        try:
            self.connection = await aio_pika.connect_robust(
                self.connection_url,
                heartbeat=60,
                client_properties={
                    "connection_name": "AgentDaf1.1 EventBus"
                }
            )
            
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            
            # Declare main exchange
            self.exchanges["main"] = await self.channel.declare_exchange(
                "agentdaf_events",
                ExchangeType.TOPIC,
                durable=True
            )
            
            # Declare service-specific exchanges
            service_exchanges = [
                "file_service", "analytics_service", 
                "notification_service", "auth_service"
            ]
            
            for service in service_exchanges:
                self.exchanges[service] = await self.channel.declare_exchange(
                    f"{service}_events",
                    ExchangeType.TOPIC,
                    durable=True
                )
            
            self.is_connected = True
            logger.info("Connected to RabbitMQ event bus")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from RabbitMQ"""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("Disconnected from RabbitMQ")
    
    async def publish_event(
        self, 
        event_type: EventType, 
        data: Dict[str, Any],
        source_service: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        routing_key: Optional[str] = None
    ) -> bool:
        """Publish an event to the event bus"""
        if not self.is_connected:
            logger.error("Not connected to event bus")
            return False
        
        try:
            metadata = EventMetadata(
                event_id=f"{event_type.value}_{datetime.now().timestamp()}",
                event_type=event_type,
                timestamp=datetime.now(),
                source_service=source_service,
                correlation_id=correlation_id,
                user_id=user_id
            )
            
            event = BaseEvent(
                metadata=metadata,
                data=data
            )
            
            # Serialize event
            event_json = json.dumps(event.dict(), default=str)
            message = Message(
                event_json.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json",
                headers={
                    "event_type": event_type.value,
                    "source_service": source_service,
                    "correlation_id": correlation_id,
                    "user_id": user_id
                }
            )
            
            # Determine routing key
            if not routing_key:
                routing_key = f"{source_service}.{event_type.value}"
            
            # Publish to main exchange
            await self.exchanges["main"].publish(
                message,
                routing_key=routing_key
            )
            
            # Also publish to service-specific exchange
            await self.exchanges[source_service].publish(
                message,
                routing_key=event_type.value
            )
            
            logger.info(f"Published event {event_type.value} with routing key {routing_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to publish event {event_type.value}: {e}")
            return False
    
    async def subscribe_to_events(
        self, 
        event_types: List[EventType],
        handler: Callable,
        service_name: str,
        queue_name: Optional[str] = None
    ) -> bool:
        """Subscribe to specific event types"""
        if not self.is_connected:
            logger.error("Not connected to event bus")
            return False
        
        try:
            # Create queue for this service
            if not queue_name:
                queue_name = f"{service_name}_events"
            
            queue = await self.channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": 3600000,  # 1 hour TTL
                    "x-max-length": 10000  # Max 10k messages
                }
            )
            
            self.queues[queue_name] = queue
            
            # Bind queue to main exchange for each event type
            for event_type in event_types:
                routing_key = f"*.{event_type.value}"
                await queue.bind(self.exchanges["main"], routing_key)
                
                # Also bind to service-specific exchanges
                for service_exchange in self.exchanges.values():
                    if service_exchange != self.exchanges["main"]:
                        await queue.bind(service_exchange, event_type.value)
            
            # Store handler
            for event_type in event_types:
                if event_type not in self.handlers:
                    self.handlers[event_type] = []
                self.handlers[event_type].append(handler)
            
            # Start consuming messages
            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        event_data = json.loads(message.body.decode())
                        event = BaseEvent(**event_data)
                        
                        # Find and call appropriate handlers
                        event_type = EventType(event.metadata.event_type)
                        if event_type in self.handlers:
                            for handler in self.handlers[event_type]:
                                await handler(event)
                        
                        logger.info(f"Processed event {event_type.value}")
                        
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
            
            await queue.consume(message_handler)
            logger.info(f"Subscribed to events: {[et.value for et in event_types]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to events: {e}")
            return False
    
    async def create_dead_letter_queue(self, queue_name: str) -> bool:
        """Create dead letter queue for failed messages"""
        try:
            dlq_name = f"{queue_name}_dlq"
            
            # Declare dead letter exchange
            dlx = await self.channel.declare_exchange(
                f"{queue_name}_dlx",
                ExchangeType.DIRECT,
                durable=True
            )
            
            # Declare dead letter queue
            dlq = await self.channel.declare_queue(
                dlq_name,
                durable=True
            )
            
            # Bind dead letter queue
            await dlq.bind(dlx, routing_key=dlq_name)
            
            logger.info(f"Created dead letter queue: {dlq_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create dead letter queue: {e}")
            return False

# Global event bus instance
event_bus = EventBus()

# Event handlers for different services
class FileServiceEventHandler:
    """Event handlers for file service"""
    
    @staticmethod
    async def handle_file_uploaded(event: BaseEvent):
        """Handle file uploaded event"""
        logger.info(f"Processing uploaded file: {event.data}")
        
        # Start file processing
        await event_bus.publish_event(
            EventType.FILE_PROCESSED,
            {
                "file_id": event.data.get("file_id"),
                "status": "processing",
                "started_at": datetime.now().isoformat()
            },
            "file_service",
            correlation_id=event.metadata.correlation_id
        )
    
    @staticmethod
    async def handle_processing_failed(event: BaseEvent):
        """Handle file processing failure"""
        logger.error(f"File processing failed: {event.data}")
        
        # Send notification
        await event_bus.publish_event(
            EventType.NOTIFICATION_SENT,
            {
                "type": "error",
                "message": "File processing failed",
                "user_id": event.metadata.user_id,
                "details": event.data
            },
            "notification_service",
            correlation_id=event.metadata.correlation_id
        )

class AnalyticsServiceEventHandler:
    """Event handlers for analytics service"""
    
    @staticmethod
    async def handle_file_processed(event: BaseEvent):
        """Handle file processed event"""
        logger.info(f"Running analytics on processed file: {event.data}")
        
        # Perform analytics
        analytics_result = {
            "file_id": event.data.get("file_id"),
            "total_records": event.data.get("total_records", 0),
            "processing_time": event.data.get("processing_time", 0),
            "analytics_completed_at": datetime.now().isoformat()
        }
        
        await event_bus.publish_event(
            EventType.ANALYTICS_COMPLETED,
            analytics_result,
            "analytics_service",
            correlation_id=event.metadata.correlation_id
        )

class NotificationServiceEventHandler:
    """Event handlers for notification service"""
    
    @staticmethod
    async def handle_dashboard_generated(event: BaseEvent):
        """Handle dashboard generated event"""
        logger.info(f"Sending dashboard notification: {event.data}")
        
        # Send notification to user
        notification_data = {
            "user_id": event.metadata.user_id,
            "type": "dashboard_ready",
            "message": "Your dashboard is ready",
            "dashboard_url": event.data.get("dashboard_url"),
            "sent_at": datetime.now().isoformat()
        }
        
        await event_bus.publish_event(
            EventType.NOTIFICATION_SENT,
            notification_data,
            "notification_service",
            correlation_id=event.metadata.correlation_id
        )

# Service initialization functions
async def initialize_file_service():
    """Initialize file service event handlers"""
    await event_bus.subscribe_to_events(
        [EventType.FILE_UPLOADED],
        FileServiceEventHandler.handle_file_uploaded,
        "file_service"
    )

async def initialize_analytics_service():
    """Initialize analytics service event handlers"""
    await event_bus.subscribe_to_events(
        [EventType.FILE_PROCESSED],
        AnalyticsServiceEventHandler.handle_file_processed,
        "analytics_service"
    )

async def initialize_notification_service():
    """Initialize notification service event handlers"""
    await event_bus.subscribe_to_events(
        [EventType.DASHBOARD_GENERATED, EventType.FILE_PROCESSING_FAILED],
        NotificationServiceEventHandler.handle_dashboard_generated,
        "notification_service"
    )

# Utility functions for event publishing
async def publish_file_uploaded(
    file_id: str, 
    filename: str, 
    user_id: str,
    correlation_id: Optional[str] = None
):
    """Publish file uploaded event"""
    await event_bus.publish_event(
        EventType.FILE_UPLOADED,
        {
            "file_id": file_id,
            "filename": filename,
            "user_id": user_id,
            "uploaded_at": datetime.now().isoformat()
        },
        "file_service",
        correlation_id=correlation_id,
        user_id=user_id
    )

async def publish_dashboard_generated(
    dashboard_id: str,
    dashboard_url: str,
    user_id: str,
    correlation_id: Optional[str] = None
):
    """Publish dashboard generated event"""
    await event_bus.publish_event(
        EventType.DASHBOARD_GENERATED,
        {
            "dashboard_id": dashboard_id,
            "dashboard_url": dashboard_url,
            "generated_at": datetime.now().isoformat()
        },
        "file_service",
        correlation_id=correlation_id,
        user_id=user_id
    )

async def publish_system_error(
    error_message: str,
    service_name: str,
    error_details: Optional[Dict[str, Any]] = None
):
    """Publish system error event"""
    await event_bus.publish_event(
        EventType.SYSTEM_ERROR,
        {
            "error_message": error_message,
            "service_name": service_name,
            "error_details": error_details or {},
            "timestamp": datetime.now().isoformat()
        },
        service_name
    )