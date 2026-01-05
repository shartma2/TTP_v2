from fastapi import FastAPI
from api.router import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="TTP v2 Backend",
    version="0.1.0",
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

app.include_router(api_router)
