import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter()

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
}


@router.post("/upload")
async def upload_report(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. "
                   "Accepted: PDF, JPEG, PNG, WEBP.",
        )

    # Read file and enforce size limit
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds {settings.max_upload_size_mb} MB limit.",
        )

    # Store with a UUID-prefixed name to avoid collisions
    ext = Path(file.filename or "upload").suffix or ".bin"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    dest = Path(settings.upload_dir) / stored_name

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)

    return JSONResponse(
        status_code=200,
        content={
            "status": "uploaded",
            "filename": stored_name,
            "original_filename": file.filename,
            "size_bytes": len(content),
            "content_type": file.content_type,
        },
    )
