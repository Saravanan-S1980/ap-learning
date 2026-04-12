"""Step 2 of the analysis chain: flag markers against reference and optimal ranges.

Flow:
    normalized markers
    → Python: compare each marker against lab_range and optimal_range
               from marker_reference.py (fast, deterministic)
    → Claude Haiku: assess clinical significance for out-of-range markers
               in a single batched API call
    → FlaggingResult
"""
from __future__ import annotations

import json
import logging
from typing import Literal

from app.data.marker_reference import MarkerRef, lookup
from app.models.markers import ExtractedMarker, FlaggedMarker, FlaggingResult
from app.utils.claude_client import HAIKU_MODEL, call_claude_json
from app.utils.prompts import FLAGGING_SYSTEM, FLAGGING_USER_TEMPLATE

logger = logging.getLogger(__name__)

_FLAGGING_MAX_TOKENS = 2048

LabStatus = Literal["normal", "low", "high"]
OptimalStatus = Literal["optimal", "suboptimal_low", "suboptimal_high"]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def flag_markers(markers: list[ExtractedMarker]) -> FlaggingResult:
    """Compare markers against lab and optimal ranges, then enrich with Claude.

    Args:
        markers: Normalized list from marker_normalizer.normalize_markers().

    Returns:
        FlaggingResult separating flagged from normal markers, with Claude
        severity and clinical notes for each flagged marker.
    """
    warnings: list[str] = []

    # ── Step 2a: pure-Python range comparison ───────────────────────────────
    needs_assessment: list[_PendingFlag] = []
    normal: list[ExtractedMarker] = []

    for m in markers:
        ref = lookup(m.name)
        lab_status = _lab_status(m, ref)
        optimal_status = _optimal_status(m, ref)
        retest_weeks = ref.retest_interval_weeks if ref else 12

        if ref is None:
            warnings.append(
                f"Marker '{m.name}' has no reference data — using extraction flag only."
            )

        is_out_of_lab = lab_status != "normal"
        is_suboptimal = optimal_status != "optimal"

        if is_out_of_lab or is_suboptimal:
            needs_assessment.append(
                _PendingFlag(
                    marker=m,
                    ref=ref,
                    lab_status=lab_status,
                    optimal_status=optimal_status,
                    retest_weeks=retest_weeks,
                )
            )
        else:
            normal.append(m)

    if not needs_assessment:
        return FlaggingResult(flagged_markers=[], normal_markers=normal, warnings=warnings)

    # ── Step 2b: Claude clinical-significance assessment (batched) ───────────
    assessments, claude_warnings = await _assess_with_claude(needs_assessment)
    warnings.extend(claude_warnings)

    flagged: list[FlaggedMarker] = []
    for pf in needs_assessment:
        asmt = assessments.get(pf.marker.name, {})
        flagged.append(
            FlaggedMarker(
                marker=pf.marker,
                canonical_name=pf.marker.name,
                lab_status=pf.lab_status,
                optimal_status=pf.optimal_status,
                severity=asmt.get("severity", _default_severity(pf.lab_status, pf.optimal_status)),
                clinical_notes=asmt.get("clinical_notes", ""),
                related_markers=asmt.get("related_markers", []),
                retest_weeks=pf.retest_weeks,
            )
        )

    return FlaggingResult(
        flagged_markers=flagged,
        normal_markers=normal,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Internal types and helpers
# ---------------------------------------------------------------------------
class _PendingFlag:
    __slots__ = ("marker", "ref", "lab_status", "optimal_status", "retest_weeks")

    def __init__(
        self,
        marker: ExtractedMarker,
        ref: MarkerRef | None,
        lab_status: LabStatus,
        optimal_status: OptimalStatus,
        retest_weeks: int,
    ) -> None:
        self.marker = marker
        self.ref = ref
        self.lab_status = lab_status
        self.optimal_status = optimal_status
        self.retest_weeks = retest_weeks


def _lab_status(m: ExtractedMarker, ref: MarkerRef | None) -> LabStatus:
    """Compare marker value against lab reference range."""
    if m.value is None:
        # Qualitative: trust the extraction flag
        if m.flag in ("high", "critical_high"):
            return "high"
        if m.flag in ("low", "critical_low"):
            return "low"
        return "normal"

    if ref is None:
        # No reference DB entry — fall back to extraction flag
        if m.flag in ("high", "critical_high"):
            return "high"
        if m.flag in ("low", "critical_low"):
            return "low"
        return "normal"

    if ref.lab_low is not None and m.value < ref.lab_low:
        return "low"
    if ref.lab_high is not None and m.value > ref.lab_high:
        return "high"
    return "normal"


def _optimal_status(m: ExtractedMarker, ref: MarkerRef | None) -> OptimalStatus:
    """Compare marker value against evidence-based optimal range."""
    if m.value is None or ref is None:
        return "optimal"  # can't assess without numeric value or reference

    if ref.optimal_low is not None and m.value < ref.optimal_low:
        return "suboptimal_low"
    if ref.optimal_high is not None and m.value > ref.optimal_high:
        return "suboptimal_high"
    return "optimal"


def _default_severity(
    lab_status: LabStatus,
    optimal_status: OptimalStatus,
) -> Literal["normal", "mild", "moderate", "significant"]:
    """Fallback severity if Claude call fails."""
    if lab_status != "normal":
        return "moderate"
    if optimal_status != "optimal":
        return "mild"
    return "normal"


def _build_claude_payload(pending: list[_PendingFlag]) -> list[dict]:
    """Build the JSON array sent to Claude for clinical assessment."""
    items = []
    for pf in pending:
        m = pf.marker
        ref = pf.ref
        item: dict = {
            "canonical_name": m.name,
            "value": m.value,
            "qualitative_value": m.qualitative_value,
            "unit": m.unit,
            "lab_status": pf.lab_status,
            "optimal_status": pf.optimal_status,
            "lab_range": {
                "low": ref.lab_low if ref else None,
                "high": ref.lab_high if ref else None,
            },
            "optimal_range": {
                "low": ref.optimal_low if ref else None,
                "high": ref.optimal_high if ref else None,
            },
        }
        items.append(item)
    return items


async def _assess_with_claude(
    pending: list[_PendingFlag],
) -> tuple[dict[str, dict], list[str]]:
    """Call Claude once for all flagged markers.

    Returns:
        (dict of canonical_name → assessment dict, warnings list)
    """
    payload = _build_claude_payload(pending)
    user_prompt = FLAGGING_USER_TEMPLATE.format(markers_json=json.dumps(payload, indent=2))

    raw = await call_claude_json(
        model=HAIKU_MODEL,
        system=FLAGGING_SYSTEM,
        user=user_prompt,
        max_tokens=_FLAGGING_MAX_TOKENS,
    )

    claude_warnings: list[str] = list(raw.get("warnings") or [])
    assessments: dict[str, dict] = {}

    for asmt in raw.get("assessments") or []:
        name = asmt.get("canonical_name")
        if not name:
            continue
        # Validate severity value
        severity = asmt.get("severity", "mild")
        if severity not in ("normal", "mild", "moderate", "significant"):
            logger.warning("Unknown severity %r for %r — defaulting to 'mild'", severity, name)
            severity = "mild"
        assessments[name] = {
            "severity": severity,
            "clinical_notes": asmt.get("clinical_notes", ""),
            "related_markers": asmt.get("related_markers") or [],
        }

    return assessments, claude_warnings
