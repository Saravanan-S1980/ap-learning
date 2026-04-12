"""Step 3 of the analysis chain: cross-reference flagged markers with user goals.

Pure Python — no Claude API call.

Flow:
    flagged_markers + selected_goals
    → match each goal's relevant_markers against the flagged list
    → deduplicate across goals, sort by severity
    → CrossRefResult (used as context for protocol generation)
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.models.markers import FlaggedMarker
from app.data.goals import GOALS, Goal, get_goal

# Severity sort order — lower number = higher priority
_SEVERITY_ORDER: dict[str, int] = {
    "significant": 0,
    "moderate": 1,
    "mild": 2,
    "normal": 3,
}


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class GoalMarkerGroup:
    """Flagged markers that are relevant to a single goal."""
    goal: Goal
    flagged_markers: list[FlaggedMarker] = field(default_factory=list)


@dataclass
class CrossRefResult:
    """Output of cross-referencing markers against user goals."""
    goal_groups: list[GoalMarkerGroup]
    priority_markers: list[FlaggedMarker]   # deduplicated, sorted by severity
    selected_goals: list[str]               # goal IDs the user chose
    unrecognized_goals: list[str]           # goal IDs that didn't match any definition
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def crossref_goals(
    flagged_markers: list[FlaggedMarker],
    selected_goals: list[str],
) -> CrossRefResult:
    """Map flagged markers to selected goals and produce a prioritized list.

    Args:
        flagged_markers: Output of flag_markers() — markers outside lab/optimal range.
        selected_goals:  List of goal IDs chosen by the user (1–3 typically).

    Returns:
        CrossRefResult with per-goal groupings and a flat priority list.
    """
    warnings: list[str] = []
    unrecognized: list[str] = []
    goal_groups: list[GoalMarkerGroup] = []

    # Track seen canonical names so we deduplicate across goals
    seen: set[str] = set()
    priority_markers: list[FlaggedMarker] = []

    for goal_id in selected_goals:
        goal = get_goal(goal_id)
        if goal is None:
            unrecognized.append(goal_id)
            warnings.append(
                f"Goal '{goal_id}' is not recognized — skipping. "
                f"Available goals: {', '.join(GOALS.keys())}"
            )
            continue

        # Match flagged markers against this goal's relevant_markers list
        relevant = [
            fm for fm in flagged_markers
            if fm.canonical_name in goal.relevant_markers
        ]
        relevant.sort(key=lambda fm: _SEVERITY_ORDER.get(fm.severity, 99))
        goal_groups.append(GoalMarkerGroup(goal=goal, flagged_markers=relevant))

        # Accumulate into deduplicated priority list
        for fm in relevant:
            if fm.canonical_name not in seen:
                seen.add(fm.canonical_name)
                priority_markers.append(fm)

    # Also include significant/moderate flagged markers not matched to any goal
    # (so the protocol generator still sees them)
    for fm in flagged_markers:
        if fm.canonical_name not in seen and fm.severity in ("significant", "moderate"):
            priority_markers.append(fm)
            seen.add(fm.canonical_name)

    # Final sort by severity
    priority_markers.sort(key=lambda fm: _SEVERITY_ORDER.get(fm.severity, 99))

    if not goal_groups:
        warnings.append("No recognized goals were provided; protocol will address all flagged markers.")

    return CrossRefResult(
        goal_groups=goal_groups,
        priority_markers=priority_markers,
        selected_goals=selected_goals,
        unrecognized_goals=unrecognized,
        warnings=warnings,
    )
