# App Registry Layer (`app/registry/modules.py`)

The registry layer is the backend’s **module dispatch table**.
It maps external module names (received through the API) to concrete Python callables that execute the module logic.

In this project, the `JobService` does not import every module directly. Instead, it resolves modules through this registry, which keeps job orchestration decoupled from module implementations.

---

## Responsibility

The registry has one focused responsibility:

- Define the set of callable backend modules
- Provide a stable key-based lookup for job execution (`"cot"`, `"pipeline"`, `"export"`, ...)
- Enforce a shared runtime contract: each module exposes a `run(payload)` entrypoint

This design keeps the orchestration path simple and explicit.

---

## Current structure

```python
from modules.cot.main import run as run_cot
from modules.pipeline.main import run as run_pipeline
...

ModuleFn = Callable[[dict[str, Any] | None], Any]

MODULES: dict[str, ModuleFn] = {
	"cot": run_cot,
	"pipeline": run_pipeline,
	"export": run_export,
	"refine": run_refine,
	"rendering": run_rendering,
}
```

Technically, modules can be synchronous or asynchronous. `JobService` handles both modes at runtime.

---

## Runtime interaction

At runtime, the flow is:

1. API receives `POST /api/jobs` with `module` and optional `payload`
2. `JobService.create_job(...)` normalizes module name (`strip().lower()`)
3. Module key is validated against `MODULES`
4. `_run_job(...)` fetches the function from the registry and executes it

This means the registry is the **single source of truth** for what can be executed via the jobs API.

---

## Extension workflow: add a new module

To make a new module executable through the API:

1. Implement a `run(payload: dict[str, Any] | None)` function in the module package
2. Import that `run` function in `app/registry/modules.py`
3. Register it in the `MODULES` dictionary under a unique key

After that, clients can submit jobs with the new `module` key.

---

## Why this matters

- Keeps orchestration logic (`JobService`) independent from module internals
- Makes supported modules explicit and auditable
- Reduces accidental coupling and dynamic import complexity
- Provides one clear place to review execution surface of the backend
