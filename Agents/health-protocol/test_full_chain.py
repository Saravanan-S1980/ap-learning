"""Full 4-step analysis chain integration test.

Uses the 12 markers extracted from the real Apollo Health report
(LabTest_06Nov2025.pdf) with goals: cardiovascular_health + energy_vitality.

Run from the project root:
    python test_full_chain.py
"""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")  # Windows: prevent cp1252 encode errors

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.models.markers import ExtractedMarker
from app.services.marker_normalizer import normalize_markers
from app.services.marker_flagger import flag_markers
from app.services.goal_crossref import crossref_goals
from app.services.protocol_generator import generate_protocol

# ── Apollo Health report markers (verbatim from extraction) ─────────────────
RAW_MARKERS = [
    ExtractedMarker(name="Total Cholesterol", reported_name="Total Cholesterol",
                    value=180.0, unit="mg/dL", reference_low=None, reference_high=200.0,
                    flag="normal", category="Lipid"),
    ExtractedMarker(name="Triglycerides", reported_name="Triglycerides",
                    value=225.0, unit="mg/dL", reference_low=None, reference_high=150.0,
                    flag="high", category="Lipid"),
    ExtractedMarker(name="HDL", reported_name="HDL Cholesterol",
                    value=42.0, unit="mg/dL", reference_low=40.0, reference_high=None,
                    flag="normal", category="Lipid"),
    ExtractedMarker(name="Non-HDL Cholesterol", reported_name="Non-HDL Cholesterol",
                    value=138.0, unit="mg/dL", reference_low=None, reference_high=130.0,
                    flag="high", category="Lipid"),
    ExtractedMarker(name="LDL", reported_name="LDL Cholesterol",
                    value=92.9, unit="mg/dL", reference_low=None, reference_high=130.0,
                    flag="normal", category="Lipid"),
    ExtractedMarker(name="VLDL", reported_name="VLDL Cholesterol",
                    value=45.0, unit="mg/dL", reference_low=None, reference_high=30.0,
                    flag="high", category="Lipid"),
    ExtractedMarker(name="Chol/HDL Ratio", reported_name="Chol/HDL Ratio",
                    value=4.28, unit="ratio", reference_low=None, reference_high=5.0,
                    flag="normal", category="Lipid"),
    ExtractedMarker(name="Atherogenic Index", reported_name="Atherogenic Index",
                    value=0.37, unit="ratio", reference_low=None, reference_high=0.24,
                    flag="high", category="Lipid"),
    ExtractedMarker(name="Calcium", reported_name="Calcium",
                    value=9.74, unit="mg/dL", reference_low=8.5, reference_high=10.5,
                    flag="normal", category="Mineral"),
    ExtractedMarker(name="Vitamin D", reported_name="25-OH Vitamin D",
                    value=57.9, unit="ng/mL", reference_low=30.0, reference_high=100.0,
                    flag="normal", category="Vitamin"),
    ExtractedMarker(name="Vitamin B12", reported_name="Vitamin B12",
                    value=625.0, unit="pg/mL", reference_low=211.0, reference_high=911.0,
                    flag="normal", category="Vitamin"),
    ExtractedMarker(name="Testosterone", reported_name="Testosterone",
                    value=344.0, unit="ng/dL", reference_low=300.0, reference_high=1000.0,
                    flag="normal", category="Hormone"),
]

SELECTED_GOALS = ["cardiovascular_health", "energy_vitality"]


def section(title: str) -> None:
    print(f"\n{'═' * 62}")
    print(f"  {title}")
    print('═' * 62)


def subsection(title: str) -> None:
    print(f"\n  {'─' * 56}")
    print(f"  {title}")
    print(f"  {'─' * 56}")


