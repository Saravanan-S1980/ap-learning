"""Step 4 of the analysis chain: generate a personalized health protocol.

Flow:
    flagged_markers + CrossRefResult + goals
    → Claude Sonnet (single call, max 4096 tokens)
    → Protocol (diet, supplements, lifestyle, retest schedule)
"""
from __future__ import annotations

import json
import logging

from app.models.markers import FlaggedMarker
from app.models.protocol import (
    DietChange,
    LifestyleChange,
    Protocol,
    RetestItem,
    SupplementRecommendation,
)
from app.services.goal_crossref import CrossRefResult
from app.utils.claude_client import SONNET_MODEL, call_claude_json
from app.utils.prompts import PROTOCOL_SYSTEM, PROTOCOL_USER_TEMPLATE

logger = logging.getLogger(__name__)

_PROTOCOL_MAX_TOKENS = 4096


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def generate_protocol(
    flagged_markers: list[FlaggedMarker],
    crossref: CrossRefResult,
    goals: list[str],
    extraction_id: str = "",
) -> Protocol:
    """Generate a full health protocol using Claude Sonnet.

    Args:
        flagged_markers: All markers outside lab or optimal range (Step 2 output).
        crossref:        Goal-to-marker mapping (Step 3 output).
        goals:           User's selected goal IDs.
        extraction_id:   Source extraction identifier (for traceability).

    Returns:
        Protocol with diet, supplements, lifestyle, and retest sections.
    """
    warnings: list[str] = list(crossref.warnings)

    if crossref.unrecognized_goals:
        logger.warning("Unrecognized goals: %s", crossref.unrecognized_goals)

    # Build the marker payload for Claude
    flagged_payload = [
        {
            "canonical_name": fm.canonical_name,
            "value": fm.marker.value,
            "unit": fm.marker.unit,
            "lab_status": fm.lab_status,
            "optimal_status": fm.optimal_status,
            "severity": fm.severity,
            "clinical_notes": fm.clinical_notes,
            "related_markers": fm.related_markers,
            "retest_weeks": fm.retest_weeks,
        }
        for fm in flagged_markers
    ]

    crossref_payload = {
        "selected_goals": crossref.selected_goals,
        "goal_groups": [
            {
                "goal_id": gg.goal.id,
                "goal_name": gg.goal.display_name,
                "relevant_flagged_markers": [fm.canonical_name for fm in gg.flagged_markers],
            }
            for gg in crossref.goal_groups
        ],
        "priority_markers": [fm.canonical_name for fm in crossref.priority_markers],
    }

    user_prompt = PROTOCOL_USER_TEMPLATE.format(
        flagged_markers=json.dumps(flagged_payload, indent=2),
        goals=json.dumps(goals),
        crossref=json.dumps(crossref_payload, indent=2),
    )

    try:
        raw = await call_claude_json(
            model=SONNET_MODEL,
            system=PROTOCOL_SYSTEM,
            user=user_prompt,
            max_tokens=_PROTOCOL_MAX_TOKENS,
        )
    except (RuntimeError, ValueError) as exc:
        logger.error("Protocol generation failed: %s", exc)
        warnings.append(f"Protocol generation error: {exc}")
        return Protocol(
            extraction_id=extraction_id,
            goals=goals,
            warnings=warnings,
        )

    diet_changes = [
        DietChange(
            action=d.get("action", ""),
            rationale=d.get("rationale", ""),
            phase=d.get("phase", "immediate"),
            targets=d.get("targets") or [],
        )
        for d in (raw.get("diet_changes") or [])
        if d.get("action")
    ]

    supplements = [
        SupplementRecommendation(
            name=s.get("name", ""),
            dose=s.get("dose", ""),
            timing=s.get("timing", ""),
            duration_weeks=int(s.get("duration_weeks") or 12),
            targets=s.get("targets") or [],
            notes=s.get("notes", ""),
        )
        for s in (raw.get("supplements") or [])
        if s.get("name")
    ]

    lifestyle_changes = [
        LifestyleChange(
            action=lc.get("action", ""),
            frequency=lc.get("frequency", "daily"),
            rationale=lc.get("rationale", ""),
            targets=lc.get("targets") or [],
        )
        for lc in (raw.get("lifestyle_changes") or [])
        if lc.get("action")
    ]

    retest_schedule = [
        RetestItem(
            marker=r.get("marker", ""),
            weeks_from_now=int(r.get("weeks_from_now") or 12),
            reason=r.get("reason", ""),
        )
        for r in (raw.get("retest_schedule") or [])
        if r.get("marker")
    ]

    return Protocol(
        extraction_id=extraction_id,
        goals=goals,
        diet_changes=diet_changes,
        supplements=supplements,
        lifestyle_changes=lifestyle_changes,
        retest_schedule=retest_schedule,
        warnings=warnings,
    )
