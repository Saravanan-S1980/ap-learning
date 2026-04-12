"""Step 1 of the analysis chain: normalize marker names and units.

Pure Python — no Claude API call. Fast and deterministic.

Steps:
    1. Alias → canonical name resolution
    2. Unit string normalization (case / symbol fixes, no value scaling)
    3. Deduplication  (keep the most complete entry per canonical name)
    4. Suspicious value detection
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.models.markers import ExtractedMarker
from app.data.marker_reference import canonical_name as resolve_canonical

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Unit alias map — string-only normalization, no value conversion
# ---------------------------------------------------------------------------
_UNIT_ALIASES: dict[str, str] = {
    # mg variants
    "mg/dl": "mg/dL",
    "mg/DL": "mg/dL",
    # g variants
    "g/dl": "g/dL",
    "g/DL": "g/dL",
    # IU variants
    "iu/ml": "IU/mL",
    "IU/ml": "IU/mL",
    "u/ml": "IU/mL",
    "U/mL": "IU/mL",
    # µg variants
    "ug/dl": "µg/dL",
    "ug/dL": "µg/dL",
    "µg/dl": "µg/dL",
    "mcg/dL": "µg/dL",
    # ng variants
    "ng/ml": "ng/mL",
    "ng/ML": "ng/mL",
    # pmol
    "pmol/l": "pmol/L",
    # mmol
    "mmol/l": "mmol/L",
    # U/L
    "u/l": "U/L",
    "U/l": "U/L",
    # fL
    "fl": "fL",
    "FL": "fL",
    # µIU/mL (TSH)
    "uiu/ml": "µIU/mL",
    "uIU/ml": "µIU/mL",
    "uIU/mL": "µIU/mL",
    "µIU/ml": "µIU/mL",
    # mIU variants
    "miu/ml": "mIU/mL",
    "mIU/ml": "mIU/mL",
    "miu/L": "mIU/L",
    # Cell counts
    "million/ul": "million/µL",
    "million/uL": "million/µL",
    "10^6/ul": "million/µL",
    "10^6/µL": "million/µL",
    "thousand/ul": "thousand/µL",
    "thousand/uL": "thousand/µL",
    "10^3/ul": "thousand/µL",
    "10^3/uL": "thousand/µL",
    # Percentage — already canonical
}

# ---------------------------------------------------------------------------
# Physiologically plausible ranges — used to flag obvious data-entry errors
# { canonical_name: (absolute_min, absolute_max) }
# ---------------------------------------------------------------------------
_PLAUSIBLE: dict[str, tuple[float, float]] = {
    "Hemoglobin": (2.0, 25.0),
    "Fasting Glucose": (20.0, 800.0),
    "HbA1c": (3.0, 20.0),
    "TSH": (0.0, 500.0),
    "Free T3": (0.5, 20.0),
    "Free T4": (0.1, 10.0),
    "Vitamin D": (0.0, 300.0),
    "Vitamin B12": (0.0, 10000.0),
    "Total Cholesterol": (50.0, 700.0),
    "Triglycerides": (10.0, 5000.0),
    "LDL": (10.0, 500.0),
    "HDL": (5.0, 200.0),
    "VLDL": (1.0, 500.0),
    "Creatinine": (0.1, 30.0),
    "ALT": (0.0, 3000.0),
    "AST": (0.0, 3000.0),
    "Uric Acid": (0.5, 20.0),
    "Calcium": (4.0, 16.0),
    "Magnesium": (0.5, 5.0),
    "Ferritin": (0.5, 15000.0),
    "Testosterone": (1.0, 2000.0),
    "CRP": (0.0, 500.0),
}


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------
@dataclass
class NormalizationResult:
    markers: list[ExtractedMarker] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def normalize_markers(markers: list[ExtractedMarker]) -> NormalizationResult:
    """Normalize names and units, deduplicate, and flag suspicious values.

    Returns:
        NormalizationResult with cleaned markers and any warnings.
    """
    warnings: list[str] = []
    step1: list[ExtractedMarker] = []

    for m in markers:
        cleaned, w = _normalize_single(m)
        step1.append(cleaned)
        warnings.extend(w)

    deduped, dedup_w = _deduplicate(step1)
    warnings.extend(dedup_w)

    return NormalizationResult(markers=deduped, warnings=warnings)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _normalize_single(m: ExtractedMarker) -> tuple[ExtractedMarker, list[str]]:
    warnings: list[str] = []

    # 1. Resolve canonical name
    canon = resolve_canonical(m.name)
    if canon != m.name:
        logger.debug("Name alias: %r → %r", m.name, canon)

    # 2. Normalize unit string
    norm_unit = _UNIT_ALIASES.get(m.unit, m.unit)
    if norm_unit != m.unit:
        logger.debug("Unit alias: %r → %r", m.unit, norm_unit)

    # 3. Check physiological plausibility
    if m.value is not None:
        bounds = _PLAUSIBLE.get(canon)
        if bounds and not (bounds[0] <= m.value <= bounds[1]):
            warnings.append(
                f"Suspicious value for '{m.reported_name}': {m.value} {m.unit} "
                f"(plausible range {bounds[0]}–{bounds[1]}). Please verify."
            )

    updated = m.model_copy(update={"name": canon, "unit": norm_unit})
    return updated, warnings


def _deduplicate(
    markers: list[ExtractedMarker],
) -> tuple[list[ExtractedMarker], list[str]]:
    """Collapse duplicates (same canonical name) keeping the more complete entry."""
    warnings: list[str] = []
    seen: dict[str, ExtractedMarker] = {}

    for m in markers:
        key = m.name.lower()
        if key not in seen:
            seen[key] = m
            continue

        existing = seen[key]
        if _completeness(m) > _completeness(existing):
            seen[key] = m

        warnings.append(
            f"Duplicate marker '{m.reported_name}' (canonical: '{m.name}') — "
            "kept the more complete entry."
        )

    return list(seen.values()), warnings


def _completeness(m: ExtractedMarker) -> int:
    """Higher score = more populated fields."""
    return sum([
        m.value is not None,
        m.reference_low is not None,
        m.reference_high is not None,
        m.qualitative_value is not None,
        bool(m.unit),
    ])
