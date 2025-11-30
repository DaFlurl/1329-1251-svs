# AgentDaf1.1 API Reference

## Base URL
- **Development**: http://localhost:8080
- **Production**: http://your-domain.com

## Authentication
Most endpoints use JWT-based authentication. Include token in header:
```
Authorization: Bearer <your-jwt-token>
```

## Core Endpoints

### 1. Health Check
```http
GET /api/health
```
**Response**: System health status
```json
{
  "status": "healthy",
  "timestamp": "2025-11-27T10:00:00Z",
  "version": "1.1.0",
  "uptime": "2h 30m"
}
```

### 2. Dashboard Data
```http
GET /api/data
```
**Response**: Complete dashboard data in JSON format
```json
{
  "status": "success",
  "data": {
    "players": [...],
    "alliances": [...],
    "statistics": {...}
  }
}
```

### 3. Players API
```http
GET /api/players
```
**Response**: Player rankings and statistics
```json
{
  "status": "success",
  "data": [
    {
      "rank": 1,
      "name": "Player1",
      "score": 10000,
      "alliance": "AllianceA"
    }
  ]
}
```

### 4. Alliances API
```http
GET /api/alliances
```
**Response**: Alliance statistics and rankings
```json
{
  "status": "success",
  "data": [
    {
      "name": "AllianceA",
      "members": 10,
      "total_score": 50000,
      "rank": 1
    }
  ]
}
```

### 5. File Upload
```http
POST /api/upload
Content-Type: multipart/form-data
```
**Body**: Excel file to process
**Response**: Processing results
```json
{
  "status": "success",
  "message": "File processed successfully",
  "records_processed": 150
}
```

### 6. Database Management
```http
GET /database
```
**Response**: Database management interface (HTML)

### 7. Authentication
```http
POST /api/auth/login
Content-Type: application/json
```
**Body**: 
```json
{
  "username": "admin",
  "password": "password"
}
```
**Response**: JWT token
```json
{
  "status": "success",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Error Responses
All endpoints return consistent error format:
```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-11-27T10:00:00Z"
}
```

## Rate Limiting
- **Standard**: 100 requests per minute
- **Authenticated**: 1000 requests per minute

## WebSocket Support
Real-time updates available via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // Handle real-time updates
};
```