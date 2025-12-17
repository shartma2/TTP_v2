from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Literal
import uuid

from modules.CoT import run as run_cot

router = APIRouter()

MODULES = {
    "cot": run_cot,
}

JOBS: dict[str, dict[str, Any]] = {}

class CreateJobRequest(BaseModel):
    module: str 

@router.post("")
def create_job(req: CreateJobRequest):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "running", "result": None, "error": None}

    try:
        if req.module not in MODULES:
            raise HTTPException(status_code=400, detail="Unknown module")

        if req.module == "cot":
            result = MODULES["cot"]()
            JOBS[job_id]["result"] = {"output": result}

        JOBS[job_id]["status"] = "done"
        return {"jobId": job_id}

    except HTTPException:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = "validation error"
        raise
    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail="Job execution failed")

@router.get("/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, **job}
