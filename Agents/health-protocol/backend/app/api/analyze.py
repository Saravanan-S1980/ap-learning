"""POST /api/analyze — run the full 4-step analysis chain.

Request body:
    markers       — list of ExtractedMarker (from upload response)
    goals         — list of goal IDs (e.g. ["cardiovascular_health", "energy_vitality"])
    extraction_id — optional, for traceability

Response:
    protocol_id — UUID for retrieval via GET /api/protocol/{id}
    protocol    — full Protocol object (diet, supplements, lifestyle, retest)
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from app.data.goals import GOALS
from app.models.markers import ExtractedMarker
from app.models.protocol import Protocol
from app.services.goal_crossref import crossref_goals
from app.services.marker_flagger import flag_markers
from app.services.marker_normalizer import normalize_markers
from app.services.protocol_generator import generate_protocol

# Import store functions from protocol router module
from app.api.protocol import save_protocol

router = APIRouter()


class AnalyzeRequest(BaseModel):
    markers: list[ExtractedMarker]
    goals: list[str]
    extraction_id: str = ""

    @field_validator("goals")
    @classmethod
    def validate_goals(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("At least one goal must be provided.")
        if len(v) > 3:
            raise ValueError("Maximum 3 goals allowed.")
        unknown = [g for g in v if g not in GOALS]
        if unknown:
            raise ValueError(
                f"Unknown goal(s): {unknown}. "
                f"Valid goals: {list(GOALS.keys())}"
            )
        return v

    @field_validator("markers")
    @classmethod
    def validate_markers(cls, v: list[ExtractedMarker]) -> list[ExtractedMarker]:
        if not v:
            raise ValueError("At least one marker must be provided.")
        return v


class AnalyzeResponse(BaseModel):
    protocol_id: str
    protocol: Protocol
    step_warnings: list[str] = []


@router.post("/analyze")
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Run the 4-step analysis chain and return a stored protocol."""
    all_warnings: list[str] = []

    # ── Step 1: Normalize ────────────────────────────────────────────────────
    norm_result = normalize_markers(request.markers)
    all_warnings.extend(norm_result.warnings)

    # ── Step 2: Flag ─────────────────────────────────────────────────────────
    try:
        flag_result = await flag_markers(norm_result.markers)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Flagging error: {exc}")

    all_warnings.extend(flag_result.warnings)

    # ── Step 3: Cross-reference goals ────────────────────────────────────────
    crossref = crossref_goals(flag_result.flagged_markers, request.goals)
    all_warnings.extend(crossref.warnings)

    # ── Step 4: Generate protocol ────────────────────────────────────────────
    extraction_id = request.extraction_id or uuid.uuid4().hex
    try:
        protocol = await generate_protocol(
            flagged_markers=flag_result.flagged_markers,
            crossref=crossref,
            goals=request.goals,
            extraction_id=extraction_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Protocol generation failed: {exc}")

    all_warnings.extend(protocol.warnings)

    # ── Store and return ─────────────────────────────────────────────────────
    protocol_id = uuid.uuid4().hex
    save_protocol(protocol_id, protocol)

    return AnalyzeResponse(
        protocol_id=protocol_id,
        protocol=protocol,
        step_warnings=all_warnings,
    )