async def main() -> None:
    print("\n" + "=" * 62)
    print("  FULL ANALYSIS CHAIN — Steps 1–4")
    print(f"  Goals: {', '.join(SELECTED_GOALS)}")
    print("=" * 62)

    # ── STEP 1: Normalize ────────────────────────────────────────────────────
    section("STEP 1 — Normalization")
    norm = normalize_markers(RAW_MARKERS)
    print(f"  Input   : {len(RAW_MARKERS)} markers")
    print(f"  Output  : {len(norm.markers)} markers")
    if norm.warnings:
        for w in norm.warnings:
            print(f"  ⚠  {w}")
    else:
        print("  No warnings.")

    # ── STEP 2: Flag ─────────────────────────────────────────────────────────
    section("STEP 2 — Clinical Flagging (Claude Haiku)")
    flag_result = await flag_markers(norm.markers)
    print(f"  Flagged : {len(flag_result.flagged_markers)}")
    print(f"  Normal  : {len(flag_result.normal_markers)}")

    if flag_result.warnings:
        for w in flag_result.warnings:
            print(f"  ⚠  {w}")

    severity_icons = {"normal": "✓", "mild": "⚡", "moderate": "⚠", "significant": "🔴"}
    for fm in flag_result.flagged_markers:
        icon = severity_icons.get(fm.severity, "?")
        val = f"{fm.marker.value} {fm.marker.unit}" if fm.marker.value is not None else fm.marker.qualitative_value
        print(f"  {icon}  {fm.canonical_name:<30} {str(val):<18}  [{fm.severity.upper()}]")

    # ── STEP 3: Cross-reference ───────────────────────────────────────────────
    section("STEP 3 — Goal Cross-Reference")
    crossref = crossref_goals(flag_result.flagged_markers, SELECTED_GOALS)

    if crossref.warnings:
        for w in crossref.warnings:
            print(f"  ⚠  {w}")

    for gg in crossref.goal_groups:
        names = [fm.canonical_name for fm in gg.flagged_markers]
        print(f"\n  {gg.goal.emoji}  {gg.goal.display_name}:")
        if names:
            for n in names:
                print(f"       • {n}")
        else:
            print("       (no flagged markers match this goal)")

    print(f"\n  Priority list ({len(crossref.priority_markers)} markers):")
    for fm in crossref.priority_markers:
        icon = severity_icons.get(fm.severity, "?")
        print(f"  {icon}  {fm.canonical_name}")

    # ── STEP 4: Generate Protocol ─────────────────────────────────────────────
    section("STEP 4 — Protocol Generation (Claude Sonnet)")
    print("  Calling Claude Sonnet...\n")
    protocol = await generate_protocol(
        flagged_markers=flag_result.flagged_markers,
        crossref=crossref,
        goals=SELECTED_GOALS,
        extraction_id="apollo_test_session",
    )

    if protocol.warnings:
        for w in protocol.warnings:
            print(f"  ⚠  {w}")

    # Diet
    subsection("🥗  DIET CHANGES")
    immediate = [d for d in protocol.diet_changes if d.phase == "immediate"]
    phase_in  = [d for d in protocol.diet_changes if d.phase == "phase_in"]

    if immediate:
        print("  START NOW:")
        for d in immediate:
            print(f"  • {d.action}")
            if d.rationale:
                print(f"    ↳ {d.rationale}")
    if phase_in:
        print("\n  PHASE IN (2–4 weeks):")
        for d in phase_in:
            print(f"  • {d.action}")
            if d.rationale:
                print(f"    ↳ {d.rationale}")

    # Supplements
    subsection("💊  SUPPLEMENTS")
    for s in protocol.supplements:
        print(f"  • {s.name}  |  {s.dose}  |  {s.timing}  |  {s.duration_weeks}w")
        if s.targets:
            print(f"    Targets: {', '.join(s.targets)}")
        if s.notes:
            print(f"    Note: {s.notes}")

    # Lifestyle
    subsection("🏃  LIFESTYLE")
    for lc in protocol.lifestyle_changes:
        print(f"  • {lc.action}  [{lc.frequency}]")
        if lc.rationale:
            print(f"    ↳ {lc.rationale}")

    # Retest
    subsection("📅  RETEST SCHEDULE")
    for r in protocol.retest_schedule:
        print(f"  • {r.marker:<30} in {r.weeks_from_now:>2}w  —  {r.reason}")

    # Disclaimer
    print(f"\n  ⚕  {protocol.disclaimer}")

    print("\n" + "=" * 62)
    print("  Done.")
    print("=" * 62 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
