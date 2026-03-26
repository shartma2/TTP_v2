# API Layer

The API layer exposes the backend functionality via HTTP endpoints implemented with FastAPI.  
All routes are mounted under the global `/api` prefix (configured in [main.py](main.md)).

The API is intentionally thin: it performs request validation, delegates execution to the [service layer](./app/services.md), and maps domain errors to HTTP responses. No business logic is implemented directly inside the route handlers.

---

## Router Composition

The central router aggregates all sub-routers and defines their URL prefixes.

**File:** `api/router.py`

```python
from fastapi import APIRouter
from api.routes.health import router as health_router
from api.routes.jobs import router as jobs_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
```

## Endpoint Overview

The API currently exposes two main endpoint groups with clearly separated responsibilities:

### Health Endpoints
Purpose: System monitoring and availability checks
Typical use: Container health checks, uptime verification, orchestration tools

The health endpoint provides a lightweight response indicating whether the backend service is running. It does not depend on business logic or internal state.

### Job Endpoints
Purpose: Core interaction with the backend system
Typical use: Creating, monitoring, and retrieving processing tasks

The job endpoints act as the primary interface for clients. They accept requests, delegate execution to the service layer, and return job-related data such as status and results.