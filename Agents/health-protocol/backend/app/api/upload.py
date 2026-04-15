import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.database import ExtractionRecord, AsyncSessionLocal
from app.services.pdf_extractor import extract_text
from app.services.marker_parser import parse_markers

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

    # Only attempt extraction pipeline on PDFs
    if file.content_type != "application/pdf":
        response_body: dict = {
            "status": "uploaded",
            "filename": stored_name,
            "original_filename": file.filename,
            "size_bytes": len(content),
            "content_type": file.content_type,
        }
        return JSONResponse(status_code=200, content=response_body)

    # --- PDF pipeline: extract text → parse markers ---
    try:
        pdf_result = extract_text(dest)
    except (ValueError, RuntimeError) as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        # Per CLAUDE.md: delete uploaded PDFs after extraction
        if dest.exists():
            dest.unlink(missing_ok=True)

    all_warnings: list[str] = list(pdf_result.warnings)

    try:
        extraction = await parse_markers(pdf_result.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Marker extraction failed: {exc}")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")

    all_warnings.extend(extraction.warnings)

    # Persist to DB
    extraction_id = uuid.uuid4().hex
    record = ExtractionRecord(
        id=extraction_id,
        filename=stored_name,
        lab_name=extraction.lab_name,
        report_date=extraction.report_date,
        extraction_confidence=extraction.extraction_confidence,
        raw_json=json.dumps([m.model_dump() for m in extraction.markers]),
        marker_count=len(extraction.markers),
    )
    async with AsyncSessionLocal() as db:
        db.add(record)
        await db.commit()

    response_body = {
        "status": "uploaded",
        "extraction_id": extraction_id,
        "filename": stored_name,
        "original_filename": file.filename,
        "size_bytes": len(content),
        "content_type": file.content_type,
        "pages": pdf_result.pages,
        "lab_name": extraction.lab_name,
        "report_date": extraction.report_date,
        "markers": [m.model_dump() for m in extraction.markers],
        "extraction_confidence": extraction.extraction_confidence,
        "warnings": all_warnings,
    }

    return JSONResponse(status_code=200, content=response_body)
