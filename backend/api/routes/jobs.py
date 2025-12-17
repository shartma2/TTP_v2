from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class JobRequest(BaseModel):
    module: str
    payload: dict = {}

@router.post("")
def create_job(req: JobRequest):
    # später: Job anlegen, Worker starten, jobId zurückgeben
    return {"jobId": "dummy-1", "module": req.module, "received": req.payload}
