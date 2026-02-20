import logging
from logging import Logger

from datetime import datetime
import json
from pathlib import Path
from typing import Any

from app.utils.jsonable import to_jsonable

LOGS_DIR = Path("/app/backend/logs")


class _DefaultFieldsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "job_id"):
            record.job_id = "N/A"
        record.timestamp = datetime.now().isoformat() + "Z"
        return True

def configure_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.setLevel(level)
    
    if root.hasHandlers():
        return
    
    handler = logging.StreamHandler()
    handler.addFilter(_DefaultFieldsFilter())

    formatter = logging.Formatter(
        '{"timestamp": "%(timestamp)s", "level": "%(levelname)s", "job_id": "%(job_id)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)

def get_logger(name: str) -> Logger:
    return logging.getLogger(name)

def save_artifact(output: Any, input: Any = None, job_id = None,prefix: str = None):
    LOGS_DIR.mkdir(parents=True, exist_ok=True) 
    artifact_path = LOGS_DIR / f"{prefix}_{job_id}.json"
    artifact = {
        "job_id": job_id,
        "timestamp": datetime.now().isoformat() ,
        "input": to_jsonable(input),
        "output": to_jsonable(output),
    }
    with artifact_path.open("w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)