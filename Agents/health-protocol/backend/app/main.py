import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router
from app.api.protocol import router as protocol_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure required directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    yield
    # Shutdown: nothing to clean up yet


app = FastAPI(
    title="Health Protocol Builder API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(protocol_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}
