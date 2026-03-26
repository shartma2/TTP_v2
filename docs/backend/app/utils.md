# App Utilities Layer (`app/utils`)

The utilities layer provides cross-cutting helpers used by services and modules. In this backend, utilities focus on three concerns:

- structured logging
- serialization to JSON-safe structures
- domain-specific exception types

These helpers keep module/service code focused on business logic.

---

## Logging utilities (`app/utils/logging.py`)

### `configure_logging(...)`

Initializes root logging with a JSON-style formatter and a default field filter.

The `_DefaultFieldsFilter` ensures common metadata is present on each log record:

- `timestamp`
- `job_id` (defaults to `"N/A"` if absent)

Example output shape:

```json
{"timestamp":"...","level":"INFO","job_id":"...","message":"..."}
```

This makes logs machine-readable and easy to correlate per job.

### `get_logger(name)`

Returns namespaced loggers used across backend modules/services (e.g. `services.job_service`, `modules.pipeline.main`).

### `save_artifact(output, input, job_id, prefix)`

Persists execution artifacts as JSON files in `/app/backend/logs`.

It stores:

- job metadata (`job_id`, timestamp)
- normalized input
- normalized output

This is especially useful for debugging pipeline stages and preserving intermediate outputs.

---

## Serialization utility (`app/utils/jsonable.py`)

### `to_jsonable(obj)`

Converts arbitrary Python objects into JSON-serializable data recursively.

Handled types include:

- primitives (`str`, `int`, `float`, `bool`, `None`)
- `datetime` → ISO string
- `Enum` → enum value
- `Path` → string path
- `bytes` → UTF-8 text with replacement fallback
- `dict` / `list` / `tuple` / `set`
- Pydantic models (`model_dump` / `dict`)

As a final fallback, it returns `repr(obj)` to guarantee log/artifact safety.

This function is the key reason artifact logging can accept diverse model outputs without failing JSON encoding.

---

## Exception taxonomy (`app/utils/exceptions.py`)

The backend defines a small domain exception hierarchy:

- `JobError` (base class for controlled job failures)
- `MissingParameterException`
- `ModelValidationException`
- `InvalidPASSModelException`
- `InvalidExportFormatException`
- `JobNotFoundException`

`JobService` treats `JobError` differently from unexpected exceptions:

- `JobError` → controlled failure message in job record
- other exceptions → generic failure with full exception logging

This separation helps preserve user-facing error clarity while still capturing technical diagnostics.

---

## Why these utilities matter

- They standardize observability across all backend modules
- They reduce duplicated serialization/exception logic
- They make asynchronous job execution easier to debug and operate
