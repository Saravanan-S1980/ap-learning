"""Reference database for common biomarkers.

Each entry maps a canonical marker name to its reference data.
lab_range   — typical laboratory reference interval (population-based)
optimal_range — evidence-based optimal for long-term health
All ranges are (low, high); use None where one-sided.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MarkerRef:
    unit: str
    lab_low: float | None
    lab_high: float | None
    optimal_low: float | None
    optimal_high: float | None
    category: str
    dietary_sources: list[str] = field(default_factory=list)
    supplement_forms: list[str] = field(default_factory=list)
    interactions: list[str] = field(default_factory=list)   # related canonical names
    retest_interval_weeks: int = 12


# ---------------------------------------------------------------------------
# Reference data — 30 markers common in Indian lab reports
# ---------------------------------------------------------------------------
MARKER_REFERENCE: dict[str, MarkerRef] = {

    # ── CBC ─────────────────────────────────────────────────────────────────
    "Hemoglobin": MarkerRef(
        unit="g/dL",
        lab_low=12.0, lab_high=17.5,
        optimal_low=13.5, optimal_high=16.5,
        category="CBC",
        dietary_sources=["red meat", "spinach", "lentils", "tofu", "pumpkin seeds"],
        supplement_forms=["ferrous sulfate", "ferrous bisglycinate", "iron polysaccharide"],
        interactions=["Serum Iron", "Ferritin", "TIBC", "RBC Count"],
        retest_interval_weeks=8,
    ),
    "RBC Count": MarkerRef(
        unit="million/µL",
        lab_low=3.8, lab_high=5.8,
        optimal_low=4.2, optimal_high=5.4,
        category="CBC",
        dietary_sources=["iron-rich foods", "vitamin B12 sources"],
        supplement_forms=["iron", "B12", "folate"],
        interactions=["Hemoglobin", "Hematocrit", "MCV"],
        retest_interval_weeks=8,
    ),
    "Hematocrit": MarkerRef(
        unit="%",
        lab_low=36.0, lab_high=52.0,
        optimal_low=39.0, optimal_high=48.0,
        category="CBC",
        dietary_sources=["iron-rich foods"],
        supplement_forms=["iron", "B12", "folate"],
        interactions=["Hemoglobin", "RBC Count"],
        retest_interval_weeks=8,
    ),
    "MCV": MarkerRef(
        unit="fL",
        lab_low=80.0, lab_high=100.0,
        optimal_low=82.0, optimal_high=96.0,
        category="CBC",
        dietary_sources=["B12 sources", "folate-rich foods"],
        supplement_forms=["B12", "folate"],
        interactions=["Hemoglobin", "RBC Count", "Vitamin B12"],
        retest_interval_weeks=12,
    ),
    "WBC Count": MarkerRef(
        unit="thousand/µL",
        lab_low=4.0, lab_high=11.0,
        optimal_low=5.0, optimal_high=8.0,
        category="CBC",
        dietary_sources=["zinc-rich foods", "vitamin C sources"],
        supplement_forms=["zinc", "vitamin C", "vitamin D"],
        interactions=["Neutrophils", "Lymphocytes", "CRP"],
        retest_interval_weeks=12,
    ),
    "Platelet Count": MarkerRef(
        unit="thousand/µL",
        lab_low=150.0, lab_high=400.0,
        optimal_low=180.0, optimal_high=350.0,
        category="CBC",
        dietary_sources=["leafy greens", "foods rich in vitamin K"],
        supplement_forms=["vitamin K2", "omega-3"],
        interactions=["WBC Count"],
        retest_interval_weeks=12,
    ),

    # ── Lipid Panel ─────────────────────────────────────────────────────────
    "Total Cholesterol": MarkerRef(
        unit="mg/dL",
        lab_low=None, lab_high=200.0,
        optimal_low=None, optimal_high=180.0,
        category="Lipid",
        dietary_sources=["oats", "legumes", "nuts", "olive oil"],
        supplement_forms=["red yeast rice", "berberine", "omega-3", "plant sterols"],
        interactions=["LDL", "HDL", "Triglycerides", "Non-HDL Cholesterol"],
        retest_interval_weeks=12,
    ),
    "LDL": MarkerRef(
        unit="mg/dL",
        lab_low=None, lab_high=130.0,
        optimal_low=None, optimal_high=100.0,
        category="Lipid",
        dietary_sources=["soluble fiber", "oats", "avocado", "olive oil"],
        supplement_forms=["berberine", "red yeast rice", "plant sterols", "omega-3"],
        interactions=["Total Cholesterol", "HDL", "Triglycerides", "Atherogenic Index"],
        retest_interval_weeks=12,
    ),
    "HDL": MarkerRef(
        unit="mg/dL",
        lab_low=40.0, lab_high=None,
        optimal_low=50.0, optimal_high=None,
        category="Lipid",
        dietary_sources=["olive oil", "nuts", "fatty fish", "avocado"],
        supplement_forms=["niacin", "omega-3", "pantethine"],
        interactions=["Total Cholesterol", "LDL", "Triglycerides"],
        retest_interval_weeks=12,
    ),
    "Triglycerides": MarkerRef(
        unit="mg/dL",
        lab_low=None, lab_high=150.0,
        optimal_low=None, optimal_high=100.0,
        category="Lipid",
        dietary_sources=["fatty fish", "flaxseed", "walnuts"],
        supplement_forms=["omega-3 (EPA/DHA)", "berberine", "niacin"],
        interactions=["HDL", "VLDL", "Total Cholesterol", "Atherogenic Index"],
        retest_interval_weeks=12,
    ),
    "VLDL": MarkerRef(
        unit="mg/dL",
        lab_low=None, lab_high=30.0,
        optimal_low=None, optimal_high=20.0,
        category="Lipid",
        dietary_sources=["low-sugar diet", "fatty fish"],
        supplement_forms=["omega-3", "berberine"],
        interactions=["Triglycerides", "LDL"],
        retest_interval_weeks=12,
    ),
    "Non-HDL Cholesterol": MarkerRef(
        unit="mg/dL",
        lab_low=None, lab_high=160.0,
        optimal_low=None, optimal_high=130.0,
        category="Lipid",
        dietary_sources=["soluble fiber", "plant sterols"],
        supplement_forms=["berberine", "omega-3", "plant sterols"],
        interactions=["LDL", "VLDL", "Total Cholesterol"],
        retest_interval_weeks=12,
    ),

    # ── Thyroid ─────────────────────────────────────────────────────────────
    "TSH": MarkerRef(
        unit="µIU/mL",
        lab_low=0.4, lab_high=4.5,
        optimal_low=0.5, optimal_high=2.5,
        category="Thyroid",
        dietary_sources=["iodized salt", "seafood", "dairy", "eggs"],
        supplement_forms=["iodine", "selenium", "zinc", "ashwagandha"],
        interactions=["Free T3", "Free T4"],
        retest_interval_weeks=12,
    ),
    "Free T3": MarkerRef(
        unit="pg/mL",
        lab_low=2.3, lab_high=4.2,
        optimal_low=3.0, optimal_high=4.0,
        category="Thyroid",
        dietary_sources=["selenium-rich foods", "zinc sources"],
        supplement_forms=["selenium", "zinc", "iodine"],
        interactions=["TSH", "Free T4"],
        retest_interval_weeks=12,
    ),
    "Free T4": MarkerRef(
        unit="ng/dL",
        lab_low=0.8, lab_high=1.8,
        optimal_low=1.0, optimal_high=1.6,
        category="Thyroid",
        dietary_sources=["iodized salt", "seafood"],
        supplement_forms=["iodine", "selenium"],
        interactions=["TSH", "Free T3"],
        retest_interval_weeks=12,
    ),

    # ── Liver ────────────────────────────────────────────────────────────────
    "ALT": MarkerRef(
        unit="U/L",
        lab_low=None, lab_high=56.0,
        optimal_low=None, optimal_high=30.0,
        category="Liver",
        dietary_sources=["coffee", "cruciferous vegetables", "garlic"],
        supplement_forms=["milk thistle (silymarin)", "NAC", "alpha-lipoic acid"],
        interactions=["AST", "GGT", "Total Bilirubin"],
        retest_interval_weeks=8,
    ),
    "AST": MarkerRef(
        unit="U/L",
        lab_low=None, lab_high=40.0,
        optimal_low=None, optimal_high=25.0,
        category="Liver",
        dietary_sources=["coffee", "turmeric"],
        supplement_forms=["milk thistle", "NAC"],
        interactions=["ALT", "GGT"],
        retest_interval_weeks=8,
    ),
    "GGT": MarkerRef(
        unit="U/L",
        lab_low=None, lab_high=61.0,
        optimal_low=None, optimal_high=30.0,
        category="Liver",
        dietary_sources=["coffee", "green tea"],
        supplement_forms=["NAC", "milk thistle"],
        interactions=["ALT", "AST"],
        retest_interval_weeks=12,
    ),

    # ── Kidney ───────────────────────────────────────────────────────────────
    "Creatinine": MarkerRef(
        unit="mg/dL",
        lab_low=0.6, lab_high=1.3,
        optimal_low=0.7, optimal_high=1.1,
        category="Kidney",
        dietary_sources=["adequate hydration", "low protein excess"],
        supplement_forms=["none typically"],
        interactions=["eGFR", "BUN", "Uric Acid"],
        retest_interval_weeks=12,
    ),
    "BUN": MarkerRef(
        unit="mg/dL",
        lab_low=7.0, lab_high=25.0,
        optimal_low=10.0, optimal_high=20.0,
        category="Kidney",
        dietary_sources=["adequate hydration"],
        supplement_forms=["none typically"],
        interactions=["Creatinine"],
        retest_interval_weeks=12,
    ),
    "Uric Acid": MarkerRef(
        unit="mg/dL",
        lab_low=2.4, lab_high=7.0,
        optimal_low=3.0, optimal_high=5.5,
        category="Kidney",
        dietary_sources=["low-purine diet", "cherries", "adequate water"],
        supplement_forms=["tart cherry extract", "quercetin", "vitamin C"],
        interactions=["Creatinine", "eGFR"],
        retest_interval_weeks=12,
    ),

    # ── Vitamins ─────────────────────────────────────────────────────────────
    "Vitamin D": MarkerRef(
        unit="ng/mL",
        lab_low=20.0, lab_high=100.0,
        optimal_low=40.0, optimal_high=80.0,
        category="Vitamin",
        dietary_sources=["fatty fish", "egg yolk", "fortified milk", "sunlight exposure"],
        supplement_forms=["Vitamin D3 (cholecalciferol)", "D3+K2 combo"],
        interactions=["Calcium", "Magnesium", "PTH"],
        retest_interval_weeks=12,
    ),
    "Vitamin B12": MarkerRef(
        unit="pg/mL",
        lab_low=211.0, lab_high=911.0,
        optimal_low=400.0, optimal_high=800.0,
        category="Vitamin",
        dietary_sources=["meat", "fish", "dairy", "eggs", "fortified foods"],
        supplement_forms=["methylcobalamin", "hydroxocobalamin", "adenosylcobalamin"],
        interactions=["MCV", "Homocysteine", "Folate"],
        retest_interval_weeks=12,
    ),
    "Folate": MarkerRef(
        unit="ng/mL",
        lab_low=3.1, lab_high=20.5,
        optimal_low=8.0, optimal_high=18.0,
        category="Vitamin",
        dietary_sources=["leafy greens", "legumes", "avocado", "broccoli"],
        supplement_forms=["methylfolate (5-MTHF)", "folinic acid"],
        interactions=["Vitamin B12", "Homocysteine", "MCV"],
        retest_interval_weeks=12,
    ),

    # ── Minerals ─────────────────────────────────────────────────────────────
    "Calcium": MarkerRef(
        unit="mg/dL",
        lab_low=8.5, lab_high=10.5,
        optimal_low=9.0, optimal_high=10.0,
        category="Mineral",
        dietary_sources=["dairy", "leafy greens", "tofu", "sesame seeds"],
        supplement_forms=["calcium citrate", "calcium malate"],
        interactions=["Vitamin D", "Magnesium", "PTH"],
        retest_interval_weeks=12,
    ),
    "Magnesium": MarkerRef(
        unit="mg/dL",
        lab_low=1.7, lab_high=2.5,
        optimal_low=2.0, optimal_high=2.4,
        category="Mineral",
        dietary_sources=["dark chocolate", "nuts", "seeds", "leafy greens", "legumes"],
        supplement_forms=["magnesium glycinate", "magnesium malate", "magnesium threonate"],
        interactions=["Calcium", "Vitamin D"],
        retest_interval_weeks=12,
    ),
    "Serum Iron": MarkerRef(
        unit="µg/dL",
        lab_low=60.0, lab_high=170.0,
        optimal_low=80.0, optimal_high=150.0,
        category="Mineral",
        dietary_sources=["red meat", "spinach", "lentils", "pumpkin seeds"],
        supplement_forms=["ferrous bisglycinate", "ferrous sulfate"],
        interactions=["Ferritin", "TIBC", "Hemoglobin"],
        retest_interval_weeks=8,
    ),
    "Ferritin": MarkerRef(
        unit="ng/mL",
        lab_low=12.0, lab_high=300.0,
        optimal_low=50.0, optimal_high=200.0,
        category="Mineral",
        dietary_sources=["red meat", "legumes", "pumpkin seeds"],
        supplement_forms=["ferrous bisglycinate"],
        interactions=["Serum Iron", "TIBC", "Hemoglobin", "CRP"],
        retest_interval_weeks=8,
    ),

    # ── Metabolic ────────────────────────────────────────────────────────────
    "Fasting Glucose": MarkerRef(
        unit="mg/dL",
        lab_low=70.0, lab_high=100.0,
        optimal_low=75.0, optimal_high=90.0,
        category="Metabolic",
        dietary_sources=["low-GI foods", "fiber-rich diet", "cinnamon"],
        supplement_forms=["berberine", "chromium picolinate", "magnesium", "alpha-lipoic acid"],
        interactions=["HbA1c", "Insulin", "Triglycerides"],
        retest_interval_weeks=12,
    ),
    "HbA1c": MarkerRef(
        unit="%",
        lab_low=None, lab_high=5.7,
        optimal_low=None, optimal_high=5.4,
        category="Metabolic",
        dietary_sources=["low-GI diet", "high fiber", "vinegar with meals"],
        supplement_forms=["berberine", "chromium", "magnesium", "alpha-lipoic acid"],
        interactions=["Fasting Glucose", "Triglycerides", "Insulin"],
        retest_interval_weeks=12,
    ),

    # ── Inflammatory ─────────────────────────────────────────────────────────
    "CRP": MarkerRef(
        unit="mg/L",
        lab_low=None, lab_high=10.0,
        optimal_low=None, optimal_high=1.0,
        category="Inflammatory",
        dietary_sources=["omega-3 rich foods", "turmeric", "ginger", "green tea"],
        supplement_forms=["omega-3 (EPA/DHA)", "curcumin with piperine", "resveratrol"],
        interactions=["Ferritin", "WBC Count", "ESR"],
        retest_interval_weeks=8,
    ),

    # ── Hormone ──────────────────────────────────────────────────────────────
    "Testosterone": MarkerRef(
        unit="ng/dL",
        lab_low=300.0, lab_high=1000.0,
        optimal_low=500.0, optimal_high=900.0,
        category="Hormone",
        dietary_sources=["zinc-rich foods", "healthy fats", "magnesium-rich foods"],
        supplement_forms=["zinc", "magnesium", "ashwagandha", "vitamin D"],
        interactions=["SHBG", "LH", "FSH", "Vitamin D"],
        retest_interval_weeks=16,
    ),
}

# ---------------------------------------------------------------------------
# Alias map — maps common alternate names → canonical name in MARKER_REFERENCE
# ---------------------------------------------------------------------------
ALIASES: dict[str, str] = {
    # Hemoglobin
    "haemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "hgb": "Hemoglobin",
    # RBC
    "red blood cells": "RBC Count",
    "rbc": "RBC Count",
    "erythrocytes": "RBC Count",
    # Hematocrit
    "hct": "Hematocrit",
    "pcv": "Hematocrit",
    "packed cell volume": "Hematocrit",
    # MCV
    "mean corpuscular volume": "MCV",
    # WBC
    "white blood cells": "WBC Count",
    "wbc": "WBC Count",
    "leukocytes": "WBC Count",
    "total leucocyte count": "WBC Count",
    "tlc": "WBC Count",
    # Platelets
    "platelets": "Platelet Count",
    "plt": "Platelet Count",
    "thrombocytes": "Platelet Count",
    # Lipid
    "total cholesterol": "Total Cholesterol",
    "cholesterol": "Total Cholesterol",
    "chol": "Total Cholesterol",
    "ldl cholesterol": "LDL",
    "ldl-c": "LDL",
    "low density lipoprotein": "LDL",
    "hdl cholesterol": "HDL",
    "hdl-c": "HDL",
    "high density lipoprotein": "HDL",
    "tg": "Triglycerides",
    "trigs": "Triglycerides",
    "serum triglycerides": "Triglycerides",
    "vldl cholesterol": "VLDL",
    "non hdl cholesterol": "Non-HDL Cholesterol",
    "non-hdl": "Non-HDL Cholesterol",
    # Thyroid
    "tsh": "TSH",
    "thyroid stimulating hormone": "TSH",
    "ft3": "Free T3",
    "free triiodothyronine": "Free T3",
    "ft4": "Free T4",
    "free thyroxine": "Free T4",
    # Liver
    "alt": "ALT",
    "sgpt": "ALT",
    "alanine aminotransferase": "ALT",
    "alanine transaminase": "ALT",
    "ast": "AST",
    "sgot": "AST",
    "aspartate aminotransferase": "AST",
    "aspartate transaminase": "AST",
    "ggt": "GGT",
    "gamma gt": "GGT",
    "gamma glutamyl transferase": "GGT",
    # Kidney
    "creatinine": "Creatinine",
    "serum creatinine": "Creatinine",
    "blood urea nitrogen": "BUN",
    "bun": "BUN",
    "urea": "BUN",
    "uric acid": "Uric Acid",
    "serum uric acid": "Uric Acid",
    # Vitamins
    "vitamin d": "Vitamin D",
    "25-oh vitamin d": "Vitamin D",
    "25-hydroxyvitamin d": "Vitamin D",
    "vit d": "Vitamin D",
    "vitamin d3": "Vitamin D",
    "vitamin b12": "Vitamin B12",
    "vit b12": "Vitamin B12",
    "cobalamin": "Vitamin B12",
    "cyanocobalamin": "Vitamin B12",
    "folate": "Folate",
    "folic acid": "Folate",
    "serum folate": "Folate",
    # Minerals
    "calcium": "Calcium",
    "serum calcium": "Calcium",
    "magnesium": "Magnesium",
    "serum magnesium": "Magnesium",
    "iron": "Serum Iron",
    "serum iron": "Serum Iron",
    "ferritin": "Ferritin",
    "serum ferritin": "Ferritin",
    # Metabolic
    "fasting glucose": "Fasting Glucose",
    "fasting blood sugar": "Fasting Glucose",
    "fbs": "Fasting Glucose",
    "blood glucose": "Fasting Glucose",
    "glucose": "Fasting Glucose",
    "hba1c": "HbA1c",
    "hb a1c": "HbA1c",
    "glycated hemoglobin": "HbA1c",
    "glycosylated hemoglobin": "HbA1c",
    # Inflammatory
    "crp": "CRP",
    "c reactive protein": "CRP",
    "c-reactive protein": "CRP",
    "hs-crp": "CRP",
    "hsCRP": "CRP",
    # Hormone
    "testosterone": "Testosterone",
    "serum testosterone": "Testosterone",
    "total testosterone": "Testosterone",
}


def lookup(name: str) -> MarkerRef | None:
    """Return MarkerRef for a canonical name or alias, or None if not found."""
    canonical = ALIASES.get(name.lower().strip(), name)
    return MARKER_REFERENCE.get(canonical)


def canonical_name(name: str) -> str:
    """Return the canonical name for a marker (alias-resolved), or name itself."""
    return ALIASES.get(name.lower().strip(), name)
