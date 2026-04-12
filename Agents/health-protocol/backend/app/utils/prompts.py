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

FLAGGING_SYSTEM = """You are an evidence-based clinical significance assessor.
Evaluate biomarker values against reference ranges and assign severity scores.
Return ONLY valid JSON. No markdown. No preamble.
Informational only. Not medical advice."""

FLAGGING_USER_TEMPLATE = """Assess the clinical significance of the following biomarkers.
Each marker includes its current value, lab reference range, and evidence-based optimal range.

Severity definitions (use exactly these strings):
- "normal"      — within both lab AND optimal range
- "mild"        — outside optimal range but within lab range (suboptimal, monitor)
- "moderate"    — outside lab range; lifestyle/dietary intervention warranted
- "significant" — markedly outside lab range; medical follow-up recommended

Markers to assess:
{markers_json}

Return JSON matching this schema exactly:
{{
  "assessments": [
    {{
      "canonical_name": string,
      "severity": "normal" | "mild" | "moderate" | "significant",
      "clinical_notes": string (1-2 sentences, evidence-based, no scare language),
      "related_markers": [string]
    }}
  ],
  "warnings": [string]
}}

RULES:
- clinical_notes must reference the specific value and what it implies physiologically.
- related_markers should list canonical names of markers that interact with this one.
- Never mention patient name. Always end clinical_notes with: "Informational only."
- Return one assessment per marker — same order as input."""


PROTOCOL_SYSTEM = """You are an evidence-based health protocol generator.
Create personalized protocols based on blood test results and health goals.
Return ONLY valid JSON. No markdown. No preamble.
Always include: Informational only. Not medical advice."""

PROTOCOL_USER_TEMPLATE = """Generate a personalized health protocol for the following blood test results.

User's selected goals: {goals}

Flagged markers (JSON):
{flagged_markers}

Goal cross-reference (which markers map to which goals):
{crossref}

INDIAN FOOD CONTEXT — prioritize locally available foods:
- Omega-3 / anti-inflammatory: flaxseed (alsi), mustard oil, walnuts, mackerel (bangda), rohu, sardine (tarli)
- Soluble fiber: psyllium husk (isabgol), oats, moong dal, sabja seeds
- Anti-inflammatory spices: turmeric (haldi) + black pepper, ginger (adrak), garlic (lehsun), amla
- Plant protein: moong dal, chana dal, rajma, soya chunks, paneer, curd (dahi)
- B12 sources: eggs, chicken, fish, fortified milk
- Iron: kala chana, spinach (palak) + lemon, jaggery (gud), horse gram (kulith)
- Vitamin D food sources are limited — supplementation usually needed in India
- Cost-conscious: prefer dal/sabzi/curd/eggs over expensive superfoods

SUPPLEMENT GUIDANCE:
- Prefer clinically validated forms: Methylcobalamin (B12), Cholecalciferol D3, Magnesium glycinate
- Indian brands available: Carbamide Forte, HealthKart, Himalaya, NOW Foods (Amazon India)
- For Omega-3: minimum 1g combined EPA+DHA daily for lipid effects
- Only recommend supplements with clear evidence for the specific marker

PROTOCOL RULES:
1. diet_changes: max 5 actions. Split into "immediate" (start today) and "phase_in" (introduce over 2–4 weeks).
2. supplements: only for markers where food sources are insufficient. Include dose, timing, duration.
3. lifestyle_changes: specific and actionable (e.g., "30-min brisk walk 5x/week", not "exercise more").
4. retest_schedule: use retest_weeks from the flagged marker data. Include clinical reason for each.
5. All actions must directly address at least one flagged marker.
6. End each diet/lifestyle action's rationale with: "Informational only."

Return JSON matching this schema exactly:
{{
  "diet_changes": [
    {{
      "action": string,
      "rationale": string,
      "phase": "immediate" | "phase_in",
      "targets": [string]
    }}
  ],
  "supplements": [
    {{
      "name": string,
      "dose": string,
      "timing": string,
      "duration_weeks": number,
      "targets": [string],
      "notes": string
    }}
  ],
  "lifestyle_changes": [
    {{
      "action": string,
      "frequency": string,
      "rationale": string,
      "targets": [string]
    }}
  ],
  "retest_schedule": [
    {{
      "marker": string,
      "weeks_from_now": number,
      "reason": string
    }}
  ]
}}"""
