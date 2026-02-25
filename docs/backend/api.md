# API Layer

The API layer exposes the backend functionality via HTTP endpoints implemented with FastAPI.  
All routes are mounted under the global `/api` prefix (configured in `main.py`).

The API is intentionally thin: it performs request validation, delegates execution to the service layer, and maps domain errors to HTTP responses. No business logic is implemented directly inside the route handlers.

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