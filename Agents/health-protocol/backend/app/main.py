import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models.database import init_db
from app.api.upload import router as upload_router
from app.api.analyze import router as analyze_router
from app.api.protocol import router as protocol_router
from app.api.markers import router as markers_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure required directories exist and DB tables are created
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    await init_db()
    yield
    # Shutdown: nothing to clean up


app = FastAPI(
    title="Health Protocol Builder API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    # Also allow any device on a local 192.168.x.x network (mobile testing over WiFi)
    allow_origin_regex=r"http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(analyze_router, prefix="/api")
app.include_router(protocol_router, prefix="/api")
app.include_router(markers_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}
