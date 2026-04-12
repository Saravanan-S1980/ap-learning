import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.pdf_extractor import extract_text

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

    # Only attempt text extraction on PDFs
    extracted_text: str | None = None
    page_count: int | None = None
    warnings: list[str] = []

    if file.content_type == "application/pdf":
        try:
            result = extract_text(dest)
            extracted_text = result.text
            page_count = result.pages
            warnings = result.warnings
        except ValueError as exc:
            # Password-protected — keep the file but surface the error
            dest.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc))
        except RuntimeError as exc:
            # Corrupt / unreadable PDF
            dest.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc))
        finally:
            # Per CLAUDE.md: delete uploaded PDFs after extraction
            if dest.exists():
                dest.unlink(missing_ok=True)

    response_body: dict = {
        "status": "uploaded",
        "filename": stored_name,
        "original_filename": file.filename,
        "size_bytes": len(content),
        "content_type": file.content_type,
    }

    if extracted_text is not None:
        response_body["text"] = extracted_text
        response_body["pages"] = page_count
        response_body["warnings"] = warnings

    return JSONResponse(status_code=200, content=response_body)
