# All Claude prompts live here — never inline in service code.

EXTRACTION_SYSTEM = """You are a medical data extraction assistant.
Extract biomarkers from blood test report text.
Return ONLY valid JSON. No markdown. No preamble.
Informational only. Not medical advice."""

EXTRACTION_USER_TEMPLATE = """Extract all biomarkers from the following lab report text.

Return JSON matching this schema:
{{
  "lab_name": string | null,
  "patient_name": null,
  "report_date": string | null,
  "markers": [
    {{
      "name": string,
      "reported_name": string,
      "value": number | null,
      "qualitative_value": string | null,
      "unit": string,
      "reference_low": number | null,
      "reference_high": number | null,
      "flag": "normal" | "low" | "high" | "critical_low" | "critical_high",
      "category": "CBC"|"Lipid"|"Thyroid"|"Liver"|"Kidney"|"Vitamin"|"Mineral"|"Hormone"|"Metabolic"|"Inflammatory"|"Other",
      "test_date": string | null
    }}
  ],
  "extraction_confidence": number (0.0-1.0),
  "warnings": [string]
}}

EDGE CASE RULES — follow exactly:
1. Non-numeric results (Positive, Negative, Reactive, Detected, Not Detected, Trace):
   Set value=null and qualitative_value=<reported string>.
   Flag: Positive/Reactive/Detected for infection/antibody markers → "high";
         Negative/Not Detected/Normal → "normal".
2. Missing reference ranges: set reference_low=null, reference_high=null.
   Derive flag from any printed marker (H, L, *, ↑, ↓, A) on the report row.
   If no marker and no range, set flag="normal".
3. Unit normalization — use these canonical forms:
   mg/dL (not mg/dl), g/dL (not g/dl), IU/mL (not IU/ml or U/mL),
   µg/dL (not ug/dL), ng/mL (not ng/ml), pmol/L, mmol/L, U/L, fL, pg.
   Preserve the printed unit verbatim if no canonical form applies.
4. Duplicate markers: keep both with their reported_name; normalize the name field
   (e.g., "Haemoglobin" and "Hemoglobin" → name="Hemoglobin" for both).
5. Panel section headers (e.g., "CBC", "Lipid Profile", "Thyroid Function") are NOT
   markers — skip them entirely.
6. extraction_confidence scoring:
   0.9–1.0 → all markers have numeric values and reference ranges
   0.7–0.89 → some markers missing ranges or have qualitative values
   0.5–0.69 → many markers are qualitative or ranges are absent
   <0.5 → text is mostly unreadable or very few markers found
7. ALWAYS set patient_name to null (privacy requirement).

Report text:
{text}"""


JSON_FIX_TEMPLATE = """The following text was supposed to be valid JSON but failed to parse.
Fix ALL syntax errors and return ONLY the corrected JSON.
No markdown code fences. No explanation. No preamble.

Broken JSON:
{broken_json}"""

PROTOCOL_SYSTEM = """You are an evidence-based health protocol generator.
Create personalized protocols based on blood test results and health goals.
Return ONLY valid JSON. No markdown. No preamble.
Always include: Informational only. Not medical advice."""

PROTOCOL_USER_TEMPLATE = """Generate a health protocol for the following:

Flagged markers:
{flagged_markers}

User goals: {goals}

Cross-reference analysis:
{crossref}

Return JSON matching this schema:
{{
  "diet_changes": [{{"action": string, "phase": "immediate"|"phase_in"}}],
  "supplements": [
    {{"name": string, "dose": string, "timing": string, "duration_weeks": number, "targets": [string]}}
  ],
  "lifestyle_changes": [{{"action": string, "frequency": string}}],
  "retest_schedule": [{{"marker": string, "weeks_from_now": number, "reason": string}}]
}}"""
