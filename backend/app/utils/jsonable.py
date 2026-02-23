from __future__ import annotations
from typing import Any
from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import BaseModel



def to_jsonable(obj: Any) -> Any:
    """
    Convert arbitrary objects into JSON-serializable structures.

    Handles:
    - Pydantic BaseModel (v2: model_dump, v1: dict)
    - datetime
    - Enum
    - Path
    - bytes
    - dict/list/tuple recursively
    - fallback: string representation
    """
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, bytes):
        # keep it readable; you can also base64 encode if needed
        return obj.decode("utf-8", errors="replace")

    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]

    # Pydantic model (v2 preferred)
    if BaseModel is not None and isinstance(obj, BaseModel):
        if hasattr(obj, "model_dump"):  # pydantic v2
            return obj.model_dump(mode="json")
        return obj.dict()  # pydantic v1

    # Common langchain objects often have .dict() / .model_dump() / .to_json()
    for attr in ("model_dump", "dict", "to_json"):
        if hasattr(obj, attr) and callable(getattr(obj, attr)):
            try:
                val = getattr(obj, attr)()
                return to_jsonable(val)
            except Exception:
                pass

    # last resort: make it at least loggable
    return repr(obj)
