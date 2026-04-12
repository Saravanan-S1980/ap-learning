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
