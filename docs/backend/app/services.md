# App Services Layer (`app/services/job_service.py`)

The services layer contains backend business orchestration. In the current architecture, this layer is centered around `JobService`, which manages asynchronous module execution and in-memory job state.

The API layer delegates job operations to this service instead of executing module logic directly in route handlers.

---

## Core responsibilities of `JobService`

`JobService` is responsible for:

- Creating and tracking jobs (`queued`, `running`, `done`, `failed`)
- Validating requested module names against the module registry
- Executing module functions in the background
- Limiting concurrent execution via an `asyncio.Semaphore`
- Capturing module results or controlled/uncontrolled errors
- Supporting graceful shutdown by cancelling pending tasks

This makes `JobService` the central runtime coordinator for backend workloads.

---

## Data model: `JobRecord`

Each job is represented by a `JobRecord` dataclass containing:

- status
- module
- result
- error
- created/start/finish timestamps

The service stores these records in an in-memory dictionary keyed by `job_id`.

Important implication: job state is process-local and non-persistent. A restart clears all existing job records.

---

## Lifecycle of a job

### 1) Job creation

`create_job(module, payload)` performs:

- module normalization (`strip().lower()`)
- module existence check against `MODULES`
- `job_id` generation (`uuid4`)
- payload enrichment with `job_id`
- in-memory insertion with status `queued`
- scheduling `_run_job(...)` via `asyncio.create_task(...)`

The method returns immediately with `job_id`, enabling non-blocking API behavior.

### 2) Job execution

`_run_job(job_id, module, payload)` runs inside semaphore-controlled context:

- sets status to `running`
- resolves callable from registry
- executes async modules via `await` or sync modules via `asyncio.to_thread(...)`
- writes result and marks status `done`

### 3) Error handling

Two error paths are used:

- `JobError`: controlled/domain failure, mapped to a user-facing error string
- generic `Exception`: unexpected runtime failure, logged with stack trace

Both paths mark status `failed` and set `finished_at`.

---

## API integration

`app/deps.py` exposes `get_job_service(request)` to fetch the singleton service from `app.state`.

This dependency is injected into route handlers in `api/routes/jobs.py`:

- `POST /api/jobs` → `create_job(...)`
- `GET /api/jobs` → `get_all_jobs()`
- `GET /api/jobs/{job_id}` → `get_job(...)`

As a result, API endpoints remain thin, while service logic stays centralized and testable.

---

## Startup and shutdown integration

`main.py` initializes one `JobService` instance during lifespan startup and stores it in `app.state.job_service`.

During shutdown, `JobService.shutdown()` cancels tracked tasks and awaits them with `return_exceptions=True`, allowing clean service termination.

---

## Design notes and trade-offs

- **Strength:** very simple async orchestration model
- **Strength:** clear separation between API transport and job execution logic
- **Trade-off:** in-memory storage means no durability across restarts
- **Trade-off:** no built-in retry, priority, or distributed execution (by design, for now)
