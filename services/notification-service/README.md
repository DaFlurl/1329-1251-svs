# AgentDaf1.1 - Notification Service

## Overview
Notification service for the AgentDaf1.1 platform that handles real-time notifications via WebSocket connections.

## Features
- Real-time WebSocket notifications
- JWT authentication
- Database integration
- Message broadcasting
- Notification history

## API Endpoints
- `POST /api/notifications` - Send notification
- `GET /api/notifications` - Get notification history
- `WebSocket /ws/notifications` - Real-time updates

## Configuration
Environment variables:
- `DATABASE_URL` - Database connection URL
- `JWT_SECRET_KEY` - JWT signing key
- `NOTIFICATION_TTL` - Notification time-to-live (seconds)

## Dependencies
- FastAPI for REST API
- WebSockets for real-time communication
- SQLAlchemy for database operations
- Pydantic for data validation

## Development
Run with: `python -m uvicorn notification_service:app --host 0.0.0.0 --port 8003`