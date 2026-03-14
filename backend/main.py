from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from app.services.job_service import JobService
from app.utils.logging import configure_logging
from app.utils.logging import get_logger



@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(logging.INFO)
    logger = get_logger("backend.main")
    logger.info("Starting up application...")
    app.state.job_service = JobService(max_concurrent_jobs=4)
    logger.info("JobService initialized.")
    yield
    logger.info("Backend shutdown initiated")
    await app.state.job_service.shutdown()
    logger.info("Backend shutdown complete")

def create_app() -> FastAPI:
    app = FastAPI(
        title="TTP Backend Service",
        description="A backend service for processing modular tasks asynchronously.",
        version="1.0.1",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()




