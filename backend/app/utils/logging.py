from datetime import datetime
import os
import json
import logging
from logging import Logger

LOGS_DIR = "/app/backend/logs"

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