"""Marker parsing service — converts raw PDF text into structured ExtractedMarker objects.

Flow:
    raw text → Claude Haiku (EXTRACTION_SYSTEM + EXTRACTION_USER_TEMPLATE)
             → JSON response
             → validate with pydantic
             → ExtractionResult
"""
from __future__ import annotations

import logging

from pydantic import ValidationError

from app.models.markers import ExtractionResult, ExtractedMarker
from app.utils.claude_client import HAIKU_MODEL, call_claude_json
from app.utils.prompts import EXTRACTION_SYSTEM, EXTRACTION_USER_TEMPLATE

logger = logging.getLogger(__name__)

# Claude Haiku token budget for extraction (generous for long reports)
_EXTRACTION_MAX_TOKENS = 2048


async def parse_markers(text: str) -> ExtractionResult:
    """Parse raw lab-report text into a structured ExtractionResult.

    Args:
        text: Plain text extracted from a PDF (or OCR output).

    Returns:
        ExtractionResult with validated markers, confidence score, and warnings.

    Raises:
        ValueError: If Claude returns invalid JSON after the repair retry.
        RuntimeError: If all Claude API retries are exhausted.
    """
    if not text or not text.strip():
        return ExtractionResult(
            warnings=["No text provided — cannot extract markers."],
            extraction_confidence=0.0,
        )

    user_prompt = EXTRACTION_USER_TEMPLATE.format(text=text)

    raw_data = await call_claude_json(
        model=HAIKU_MODEL,
        system=EXTRACTION_SYSTEM,
        user=user_prompt,
        max_tokens=_EXTRACTION_MAX_TOKENS,
    )

    return _build_result(raw_data)


def _build_result(data: dict) -> ExtractionResult:
    """Validate and coerce the raw Claude JSON dict into an ExtractionResult.

    Handles per-marker validation failures gracefully — a bad marker is skipped
    and a warning is appended rather than crashing the whole extraction.
    """
    warnings: list[str] = list(data.get("warnings") or [])
    good_markers: list[ExtractedMarker] = []

    for raw_marker in data.get("markers") or []:
        try:
            good_markers.append(ExtractedMarker.model_validate(raw_marker))
        except ValidationError as exc:
            name = raw_marker.get("reported_name") or raw_marker.get("name") or "<unknown>"
            logger.warning("Skipping marker %r due to validation error: %s", name, exc)
            warnings.append(
                f"Marker '{name}' was skipped due to a data validation error: {exc.error_count()} field(s) invalid."
            )

    confidence = float(data.get("extraction_confidence") or 0.0)
    # Clamp to [0.0, 1.0]
    confidence = max(0.0, min(1.0, confidence))

    return ExtractionResult(
        lab_name=data.get("lab_name"),
        patient_name=None,  # Always null — privacy requirement
        report_date=data.get("report_date"),
        markers=good_markers,
        extraction_confidence=confidence,
        warnings=warnings,
    )
