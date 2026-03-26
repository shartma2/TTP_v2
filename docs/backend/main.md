# Backend Application Entry Point (`main.py`)

The `main.py` file is the entry point of the backend service. It is responsible for **initializing and configuring the FastAPI application instance**, as well as managing its lifecycle.

Its responsibilities are strictly limited to:

- Defining application startup and shutdown behavior
- Configuring logging
- Initializing shared services
- Registering middleware (CORS)
- Mounting the API router

This file acts as the **composition root**, where core components are instantiated and wired together.

---

## Lifecycle Management

The application lifecycle is managed using FastAPI’s lifespan mechanism via an `@asynccontextmanager`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(logging.INFO)
    logger = get_logger("backend.main")
    logger.info("Starting up application...")

    app.state.job_service = JobService(max_concurrent_jobs=4)
    logger.info("JobService initialized.")

    yield

    logger.info("Backend shutdown initiated")
    await app.state.job_service.shutdown()
    logger.info("Backend shutdown complete")
```
### Startup Phase

Before the `yield`, the application performs initialization:

- Logging is configured via `configure_logging`
- A module-specific logger is created
- The `JobService` is instantiated with a defined concurrency limit
- The service is attached to `app.state` for global access

This ensures that all required runtime components are available before handling requests.

### Shutdown Phase

After the yield, graceful shutdown logic is executed:

- A shutdown log message is emitted
- The `JobService` is properly terminated via its `shutdown()` method
- Final shutdown confirmation is logged

This guarantees a clean termination of background processes and resources.

## Middleware Configuration (CORS)

CORS middleware is configured to allow requests from the frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Key aspects:

- Restricts access to the local frontend origin
- Allows credentials and all HTTP methods/headers
- Enables browser-based communication between frontend and backend

## API Router Registration

The API routes are registered with a common prefix:

```python
app.include_router(api_router, prefix="/api")
```

This ensures that all endpoints are accessible under the `/api` namespace.

