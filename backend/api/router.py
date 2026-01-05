from fastapi import APIRouter
from api.routes.health import router as health_router
from api.routes.jobs import router as jobs_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
