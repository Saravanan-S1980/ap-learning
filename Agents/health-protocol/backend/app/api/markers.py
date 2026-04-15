"""GET /api/extraction/{id} — retrieve a saved extraction by ID."""
import json

from fastapi import APIRouter, HTTPException

from app.models.database import ExtractionRecord, AsyncSessionLocal

router = APIRouter()


@router.get("/extraction/{extraction_id}")
async def get_extraction(extraction_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        record = await db.get(ExtractionRecord, extraction_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Extraction '{extraction_id}' not found.",
        )

    markers = json.loads(record.raw_json) if record.raw_json else []
    return {
        "id": record.id,
        "lab_name": record.lab_name,
        "report_date": record.report_date,
        "extraction_confidence": record.extraction_confidence,
        "markers": markers,
        "marker_count": record.marker_count,
        "warnings": [],
    }
