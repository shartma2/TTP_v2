from __future__ import annotations

from typing import Any, Callable, Awaitable
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
import asyncio

from app.registry.modules import MODULES
from app.utils.logging import get_logger
from app.utils.exceptions import JobError

logger = get_logger("services.job_service")

JobId = str
Payload = dict[str, Any] | None
Result = Any

SyncModuleFunction = Callable[[Payload], Result]
AsyncModuleFunction = Callable[[Payload], Awaitable[Result]]
ModuleFunction = SyncModuleFunction | AsyncModuleFunction

@dataclass
class JobRecord:
    status: str
    module: str | None = None
    result: Any = None
    error: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None



class JobService:
    """
    Actual Job Service managing job execution and state.
    """
    def __init__(self, max_concurrent_jobs: int = 4):
        self._jobs: dict[JobId, JobRecord] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent_jobs)

        self._tasks: set[asyncio.Task] = set()
    
    async def create_job(self, module: str, payload: Payload) -> JobId:
        module = module.strip().lower()
        if module not in MODULES:
            logger.warning("Unknown module requested", extra={"job_module": module})
            raise ValueError(f"Unknown module: {module}")

        timestamp = datetime.now().isoformat() + "Z"
        job_id: JobId = str(uuid.uuid4())
        payload = dict(payload or {})
        payload["job_id"] = job_id
        self._jobs[job_id] = JobRecord(status="queued", module=module, created_at=timestamp)

        logger.info("Job Queued", extra={"job_id": job_id, "job_module": module})

        task = asyncio.create_task(self._run_job(job_id, module, payload))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        return job_id
    
    def get_job(self, jobId: str) -> dict[str, Any] | None:
        job = self._jobs.get(jobId)
        if not job:
            return None
        return {
            "jobId": jobId,
            "status": job.status,
            "result": job.result,
            "error": job.error,
            "module": job.module,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at
            }
    
    def get_all_jobs(self) -> list[dict[str, Any]]:
        result = []

        for job_id, job in self._jobs.items():
            job_dict = asdict(job)

            for key in ["createdAt", "startedAt", "finishedAt"]:
                value = job_dict.get(key)
                if isinstance(value, datetime):
                    job_dict[key] = value.isoformat()

            job_dict["jobId"] = str(job_id)
            result.append(job_dict)
        
        return result
    
    async def _run_job(self, job_id: JobId, module: str, payload: Payload) -> None:
        async with self._semaphore:
            job = self._jobs[job_id]
            job.started_at = datetime.now().isoformat() + "Z"
            job.status = "running"
            logger.info("Job started", extra={"job_id": job_id, "job_module": module})
            function = MODULES[module]
            try:
                if asyncio.iscoroutinefunction(function):
                    result = await function(payload)
                else:
                    result = await asyncio.to_thread(function, payload)
                
                job.finished_at = datetime.now().isoformat() + "Z"
                job.status = "done"
                job.result = result

                logger.info("Job completed", extra={"job_id": job_id, "job_module": module})

            except JobError as e:
                job.finished_at = datetime.now().isoformat() + "Z"
                job.error = e.message
                job.status = "failed"
                logger.warning("Job failed (controlled)",extra={"job_id": job_id, "job_module": module},)

            except Exception as e:
                job.finished_at = datetime.now().isoformat() + "Z"
                job.error = str(e)
                job.status = "failed"
                logger.exception("Error running job", extra={"job_id": job_id, "job_module": module})
    
    async def shutdown(self) -> None:
        """
        Gracefully shutdown the JobService, waiting for all running jobs to complete.
        """
        if not self._tasks:
            return
        
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()