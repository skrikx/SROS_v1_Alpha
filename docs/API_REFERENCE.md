# SROS v1 - API Reference

## Overview

The SROS HTTP API provides RESTful access to all SROS operations. Built with FastAPI.

## Starting the API Server

```bash
cd sros_v1
python -m sros.nexus.api.server
```

Server will start on `http://localhost:8000`

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Health & Status

#### GET /
Root endpoint with API information.

**Response:**
```json
{
  "name": "SROS API",
  "version": "1.0.0",
  "status": "operational"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### GET /api/status
Get system status.

**Response:**
```json
{
  "status": "operational",
  "version": "1.0.0",
  "components": {
    "kernel": "running",
    "runtime": "ready",
    "governance": "active",
    "mirroros": "observing"
  }
}
```

### Agents

#### GET /api/agents
List available agents.

**Response:**
```json
{
  "agents": [
    {"name": "architect", "role": "System Architect"},
    {"name": "builder", "role": "Code Builder"},
    {"name": "tester", "role": "Test Engineer"}
  ]
}
```

#### POST /api/agents/run
Run an agent with a task.

**Request Body:**
```json
{
  "agent_name": "architect",
  "task": "Analyze the memory system"
}
```

**Response:**
```json
{
  "status": "success",
  "agent": "architect",
  "result": "Analysis complete..."
}
```

### Memory

#### GET /api/memory
Read from memory.

**Query Parameters:**
- `layer` (optional): Memory layer (short, long, codex). Default: "short"
- `query` (optional): Search query

**Response:**
```json
{
  "status": "success",
  "layer": "short",
  "count": 5,
  "results": [...]
}
```

#### POST /api/memory
Write to memory.

**Request Body:**
```json
{
  "content": "Important data",
  "layer": "long",
  "key": "data_001"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Content written to memory"
}
```

### Adapters

#### GET /api/adapters
List available adapters.

**Response:**
```json
{
  "status": "success",
  "adapters": {
    "model": ["gemini", "openai", "local"],
    "tool": ["http"],
    "storage": ["filesystem"]
  }
}
```

### Costs

#### GET /api/costs
Get cost summary and budget status.

**Response:**
```json
{
  "status": "success",
  "budget": {
    "daily_cost": 2.50,
    "daily_budget": 100.0,
    "daily_exceeded": false,
    "monthly_cost": 45.00,
    "monthly_budget": 1000.0,
    "monthly_exceeded": false
  },
  "usage": {
    "daily_cost": 2.50,
    "monthly_cost": 45.00,
    "total_calls": 150,
    "adapter_counts": {
      "gemini": 120,
      "openai": 30
    }
  }
}
```

## Authentication

Currently, the API does not require authentication. For production use, implement:
- API key authentication
- JWT tokens
- OAuth2

## CORS

CORS is enabled for all origins in development. For production, configure specific origins in `server.py`.

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200`: Success
- `404`: Not Found
- `500`: Internal Server Error

## Examples

### Using curl

```bash
# Get status
curl http://localhost:8000/api/status

# Run agent
curl -X POST http://localhost:8000/api/agents/run \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "architect", "task": "Design feature"}'

# Write to memory
curl -X POST http://localhost:8000/api/memory \
  -H "Content-Type: application/json" \
  -d '{"content": "Important note", "layer": "long"}'

# Read from memory
curl "http://localhost:8000/api/memory?layer=long&query=important"
```

### Using Python

```python
import requests

# Get status
response = requests.get("http://localhost:8000/api/status")
print(response.json())

# Run agent
response = requests.post(
    "http://localhost:8000/api/agents/run",
    json={"agent_name": "architect", "task": "Analyze system"}
)
print(response.json())

# Write to memory
response = requests.post(
    "http://localhost:8000/api/memory",
    json={"content": "Data", "layer": "long", "key": "key1"}
)
print(response.json())
```

## Rate Limiting

Not currently implemented. For production, add rate limiting middleware.

## Deployment

For production deployment:

```bash
# Install production server
pip install uvicorn[standard]

# Run with production settings
uvicorn sros.nexus.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```
