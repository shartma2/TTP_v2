from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
import uuid
import logging
import asyncio

from modules.CoT import run as run_cot

logger = logging.getLogger("jobs")
router = APIRouter()

MODULES = {
    "cot": run_cot,
}

JOBS: dict[str, dict[str, Any]] = {}

JOB_SEMAPHORE = asyncio.Semaphore(4) 

class CreateJobRequest(BaseModel):
    module: str
    payload: dict[str, Any] | None = None 

@router.post("")
async def create_job(req: CreateJobRequest):
    module = req.module.strip().lower()
    if module not in MODULES:
        raise HTTPException(
            status_code=400,
            detail="Unknown module"
        )
    
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {
        "status": "queued",
        "result": None,
        "error": None
        }

    asyncio.create_task(_run_job(job_id, module, req.payload))

    return {"jobId": job_id}

@router.get("/{job_id}")
async def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, **job}

async def _run_job(job_id: str, module: str, payload: dict[str, Any] | None):
    async with JOB_SEMAPHORE:
        JOBS[job_id]["status"] = "running"
        try: 
            fn = MODULES[module]
            
            result = await asyncio.to_thread(fn, payload)
            
            JOBS[job_id]["result"] = result
            JOBS[job_id]["status"] = "done"

        except Exception as e:
            logger.exception(f"Job {job_id} failed")
            JOBS[job_id]["error"] = str(e)
            JOBS[job_id]["status"] = "failed"