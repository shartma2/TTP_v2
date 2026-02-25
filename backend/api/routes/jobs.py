from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any

from app.deps import get_job_service
from app.services.job_service import JobService

router = APIRouter()

class CreateJobRequest(BaseModel):
    module: str
    payload: dict[str, Any] | None = None

@router.post("")
async def create_job(
    req: CreateJobRequest,
    job_service: JobService = Depends(get_job_service)
    ):
    try: 
        job_id = await job_service.create_job(req.module, req.payload)
        return {"jobId": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("")
async def get_job(
    job_service: JobService = Depends(get_job_service)
    ):
    jobs = job_service.get_all_jobs()
    return jobs

@router.get("/{job_id}")
async def get_job(
    job_id: str,
    job_service: JobService = Depends(get_job_service)
    ):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"jobId": job_id, **job}