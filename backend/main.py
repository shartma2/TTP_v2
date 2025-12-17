from fastapi import FastAPI
from api.router import api_router

app = FastAPI(
    title="TTP v2 Backend",
    version="0.1.0",
)

app.include_router(api_router)
