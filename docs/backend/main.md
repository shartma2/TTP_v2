# Backend Application Entry Point (`main.py`)

The `main.py` file is the primary entry point of the backend service. It is responsible for:

- Creating and configuring the FastAPI application instance
- Registering middleware (CORS)
- Wiring the API router under `/api`
- Managing application startup and shutdown via FastAPI’s **lifespan** mechanism
- Initializing shared runtime services (notably `JobService`) and attaching them to `app.state`

This file therefore defines the backend’s **composition root** (i.e., the place where dependencies are created and assembled).

---

## Lifecycle management

The backend uses FastAPI’s lifespan API via an `@asynccontextmanager`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    yield
    ...