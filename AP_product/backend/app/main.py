"""
AP Suite backend entry point.

Right now this is a stub: a FastAPI app with one health-check route so you can
confirm the server runs. We'll grow it slice by slice (ingestion, extraction,
matching, and so on) in later modules.
"""
from fastapi import FastAPI

app = FastAPI(title="AP Suite", version="0.1.0")


@app.get("/health")
def health():
    """Returns ok if the server is alive. Try it at http://localhost:8000/health"""
    return {"status": "ok", "service": "ap-suite", "version": "0.1.0"}
