# Utilities

The `app/utils` package contains small cross-cutting helper modules that support the rest of the backend.
These utilities do not implement domain logic themselves. Instead, they provide reusable functionality for error modeling, serialization, and logging.

## Exceptions

The `exceptions.py` file defines the backend’s custom exception hierarchy. It introduces `JobError` as the common base class for controlled job-level failures and stores a human-readable `message` on the exception instance. On top of this base class, the file declares specialized exceptions such as `MissingParameterException`, `ModelValidationException`, `InvalidPASSModelException`, `InvalidExportFormatException`, and `JobNotFoundException`. This structure makes error cases explicit and provides a consistent way to distinguish expected business failures from unexpected runtime errors.

The utility is intentionally minimal. It does not contain handling logic itself, but instead provides standardized exception types that can be raised by other layers. This improves readability and keeps error semantics centralized in a single place.

## JSON Serialization Helper

The `jsonable.py` file provides the function `to_jsonable(obj: Any) -> Any`, which converts arbitrary Python objects into JSON-serializable representations. It explicitly handles primitive values, datetime, Enum, Path, bytes, dictionaries, and collection types recursively. It also supports Pydantic models and falls back to methods such as `model_dump()`, `dict()`, or `to_json()` when available. As a final fallback, it returns `repr(obj)` so that unsupported values remain at least loggable.

This helper is mainly relevant because backend artifacts and structured logs may contain complex Python objects that cannot be written directly as JSON. The function therefore acts as a small normalization layer between internal runtime objects and serialized output.

## Logging

The `logging.py` file centralizes logging-related functionality. It defines `configure_logging()`, `get_logger()`, and `save_artifact()`, as well as the internal `_DefaultFieldsFilter`. The filter ensures that each log record contains a job_id field and a generated timestamp, while `configure_logging()` installs a stream handler with a JSON-style log format containing `timestamp`, `level`, `job_id`, and `message`. This creates a consistent structured logging format for the backend.

In addition to runtime logging, the file also supports artifact persistence. The `save_artifact()` function writes structured JSON files into `/app/backend/logs`, creating the directory if necessary. Each artifact contains optional input data, and output data. Both input and output are passed through `to_jsonable()` beforehand so that complex objects can be written safely.