from typing import Literal
from pydantic import BaseModel


class ExtractedMarker(BaseModel):
    name: str
    reported_name: str
    value: float | None = None
    qualitative_value: str | None = None
    unit: str
    reference_low: float | None = None
    reference_high: float | None = None
    flag: Literal["normal", "low", "high", "critical_low", "critical_high"] = "normal"
    category: Literal[
        "CBC", "Lipid", "Thyroid", "Liver", "Kidney",
        "Vitamin", "Mineral", "Hormone", "Metabolic",
        "Inflammatory", "Other"
    ] = "Other"
    test_date: str | None = None


class ExtractionResult(BaseModel):
    lab_name: str | None = None
    patient_name: str | None = None
    report_date: str | None = None
    markers: list[ExtractedMarker] = []
    extraction_confidence: float = 0.0
    warnings: list[str] = []


# ── Analysis chain models ────────────────────────────────────────────────────

class FlaggedMarker(BaseModel):
    """A marker that is outside its lab or optimal range, enriched with Claude's assessment."""
    marker: ExtractedMarker
    canonical_name: str
    # Comparison against population lab reference
    lab_status: Literal["normal", "low", "high"]
    # Comparison against evidence-based optimal range
    optimal_status: Literal["optimal", "suboptimal_low", "suboptimal_high"]
    # Clinical significance assigned by Claude
    severity: Literal["normal", "mild", "moderate", "significant"] = "mild"
    clinical_notes: str = ""
    related_markers: list[str] = []
    retest_weeks: int = 12


class FlaggingResult(BaseModel):
    flagged_markers: list[FlaggedMarker] = []
    normal_markers: list[ExtractedMarker] = []
    warnings: list[str] = []
