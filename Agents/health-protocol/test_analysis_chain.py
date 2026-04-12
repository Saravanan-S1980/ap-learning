"""Quick integration test for analysis chain steps 1 & 2.

Uses the 12 markers extracted from the real Apollo Health report
(LabTest_06Nov2025.pdf) in the previous session.

Run from the project root:
    cd backend && python ../test_analysis_chain.py
"""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")  # Windows: prevent cp1252 encode errors

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.models.markers import ExtractedMarker
from app.services.marker_normalizer import normalize_markers
from app.services.marker_flagger import flag_markers

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


def print_section(title: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)


async def main() -> None:
    print("\n" + "=" * 60)
    print("  ANALYSIS CHAIN — Steps 1 & 2")
    print("=" * 60)

    # ── STEP 1: Normalize ────────────────────────────────────────────────────
    print_section("STEP 1 — Normalization")
    norm_result = normalize_markers(RAW_MARKERS)

    print(f"Input markers : {len(RAW_MARKERS)}")
    print(f"After dedup   : {len(norm_result.markers)}")
    if norm_result.warnings:
        print("Warnings:")
        for w in norm_result.warnings:
            print(f"  ⚠  {w}")
    else:
        print("No warnings.")

    print("\nNormalized markers:")
    for m in norm_result.markers:
        val = f"{m.value} {m.unit}" if m.value is not None else m.qualitative_value
        print(f"  {m.name:<30} {str(val):<20} [{m.flag}]")

    # ── STEP 2: Flag ─────────────────────────────────────────────────────────
    print_section("STEP 2 — Flagging (Claude assessment)")
    print("Calling Claude Haiku for clinical significance...\n")

    flag_result = await flag_markers(norm_result.markers)

    print(f"Flagged markers : {len(flag_result.flagged_markers)}")
    print(f"Normal markers  : {len(flag_result.normal_markers)}")

    if flag_result.warnings:
        print("\nWarnings:")
        for w in flag_result.warnings:
            print(f"  ⚠  {w}")

    if flag_result.normal_markers:
        print("\nNORMAL (within optimal range):")
        for m in flag_result.normal_markers:
            val = f"{m.value} {m.unit}" if m.value is not None else m.qualitative_value
            print(f"  ✓  {m.name:<30} {val}")

    if flag_result.flagged_markers:
        severity_icons = {
            "normal": "✓",
            "mild": "⚡",
            "moderate": "⚠",
            "significant": "🔴",
        }
        print("\nFLAGGED MARKERS:")
        for fm in flag_result.flagged_markers:
            m = fm.marker
            val = f"{m.value} {m.unit}" if m.value is not None else m.qualitative_value
            icon = severity_icons.get(fm.severity, "?")
            print(f"\n  {icon}  {fm.canonical_name}")
            print(f"     Value      : {val}")
            print(f"     Lab status : {fm.lab_status}   |   Optimal: {fm.optimal_status}")
            print(f"     Severity   : {fm.severity.upper()}")
            if fm.clinical_notes:
                print(f"     Notes      : {fm.clinical_notes}")
            if fm.related_markers:
                print(f"     Watch also : {', '.join(fm.related_markers)}")
            print(f"     Retest in  : {fm.retest_weeks} weeks")

    print("\n" + "=" * 60)
    print("  Done.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
