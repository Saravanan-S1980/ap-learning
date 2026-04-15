"""Protocol endpoints: GET /api/protocol/{id}  and  GET /api/protocols."""
import json

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, desc

from app.models.database import ExtractionRecord, ProtocolRecord, AsyncSessionLocal
from app.models.protocol import Protocol

router = APIRouter()


async def save_protocol(
    protocol_id: str,
    protocol: Protocol,
    *,
    goals: list[str],
    extraction_id: str,
) -> None:
    """Persist a protocol to SQLite, denormalising lab info from the extraction."""
    lab_name: str | None = None
    report_date: str | None = None
    marker_count: int = 0

    async with AsyncSessionLocal() as db:
        extraction = await db.get(ExtractionRecord, extraction_id)
        if extraction:
            lab_name = extraction.lab_name
            report_date = extraction.report_date
            marker_count = extraction.marker_count or 0

        record = ProtocolRecord(
            id=protocol_id,
            extraction_id=extraction_id,
            goals=json.dumps(goals),
            protocol_json=protocol.model_dump_json(),
            lab_name=lab_name,
            report_date=report_date,
            marker_count=marker_count,
        )
        db.add(record)
        await db.commit()


@router.get("/protocol/{protocol_id}")
async def get_protocol(protocol_id: str) -> Protocol:
    async with AsyncSessionLocal() as db:
        record = await db.get(ProtocolRecord, protocol_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Protocol '{protocol_id}' not found.",
        )

    return Protocol.model_validate_json(record.protocol_json)


@router.get("/protocols")
async def list_protocols() -> list[dict]:
    """Return all past protocols, newest first, for the History tab and Recent Reports."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ProtocolRecord).order_by(desc(ProtocolRecord.created_at))
        )
        records = result.scalars().all()

    return [
        {
            "id": r.id,
            "extraction_id": r.extraction_id,
            "lab_name": r.lab_name,
            "report_date": r.report_date,
            "marker_count": r.marker_count,
            "goals": json.loads(r.goals) if r.goals else [],
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
