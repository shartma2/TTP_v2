from __future__ import annotations
from typing import Any
import base64
import json

from app.utils.logging import get_logger
from app.utils.exceptions import InvalidExportFormatException, JobNotFoundException


logger = get_logger("modules.pipeline.main")

def run(payload: dict[str, Any]) -> dict[str, Any]:
    
    job_id = payload.get("job_id", "N/A")
    source_job_id = payload.get("source_job_id", "N/A")
    format = payload.get("format", None)
    job = payload.get("result", None)

    if(not job):
        logger.error("Job not found", extra={"source_job_id": source_job_id})
        raise JobNotFoundException(f"Job not found: {source_job_id}")


    module = job.get("module", "N/A")
    status = job.get("status", "N/A")

    if status != "done":
        logger.error("Job is not ready for export", extra={"job_id": job_id},)
        raise JobNotFoundException(f"Job is not ready for export: {source_job_id}")

    result = job.get("result", {}).get("response")



    logger.info("Running Export module", extra={"job_id": job_id, "format": format})

    match (module, format):
        case (_, ".txt"):
            fileName = "export.txt"
            contentType = "text/plain; charset=utf-8"
            raw_bytes = _to_txt_bytes(result)

        case ("pipeline", ".json"):
            fileName = "export.json"
            contentType = "application/json"
            raw_bytes = _to_json_bytes(result)

        case ("pipeline", ".owl"):
            fileName = "export.owl"
            contentType = "application/rdf+xml"
            raw_bytes = _to_owl_bytes(result)
        
        case (_, _):
            logger.error("Unsupported format", extra={"job_id": job_id, "format": format})
            raise InvalidExportFormatException(f"Unsupported format: {format}")

    result = {
        "fileName": fileName,
        "contentType": contentType,
        "sizeBytes": len(raw_bytes),
        "dataBase64": base64.b64encode(raw_bytes).decode("ascii"),
     }

    return {"response": result}

def _to_txt_bytes(result: str) -> bytes:
    return _to_bytes(result)


def _to_json_bytes(result: str) -> bytes:
    # Placeholder:
    return _to_bytes(result)


def _to_owl_bytes(result: str) -> bytes:
    # Placeholder
    return _to_bytes(result)

def _to_bytes(data: Any) -> bytes:
    if data is None:
        return b""

    if isinstance(data, bytes):
        return data

    if isinstance(data, str):
        return data.encode("utf-8")

    if isinstance(data, (dict, list)):
        return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

    return str(data).encode("utf-8")