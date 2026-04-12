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

IMPORTANT: Set patient_name to null always (privacy).

Report text:
{text}"""

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
