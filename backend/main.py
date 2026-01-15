from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from app.services.job_service import JobService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.job_service = JobService(max_concurrent_jobs=4)
    yield
    await app.state.job_service.shutdown()

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
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )
    return app

app = create_app()




