"""
orchestra_app.py — OrchestraIQ
A separate, standalone Streamlit app that demonstrates a MULTI-AGENT
architecture for AP invoice processing: one Supervisor agent that plans
the work and reviews the results, and four specialist agents that each
do one job. Every agent is its OWN Claude API call with its OWN system
prompt — nothing is shared "reasoning state" between them except the
JSON each one hands to the next. That hand-off is the whole point of
this learning app: you can see exactly what each agent received and
what it decided.

This file does not import or modify app.py (InvoiceIQ). It is a
self-contained sibling app that happens to read the same master CSVs.
"""

import os
import io
import csv
import json
import re
import streamlit as st
import pandas as pd
import PyPDF2
import anthropic
from dotenv import load_dotenv

# ── Page config (must be the first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="OrchestraIQ",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded",
)

_BASE  = os.path.dirname(os.path.abspath(__file__))
MODEL  = "claude-opus-4-6"

# ── API key: st.secrets first, then .env (same convention as InvoiceIQ) ────────
load_dotenv()
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

_MASTER_FILES = [
    "vendor_master.csv", "po_master.csv", "grn_master.csv",
    "gl_master.csv", "invoices.csv",
]


def _masters_ok() -> bool:
    return all(os.path.exists(os.path.join(_BASE, f)) for f in _MASTER_FILES)


@st.cache_data
def _csv_rows(filename: str) -> list:
    """Read a master CSV from the project folder as a list of dicts.
    Same master data InvoiceIQ uses, read independently here so this
    file never has to import app.py."""
    path = os.path.join(_BASE, filename)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _pdf_to_text(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    pages  = [p.extract_text() for p in reader.pages if p.extract_text()]
    return "\n".join(pages)


# ══════════════════════════════════════════════════════════════════════════════
# SOP KNOWLEDGE BASE
# The base rules an AP processor already knows, plus the NON-PO specific
# rules HelpDeskIQ needs when there's no PO to lean on.
# ══════════════════════════════════════════════════════════════════════════════
SOP_KB = {
    "vendor_mismatch": (
        "When vendor name on invoice does not match vendor master: "
        "1) Check for spelling variations in vendor master. "
        "2) Verify GST number matches. "
        "3) If new vendor, initiate vendor onboarding. "
        "4) If existing vendor with name change, update vendor master with approval. "
        "5) Do not process invoice until vendor is confirmed."
    ),
    "po_missing": (
        "When PO reference is absent: "
        "1) Contact requestor to provide PO number. "
        "2) Check if invoice is for recurring service with blanket PO. "
        "3) If amount under ₹10,000, may process with manager approval. "
        "4) For amounts over ₹10,000, PO is mandatory. "
        "5) Place invoice on hold until PO is provided."
    ),
    "gl_coding": (
        "GL code assignment rules: IT Services and Software = 6100. "
        "Logistics and Freight = 5200. Utilities = 6200. "
        "Office Supplies = 6300. BPO Services = 7100. "
        "When in doubt, refer to vendor category in vendor master."
    ),
    # ── NON-PO rules added for OrchestraIQ's non-PO validation path ────────────
    "non_po_invoice": (
        "Non-PO invoices are permitted for: utilities, subscriptions, recurring "
        "professional services, travel reimbursements, and emergency purchases "
        "under ₹50,000. Process: 1) Verify vendor is on the approved non-PO "
        "vendor list. 2) Check for an active blanket PO or framework agreement. "
        "3) For recurring services verify the amount matches the historical "
        "pattern within 10%. 4) Route to the cost centre owner for approval, "
        "not procurement. 5) Amounts above ₹50,000 require retrospective PO "
        "creation and dual approval. 6) Assign GL code based on vendor category "
        "and line description since no PO line exists to inherit from."
    ),
    "blanket_po": (
        "Blanket POs cover recurring purchases over a period. When an invoice "
        "has no specific PO: 1) Search for an open blanket PO for this vendor. "
        "2) Verify remaining balance covers the invoice amount. 3) Check the "
        "blanket PO validity period covers the invoice date. 4) Draw down the "
        "invoice amount from the blanket PO balance. 5) If blanket PO is "
        "exhausted, escalate to procurement for extension."
    ),
}

NON_PO_LIMIT_INR = 50_000


# ══════════════════════════════════════════════════════════════════════════════
# JSON PARSING — Claude's response is sometimes truncated mid-object when it
# runs out of tokens ("Unterminated string" from json.loads). safe_json_parse
# strips markdown fences first, and if the plain parse still fails, tries to
# repair a truncated object by closing whatever braces/brackets were left
# open. If even that fails, it returns an error dict instead of raising —
# every agent function is guaranteed to return a dict, never throw.
# ══════════════════════════════════════════════════════════════════════════════
def safe_json_parse(text: str, agent_name: str) -> dict:
    # strip markdown fences if present
    text = re.sub(r'```json\s*|```\s*', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # attempt to fix truncated JSON by closing open structures
        try:
            fixed = text.rstrip().rstrip(',')
            open_braces = fixed.count('{') - fixed.count('}')
            open_brackets = fixed.count('[') - fixed.count(']')
            fixed += ']' * open_brackets + '}' * open_braces
            return json.loads(fixed)
        except Exception:
            return {'error': f'{agent_name} returned invalid JSON', 'raw_response': text[:500], 'parse_error': str(e)}


# Raw text of the most recent call per agent, kept for the debug expander in
# the UI. Cleared at the start of every run_orchestra_pipeline() call.
_RAW_LOG: dict = {}


# ══════════════════════════════════════════════════════════════════════════════
# LOW-LEVEL CLAUDE CALL HELPER
# Every agent below wants the same thing: send a system prompt + a user
# message, get back ONE JSON object. This wraps that so each agent
# function only has to worry about *what* it's asking, not *how* to ask.
# A failed API call is converted into an error dict rather than raised, so
# one agent going down doesn't take the rest of the pipeline with it.
# ══════════════════════════════════════════════════════════════════════════════
def _call_agent(system_prompt: str, user_content: str, agent_name: str,
                 max_tokens: int = 4096) -> dict:
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )
        raw = "".join(b.text for b in response.content if b.type == "text").strip()
    except Exception as e:
        _RAW_LOG[agent_name] = f"(API call failed before any response was received: {e})"
        return {'error': f'{agent_name} API call failed', 'parse_error': str(e)}

    _RAW_LOG[agent_name] = raw
    return safe_json_parse(raw, agent_name)


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 1 — SUPERVISOR (PLANNING)
# The supervisor never touches the invoice fields itself. Its one job is
# to read the raw invoice text and decide the ROUTE: is this PO-BASED
# (a standard 3-way match applies) or NON-PO (recurring/utility/emergency
# spend that needs a different validation path)? That single decision
# changes every instruction it writes for the four specialists below.
# ══════════════════════════════════════════════════════════════════════════════
SUPERVISOR_PLAN_PROMPT = (
    "You are the Supervisor agent in OrchestraIQ, an AP invoice processing "
    "system. Read this invoice and write a processing plan. First determine "
    "the invoice type: PO-BASED (has a valid PO reference) or NON-PO (no PO "
    "reference — likely utilities, subscriptions, recurring services, "
    "reimbursements, or emergency purchase). This determination changes "
    "everything downstream. Then decide which agents to deploy and write "
    "specific instructions for each. Return JSON: {invoice_type: PO-BASED or "
    "NON-PO, invoice_category: string (e.g. utilities, professional services, "
    "goods, subscription), reasoning: string, agents_to_deploy: [list], "
    "instructions: {ExtractIQ: string, ProcessorIQ: string, AuditIQ: string, "
    "HelpDeskIQ: string}}. Be highly specific in instructions — for NON-PO "
    "invoices instruct ProcessorIQ to check blanket POs, recurring payment "
    "patterns, and cost centre approval instead of standard 3-way match. "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def supervisor_plan(invoice_text: str) -> dict:
    user = f"--- INVOICE TEXT ---\n{invoice_text}"
    return _call_agent(SUPERVISOR_PLAN_PROMPT, user, "Supervisor (Planning)")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 2 — ExtractIQ (FIELD EXTRACTION)
# Pulls every field off the invoice and — critically — grades its own
# confidence per field. That self-reported confidence is what triggers
# the re-task loop in run_orchestra_pipeline() below.
# ══════════════════════════════════════════════════════════════════════════════
EXTRACTIQ_PROMPT = (
    "You are ExtractIQ, a specialist invoice extraction agent in OrchestraIQ. "
    "Extract every field with maximum accuracy. Assign a confidence score to "
    "each field: High (clearly stated on invoice), Medium (inferred from "
    "context), Low (guessed or missing). Return ONLY JSON: {invoice_number, "
    "vendor_name, vendor_gst, invoice_date, due_date, po_reference (null if "
    "absent), line_items: [{description, qty, unit_price, total, "
    "suggested_gl_code, suggested_tax_code}], subtotal, shipping, gst_type, "
    "gst_rate, gst_amount, grand_total, payment_terms, bank_account, "
    "ifsc_code, hsn_sac_code, confidence_scores: {field_name: High/Medium/Low}, "
    "overall_confidence: High/Medium/Low, extraction_notes: string} "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def extractiq_agent(invoice_text: str, supervisor_instruction: str) -> dict:
    user = (
        f"Supervisor instruction: {supervisor_instruction}\n\n"
        f"--- INVOICE TEXT ---\n{invoice_text}"
    )
    return _call_agent(EXTRACTIQ_PROMPT, user, "ExtractIQ")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 3 — ProcessorIQ (VALIDATION)
# The agent whose behaviour actually forks on invoice_type. PO-BASED gets
# the textbook 3-way match (vendor / PO / GRN / GL / approval limit).
# NON-PO gets a different checklist entirely — blanket PO, recurring
# pattern, cost centre routing — because there's no PO or GRN to match
# against.
# ══════════════════════════════════════════════════════════════════════════════
PROCESSORIQ_PROMPT = (
    "You are ProcessorIQ, a specialist validation agent in OrchestraIQ. Your "
    "validation path depends on invoice_type.\n"
    "IF PO-BASED, run standard 3-way match: 1) Vendor validation (exact then "
    "fuzzy match, suggest closest match if no exact) 2) PO match — exists, is "
    "open, amount within 10% tolerance 3) GRN match — goods received, full or "
    "partial 4) GL code validation against vendor category 5) Approval limit "
    "check.\n"
    "IF NON-PO, run the non-PO validation path instead: 1) Vendor validation "
    "(same as above) 2) Blanket PO or framework agreement check — is there an "
    "open blanket PO for this vendor? 3) Recurring pattern check — has this "
    "vendor invoiced a similar amount in previous periods? Look at "
    "invoice_history 4) Cost centre routing — which cost centre should approve "
    "based on GL code and vendor category 5) GL code assignment — no PO line "
    "to inherit from, so recommend based on vendor category and line "
    "description 6) Non-PO threshold check — flag if amount exceeds the "
    f"non-PO limit of ₹{NON_PO_LIMIT_INR:,} requiring additional approval.\n"
    "For each check return: status (PASS/WARN/FAIL), detail, confidence, "
    "recommendation. Return JSON: {validation_path: PO-BASED or NON-PO, "
    "checks: [{check_name, status, detail, confidence, recommendation}], "
    "overall_match: full/partial/none, requires_po_creation: boolean, "
    "suggested_cost_centre: string, processoriq_notes: string, confidence: "
    "High/Medium/Low} "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def processoriq_agent(extracted_data: dict, invoice_type: str,
                       supervisor_instruction: str, vendor_master: list,
                       po_master: list, grn_master: list, gl_master: list,
                       invoice_history: list) -> dict:
    user = (
        f"invoice_type: {invoice_type}\n"
        f"Supervisor instruction: {supervisor_instruction}\n\n"
        f"extracted_data: {json.dumps(extracted_data)}\n\n"
        f"vendor_master: {json.dumps(vendor_master)}\n"
        f"po_master: {json.dumps(po_master)}\n"
        f"grn_master: {json.dumps(grn_master)}\n"
        f"gl_master: {json.dumps(gl_master)}\n"
        f"invoice_history: {json.dumps(invoice_history)}"
    )
    return _call_agent(PROCESSORIQ_PROMPT, user, "ProcessorIQ")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 4 — AuditIQ (FRAUD / ANOMALY DETECTION)
# Runs independently of ProcessorIQ, on purpose — it's a second, unrelated
# set of eyes on the same invoice. This is where a "conflict" can surface:
# ProcessorIQ might pass the vendor while AuditIQ flags a bank-detail change
# on that same vendor. The Supervisor synthesis step below is what catches
# that kind of disagreement.
# ══════════════════════════════════════════════════════════════════════════════
AUDITIQ_PROMPT = (
    "You are AuditIQ, a specialist fraud detection and anomaly agent in "
    "OrchestraIQ. Run: 1) Duplicate detection — same vendor and same amount "
    "within 30 days, also check similar amounts within 5% 2) Amount anomaly — "
    "compare against vendor historical average, flag if more than 2x 3) "
    "Frequency anomaly — for NON-PO recurring invoices, check if the billing "
    "frequency has changed unexpectedly 4) Vendor pattern analysis — any "
    "suspicious changes in bank details, GST number, or billing address 5) "
    "For NON-PO invoices apply extra scrutiny since there is no PO control. "
    "Return JSON: {duplicate_check: {status, detail, matching_invoices}, "
    "anomaly_check: {status, detail, vendor_average, deviation_percent}, "
    "frequency_check: {status, detail}, vendor_pattern_analysis: string, "
    "risk_level: Low/Medium/High, requires_manual_review: boolean, "
    "auditiq_notes: string, confidence: High/Medium/Low} "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def auditiq_agent(extracted_data: dict, invoice_type: str,
                   supervisor_instruction: str, invoice_history: list) -> dict:
    user = (
        f"invoice_type: {invoice_type}\n"
        f"Supervisor instruction: {supervisor_instruction}\n\n"
        f"extracted_data: {json.dumps(extracted_data)}\n\n"
        f"invoice_history: {json.dumps(invoice_history)}"
    )
    return _call_agent(AUDITIQ_PROMPT, user, "AuditIQ")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 5 — HelpDeskIQ (DECISION & COMMUNICATION)
# The only agent that talks to a human. It doesn't re-run any checks —
# it reads what ExtractIQ, ProcessorIQ and AuditIQ already found and turns
# that into a decision plus a message a person could actually send.
# ══════════════════════════════════════════════════════════════════════════════
HELPDESKIQ_PROMPT = (
    "You are HelpDeskIQ, the decision and communication agent in OrchestraIQ. "
    "You receive findings from ExtractIQ, ProcessorIQ and AuditIQ. Generate: "
    "1) Final decision: Auto-approve / Route for approval / Escalate to "
    "manager / Return to vendor / Create PO retrospectively (only for NON-PO "
    "invoices that need a PO) 2) A professional helpdesk note in plain "
    "English an AP processor could send directly to the vendor or manager 3) "
    "SLA: same day / 2 business days / 5 business days 4) Top 3 recommended "
    "next actions 5) Escalation path — who specifically should this go to. "
    "For NON-PO invoices, reference non-PO SOP rules. Return JSON: {decision, "
    "confidence: High/Medium/Low, helpdesk_note, next_actions: [3 items], "
    "sla, escalation_path, requires_po_creation: boolean} "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def helpdesiq_agent(all_findings: dict, invoice_type: str,
                     supervisor_instruction: str, sop_knowledge: dict) -> dict:
    user = (
        f"invoice_type: {invoice_type}\n"
        f"Supervisor instruction: {supervisor_instruction}\n\n"
        f"all_findings: {json.dumps(all_findings)}\n\n"
        f"sop_knowledge: {json.dumps(sop_knowledge)}"
    )
    return _call_agent(HELPDESKIQ_PROMPT, user, "HelpDeskIQ")


# ══════════════════════════════════════════════════════════════════════════════
# AGENT 6 — SUPERVISOR (SYNTHESIS)
# The Supervisor's second and final call. This is the "manager checking
# the team's work" step — it looks for low-confidence findings, conflicts
# between agents, and whether the PO-BASED vs NON-PO call it made at
# planning time actually held up once the specialists dug in.
# ══════════════════════════════════════════════════════════════════════════════
SUPERVISOR_SYNTHESISE_PROMPT = (
    "You are the Supervisor agent in OrchestraIQ completing the "
    "orchestration. Review all agent findings: 1) Check each agent "
    "confidence score — flag any Low confidence findings and state what "
    "additional data would resolve it 2) Identify conflicts between agents — "
    "for example ProcessorIQ passes the vendor but AuditIQ flags a suspicious "
    "bank detail change 3) Validate that the invoice_type routing decision "
    "you made at planning was correct given what the agents found 4) Make "
    "the final routing call 5) Assign overall processing confidence. Return "
    "JSON: {low_confidence_flags: [list], conflicts_detected: [list], "
    "routing_validation: string, final_routing: string, overall_confidence: "
    "High/Medium/Low, supervisor_notes: string, recommended_human_review: "
    "boolean} "
    "Keep your response concise. Return ONLY valid JSON with no markdown "
    "formatting, no code fences, and no explanation before or after. Keep "
    "all string values under 200 characters."
)


def supervisor_synthesise(plan: dict, all_agent_findings: dict) -> dict:
    user = (
        f"plan: {json.dumps(plan)}\n\n"
        f"all_agent_findings: {json.dumps(all_agent_findings)}"
    )
    return _call_agent(SUPERVISOR_SYNTHESISE_PROMPT, user, "Supervisor (Synthesis)")


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATION
# This is the conductor. It calls the six agent functions above in order,
# feeding each one's output into the next, and runs the ExtractIQ re-task
# loop when confidence is Low. `on_update`, if given, is called after every
# stage so the Streamlit UI can repaint its live status panel in real time
# as the pipeline runs (see run_orchestra_pipeline call in the UI section).
# ══════════════════════════════════════════════════════════════════════════════
def run_orchestra_pipeline(invoice_text: str, on_update=None) -> dict:

    def _update(stage: str, status: str, confidence: str = None, note: str = ""):
        if on_update:
            on_update(stage, status, confidence, note)

    def _finish(stage: str, result: dict, confidence_key: str = "confidence"):
        """Mark a stage complete, or — if the agent returned an error dict —
        mark it 'error' (red in the live panel) and let the pipeline carry on
        with whatever partial result we have instead of raising."""
        if isinstance(result, dict) and result.get("error"):
            _update(stage, "error", None, note=result["error"])
        else:
            _update(stage, "complete", (result or {}).get(confidence_key))

    _RAW_LOG.clear()
    re_task_log = []

    # 1. Supervisor plans the route ------------------------------------------------
    _update("supervisor_plan", "running")
    plan = supervisor_plan(invoice_text)
    invoice_type = plan.get("invoice_type", "NON-PO")
    instructions = plan.get("instructions", {}) if not plan.get("error") else {}
    _update("supervisor_plan", "error" if plan.get("error") else "complete",
            None, note=plan.get("error", ""))

    # 2. ExtractIQ pulls the fields --------------------------------------------------
    _update("extractiq", "running")
    extracted = extractiq_agent(invoice_text, instructions.get("ExtractIQ", ""))

    # 3. RE-TASK LOOP — re-extract if ExtractIQ is not confident (max 2 attempts) ----
    attempt = 1
    while extracted.get("overall_confidence") == "Low" and attempt < 2:
        attempt += 1
        low_fields = [
            f for f, c in (extracted.get("confidence_scores") or {}).items()
            if c == "Low"
        ]
        re_task_log.append({
            "agent": "ExtractIQ",
            "attempt": attempt,
            "trigger": "overall_confidence was Low",
            "low_confidence_fields": low_fields,
        })
        _update("extractiq", "retasked", None,
                note=f"Re-extracting fields: {', '.join(low_fields) or 'unspecified'}")
        retask_instruction = (
            f"Re-extract with extra attention to these low confidence fields: "
            f"{low_fields}"
        )
        extracted = extractiq_agent(invoice_text, retask_instruction)

    _finish("extractiq", extracted, confidence_key="overall_confidence")

    # ── Master data (shared by ProcessorIQ + AuditIQ) ───────────────────────────────
    vendor_master   = _csv_rows("vendor_master.csv")
    po_master       = _csv_rows("po_master.csv")
    grn_master      = _csv_rows("grn_master.csv")
    gl_master       = _csv_rows("gl_master.csv")
    invoice_history = _csv_rows("invoices.csv")

    # 4. ProcessorIQ validates (path depends on invoice_type) -------------------------
    _update("processoriq", "running")
    processoriq_result = processoriq_agent(
        extracted, invoice_type, instructions.get("ProcessorIQ", ""),
        vendor_master, po_master, grn_master, gl_master, invoice_history,
    )
    _finish("processoriq", processoriq_result)

    # 5. AuditIQ checks for fraud / anomalies -----------------------------------------
    _update("auditiq", "running")
    auditiq_result = auditiq_agent(
        extracted, invoice_type, instructions.get("AuditIQ", ""), invoice_history,
    )
    _finish("auditiq", auditiq_result)

    # 6. HelpDeskIQ decides and drafts the human-facing note --------------------------
    _update("helpdeskiq", "running")
    all_findings = {
        "ExtractIQ": extracted,
        "ProcessorIQ": processoriq_result,
        "AuditIQ": auditiq_result,
    }
    helpdeskiq_result = helpdesiq_agent(
        all_findings, invoice_type, instructions.get("HelpDeskIQ", ""), SOP_KB,
    )
    _finish("helpdeskiq", helpdeskiq_result)

    # 7. Supervisor synthesises everything ---------------------------------------------
    _update("supervisor_synthesis", "running")
    all_findings["HelpDeskIQ"] = helpdeskiq_result
    synthesis = supervisor_synthesise(plan, all_findings)
    _finish("supervisor_synthesis", synthesis, confidence_key="overall_confidence")

    return {
        "plan": plan,
        "extracted": extracted,
        "processoriq": processoriq_result,
        "auditiq": auditiq_result,
        "helpdeskiq": helpdeskiq_result,
        "synthesis": synthesis,
        "re_task_log": re_task_log,
        "raw_responses": dict(_RAW_LOG),
    }


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Dark Enterprise Theme
# Copied verbatim from app.py (InvoiceIQ) so both apps render identically.
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Palette ─────────────────────────────────────────────────────────────── */
:root {
    --bg:     #0F1117;
    --sb:     #1A1D27;
    --card:   #1E2130;
    --border: #2A2D3E;
    --blue:   #4F8EF7;
    --green:  #00C48C;
    --amber:  #FFB547;
    --red:    #FF5C5C;
    --text:   #E8EAF0;
    --muted:  #8B8FA8;
}

/* ── Main canvas ─────────────────────────────────────────────────────────── */
.stApp {
    background-color: var(--bg);
}
.block-container {
    padding-top: 1.75rem;
    padding-bottom: 2rem;
}
.stApp, .stApp p, .stApp li, .stApp span,
.stApp label, .stApp div {
    color: var(--text);
}

/* ── Sidebar shell ───────────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
    background-color: var(--sb) !important;
    border-right: 1px solid var(--border);
}

/* ── Hide the default radio bullet ──────────────────────────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio"] label > div:first-child {
    display: none !important;
}

/* ── Remove gap between radio options ───────────────────────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio-group"] {
    gap: 0 !important;
}

/* ── Nav item — default state ────────────────────────────────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio"] {
    padding: 0;
    margin: 0;
}
[data-testid="stSidebar"] [data-baseweb="radio"] label {
    display: block;
    padding: 0.6rem 1.25rem;
    border-left: 3px solid transparent;
    color: var(--muted);
    font-size: 0.875rem;
    cursor: pointer;
    transition: color 0.12s, background 0.12s, border-color 0.12s;
    background: transparent;
    user-select: none;
    line-height: 1.4;
}

/* ── Nav item — hover ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio"] label:hover {
    color: var(--text);
    background: rgba(79, 142, 247, 0.07);
    border-left-color: rgba(79, 142, 247, 0.35);
}

/* ── Nav item — active (selected) ────────────────────────────────────────── */
[data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) label {
    border-left-color: var(--blue) !important;
    color: var(--blue) !important;
    background: rgba(79, 142, 247, 0.12) !important;
    font-weight: 600;
}

/* ── Headings ────────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }

/* ── Horizontal rules ────────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; opacity: 1; }

/* ── Inputs & text areas ─────────────────────────────────────────────────── */
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background-color: var(--card) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}

/* ── Selectbox / dropdown background ────────────────────────────────────── */
[data-baseweb="select"] > div {
    background-color: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── File uploader — dark drop zone ─────────────────────────────────────── */
[data-testid="stFileUploader"] section {
    background-color: var(--card);
    border: 2px dashed var(--border);
    border-radius: 10px;
    transition: border-color 0.18s, background 0.18s;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--blue);
    background-color: rgba(79, 142, 247, 0.04);
}
[data-testid="stFileUploaderDropzoneInstructions"] div span {
    color: var(--muted) !important;
}

/* ── Primary button ──────────────────────────────────────────────────────── */
.stButton > button[kind="primary"] {
    background: var(--blue);
    border: none;
    color: #fff;
    font-weight: 600;
    border-radius: 6px;
    padding: 0.45rem 1.4rem;
}
.stButton > button[kind="primary"]:hover {
    background: #3a78e8;
}

/* ── Download buttons — green ────────────────────────────────────────────── */
.stDownloadButton > button {
    background: #00C48C !important;
    color: #fff !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 0.5rem 0.6rem !important;
    font-size: 0.78rem !important;
    line-height: 1.4 !important;
    width: 100% !important;
}
.stDownloadButton > button:hover {
    background: #00a87a !important;
}

/* ── OrchestraIQ-specific: multi-agent badge ─────────────────────────────── */
.oiq-badge {
    display: inline-block;
    background: rgba(79,142,247,0.12);
    color: var(--blue);
    border: 1px solid var(--blue);
    border-radius: 12px;
    padding: 2px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — same structure as app.py: brand title, nav radio, masters indicator
# ══════════════════════════════════════════════════════════════════════════════
PAGES = ["Pipeline", "Agent Reports", "Comparison", "Master Data"]

with st.sidebar:
    st.markdown(
        "<h2 style='color:#4F8EF7; font-size:1.4rem; "
        "margin-bottom:0.1rem; padding-bottom:0;'>OrchestraIQ</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<hr style='margin:0.5rem 0 0.75rem;'>",
        unsafe_allow_html=True,
    )

    page = st.radio(
        label="Navigation",
        options=PAGES,
        label_visibility="collapsed",
    )

    # Push master-data status to the bottom
    st.markdown(
        "<div style='margin-top:3rem;'></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='margin:0 0 0.6rem;'>", unsafe_allow_html=True)

    if _masters_ok():
        st.markdown(
            "<p style='font-size:0.78rem; color:var(--muted,#8B8FA8); margin:0;'>"
            "<span style='color:#00C48C;'>●</span>&nbsp; Masters loaded</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<p style='font-size:0.78rem; color:var(--muted,#8B8FA8); margin:0;'>"
            "<span style='color:#FF5C5C;'>●</span>&nbsp; Masters not loaded</p>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# SHARED UI HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _indian_fmt(amount) -> str:
    """Format a number in Indian numbering style with ₹ prefix."""
    try:
        n = int(float(amount))
    except (TypeError, ValueError):
        return "—"
    s = str(abs(n))
    if len(s) <= 3:
        out = s
    else:
        last3 = s[-3:]
        rest  = s[:-3]
        pairs = []
        while rest:
            pairs.append(rest[-2:])
            rest = rest[:-2]
        pairs.reverse()
        out = ",".join(pairs) + "," + last3
    return f"{'-' if n < 0 else ''}₹{out}"


def _pill(text: str, color: str) -> str:
    return (
        f"<span style='background:rgba(0,0,0,0.15); color:{color}; "
        f"border:1px solid {color}; border-radius:12px; padding:2px 10px; "
        f"font-size:0.75rem; font-weight:600; white-space:nowrap;'>{text}</span>"
    )


def _show_agent_error(result: dict) -> None:
    """Render a red warning for an agent whose response failed to parse
    (or whose API call failed), instead of raising or silently showing a
    blank report."""
    st.error(f"⚠️ {result.get('error', 'This agent failed.')}")
    if result.get("parse_error"):
        st.caption(f"Parse error: {result['parse_error']}")
    if result.get("raw_response"):
        with st.expander("Raw response (truncated)"):
            st.code(result["raw_response"], language="text")


def _sec_hdr(title: str) -> None:
    st.markdown(
        f"<div style='border-left:3px solid #4F8EF7; padding-left:0.8rem; "
        f"margin:1.75rem 0 0.5rem;'>"
        f"<span style='color:#E8EAF0; font-size:1rem; font-weight:700;'>"
        f"{title}</span></div>",
        unsafe_allow_html=True,
    )


# Confidence / status → colour maps, shared by every report section below.
_CONF_COLOR   = {"High": "#00C48C", "Medium": "#FFB547", "Low": "#FF5C5C"}
_CHECK_COLOR  = {"PASS": "#00C48C", "WARN": "#FFB547", "FAIL": "#FF5C5C"}
_RISK_COLOR   = {"Low": "#00C48C", "Medium": "#FFB547", "High": "#FF5C5C"}
_DECISION_COLOR = {
    "Auto-approve": "#00C48C",
    "Route for approval": "#4F8EF7",
    "Escalate to manager": "#FF5C5C",
    "Return to vendor": "#FF5C5C",
    "Create PO retrospectively": "#FFB547",
}

# Row status → (label, colour) for the live agent status panel.
_ROW_STATUS = {
    "waiting":  ("Waiting",   "#8B8FA8"),
    "running":  ("Running…",  "#4F8EF7"),
    "complete": ("Complete",  "#00C48C"),
    "retasked": ("Re-tasked", "#FFB547"),
    "error":    ("Error",     "#FF5C5C"),
}

_AGENT_ROWS = [
    ("supervisor_plan",      "Supervisor (Planning)"),
    ("extractiq",            "ExtractIQ"),
    ("processoriq",          "ProcessorIQ"),
    ("auditiq",              "AuditIQ"),
    ("helpdeskiq",           "HelpDeskIQ"),
    ("supervisor_synthesis", "Supervisor (Synthesis)"),
]


def _render_row(placeholder, name: str, status_key: str, confidence: str = None):
    label, color = _ROW_STATUS[status_key]
    spinner = " ⏳" if status_key == "running" else ""
    conf_html = (
        f"&nbsp;&nbsp;<span style='color:{_CONF_COLOR.get(confidence,'#8B8FA8')}; "
        f"font-size:0.8rem;'>Confidence: {confidence}</span>"
        if confidence else ""
    )
    placeholder.markdown(
        f"<div style='background:#1E2130; border:1px solid #2A2D3E; "
        f"border-radius:8px; padding:0.65rem 1rem; margin-bottom:0.4rem; "
        f"display:flex; align-items:center; justify-content:space-between;'>"
        f"<span style='font-weight:600;'>{name}</span>"
        f"<span>{_pill(label + spinner, color)}{conf_html}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Session state ────────────────────────────────────────────────────────────
for _k in ("oiq_pdf_name", "oiq_result"):
    if _k not in st.session_state:
        st.session_state[_k] = None


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — PIPELINE
# Upload an invoice, run the six agents, watch them go in real time.
# ══════════════════════════════════════════════════════════════════════════════
def page_pipeline():
    st.markdown(
        "<div style='display:flex; align-items:center; gap:0.75rem; margin-bottom:0.1rem;'>"
        "<h1 style='margin:0;'>Pipeline</h1>"
        "<span class='oiq-badge'>Multi-Agent Architecture</span>"
        "</div>"
        "<p style='color:#8B8FA8; margin:0.15rem 0 1.5rem; font-size:0.95rem;'>"
        "Supervisor + 4 specialist agents</p>",
        unsafe_allow_html=True,
    )

    if not _masters_ok():
        st.markdown(
            "<div style='background:rgba(255,92,92,0.09); border-left:4px solid #FF5C5C; "
            "border-radius:6px; padding:0.7rem 1.1rem; margin-bottom:1rem; color:#FF5C5C; "
            "font-size:0.88rem;'>Master CSVs not found in this folder — ProcessorIQ and "
            "AuditIQ need vendor_master.csv, po_master.csv, grn_master.csv, gl_master.csv "
            "and invoices.csv alongside this file.</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<p style='color:#8B8FA8; margin-bottom:0.4rem; font-size:0.85rem;'>"
        "Drop invoice PDF here or click to browse</p>",
        unsafe_allow_html=True,
    )
    pdf_file = st.file_uploader(
        "Invoice PDF", type=["pdf"], key="oiq_pdf_uploader", label_visibility="collapsed",
    )

    if pdf_file is not None and st.session_state.oiq_pdf_name != pdf_file.name:
        st.session_state.oiq_result = None
        st.session_state.oiq_pdf_name = pdf_file.name

    run_clicked = st.button("Run Orchestra Pipeline", type="primary", disabled=pdf_file is None)

    # ── Live agent status panel ──────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    _sec_hdr("Live Agent Status")
    row_placeholders = {}
    for key, label in _AGENT_ROWS:
        row_placeholders[key] = st.empty()
        _render_row(row_placeholders[key], label, "waiting")

    # ── Run the pipeline ──────────────────────────────────────────────────────
    if run_clicked and pdf_file is not None:
        if not ANTHROPIC_API_KEY:
            st.error("ANTHROPIC_API_KEY not found in st.secrets or .env — cannot run agents.")
        else:
            pdf_text = _pdf_to_text(pdf_file.getvalue())
            if not pdf_text.strip():
                st.error("No text found in this PDF. The file must contain selectable text.")
            else:
                labels = dict(_AGENT_ROWS)

                def _on_update(stage, status, confidence=None, note=""):
                    _render_row(row_placeholders[stage], labels[stage], status, confidence)

                try:
                    st.session_state.oiq_result = run_orchestra_pipeline(pdf_text, on_update=_on_update)
                except Exception as e:
                    st.error(f"Pipeline failed: {e}")

    if st.session_state.oiq_result:
        st.markdown(
            "<div style='background:rgba(0,196,140,0.09); border-left:4px solid #00C48C; "
            "border-radius:6px; padding:0.7rem 1.1rem; margin-top:1.1rem; color:#00C48C; "
            "font-size:0.9rem;'>&#10003;&nbsp; Pipeline complete — see the "
            "<strong style='color:#E8EAF0;'>Agent Reports</strong> and "
            "<strong style='color:#E8EAF0;'>Comparison</strong> pages for full detail.</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — AGENT REPORTS
# The six expandable report sections, one per agent call.
# ══════════════════════════════════════════════════════════════════════════════
def page_agent_reports():
    st.title("Agent Reports")

    result = st.session_state.oiq_result
    if not result:
        st.markdown(
            "<div style='background:#1E2130; border-radius:8px; padding:2rem; "
            "text-align:center; color:#8B8FA8; margin-top:2rem;'>"
            "No pipeline run yet. Upload an invoice and click "
            "<strong style='color:#E8EAF0;'>Run Orchestra Pipeline</strong> on the "
            "<strong style='color:#E8EAF0;'>Pipeline</strong> page."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── 1. Supervisor Plan ───────────────────────────────────────────────────
    with st.expander("1. Supervisor Plan", expanded=True):
        plan = result["plan"]
        if plan.get("error"):
            _show_agent_error(plan)
        else:
            c1, c2 = st.columns(2)
            c1.markdown(f"**Invoice type:** {_pill(plan.get('invoice_type','—'), '#4F8EF7')}",
                        unsafe_allow_html=True)
            c2.markdown(f"**Category:** {plan.get('invoice_category','—')}")
            st.markdown(f"**Reasoning:** {plan.get('reasoning','—')}")
            st.markdown(f"**Agents deployed:** {', '.join(plan.get('agents_to_deploy', []))}")
            st.markdown("**Instructions issued to each agent:**")
            for agent, instr in (plan.get("instructions") or {}).items():
                st.markdown(f"- **{agent}:** {instr}")

    # ── 2. ExtractIQ Report ──────────────────────────────────────────────────
    with st.expander("2. ExtractIQ Report"):
        ex = result["extracted"]
        if ex.get("error"):
            _show_agent_error(ex)
        else:
            conf_scores = ex.get("confidence_scores") or {}
            overall = ex.get("overall_confidence", "—")
            st.markdown(
                f"**Overall confidence:** "
                f"{_pill(overall, _CONF_COLOR.get(overall, '#8B8FA8'))}",
                unsafe_allow_html=True,
            )
            field_rows = []
            for field in ("invoice_number", "vendor_name", "vendor_gst", "invoice_date",
                          "due_date", "po_reference", "subtotal", "shipping", "gst_type",
                          "gst_rate", "gst_amount", "grand_total", "payment_terms",
                          "bank_account", "ifsc_code", "hsn_sac_code"):
                field_rows.append({
                    "Field": field,
                    "Value": ex.get(field),
                    "Confidence": conf_scores.get(field, "—"),
                })
            st.dataframe(pd.DataFrame(field_rows), width="stretch", hide_index=True)

            line_items = ex.get("line_items") or []
            if line_items:
                st.markdown("**Line items:**")
                st.dataframe(pd.DataFrame(line_items), width="stretch", hide_index=True)

            st.markdown(f"**Extraction notes:** {ex.get('extraction_notes','—')}")

    # ── 3. ProcessorIQ Report ────────────────────────────────────────────────
    with st.expander("3. ProcessorIQ Report"):
        pr = result["processoriq"]
        if pr.get("error"):
            _show_agent_error(pr)
        else:
            path = pr.get("validation_path", "—")
            st.markdown(
                f"**Validation path:** {_pill(path, '#4F8EF7')}&nbsp;&nbsp;"
                f"**Overall match:** {pr.get('overall_match','—')}",
                unsafe_allow_html=True,
            )
            checks = pr.get("checks") or []
            if checks:
                rows = []
                for c in checks:
                    rows.append({
                        "Check": c.get("check_name"),
                        "Status": c.get("status"),
                        "Detail": c.get("detail"),
                        "Confidence": c.get("confidence"),
                        "Recommendation": c.get("recommendation"),
                    })
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            st.markdown(f"**Requires PO creation:** {pr.get('requires_po_creation', False)}")
            st.markdown(f"**Suggested cost centre:** {pr.get('suggested_cost_centre','—')}")
            st.markdown(f"**Notes:** {pr.get('processoriq_notes','—')}")

    # ── 4. AuditIQ Report ────────────────────────────────────────────────────
    with st.expander("4. AuditIQ Report"):
        au = result["auditiq"]
        if au.get("error"):
            _show_agent_error(au)
        else:
            risk = au.get("risk_level", "—")
            st.markdown(
                f"**Risk level:** {_pill(risk, _RISK_COLOR.get(risk, '#8B8FA8'))}&nbsp;&nbsp;"
                f"**Requires manual review:** {au.get('requires_manual_review', False)}",
                unsafe_allow_html=True,
            )
            dup = au.get("duplicate_check") or {}
            anom = au.get("anomaly_check") or {}
            freq = au.get("frequency_check") or {}
            st.markdown(f"**Duplicate check:** {dup.get('status','—')} — {dup.get('detail','—')}")
            if dup.get("matching_invoices"):
                st.markdown(f"&nbsp;&nbsp;Matching invoices: {dup.get('matching_invoices')}")
            st.markdown(
                f"**Anomaly check:** {anom.get('status','—')} — {anom.get('detail','—')} "
                f"(vendor average: {anom.get('vendor_average','—')}, "
                f"deviation: {anom.get('deviation_percent','—')}%)"
            )
            st.markdown(f"**Frequency check:** {freq.get('status','—')} — {freq.get('detail','—')}")
            st.markdown(f"**Vendor pattern analysis:** {au.get('vendor_pattern_analysis','—')}")
            st.markdown(f"**Notes:** {au.get('auditiq_notes','—')}")

    # ── 5. HelpDeskIQ Report ─────────────────────────────────────────────────
    with st.expander("5. HelpDeskIQ Report"):
        hd = result["helpdeskiq"]
        if hd.get("error"):
            _show_agent_error(hd)
        else:
            decision = hd.get("decision", "—")
            d_color = _DECISION_COLOR.get(decision, "#8B8FA8")
            st.markdown(
                f"<div style='background:rgba(0,0,0,0.15); border-left:4px solid {d_color}; "
                f"border-radius:6px; padding:0.9rem 1.2rem; margin-bottom:0.9rem;'>"
                f"<span style='color:{d_color}; font-weight:700; font-size:1.05rem;'>"
                f"{decision}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Helpdesk note:**\n\n{hd.get('helpdesk_note','—')}")
            st.markdown("**Next actions:**")
            for i, action in enumerate(hd.get("next_actions") or [], 1):
                st.markdown(f"{i}. {action}")
            st.markdown(f"**SLA:** {hd.get('sla','—')}")
            st.markdown(f"**Escalation path:** {hd.get('escalation_path','—')}")
            st.markdown(f"**Requires PO creation:** {hd.get('requires_po_creation', False)}")

    # ── 6. Supervisor Synthesis ──────────────────────────────────────────────
    with st.expander("6. Supervisor Synthesis"):
        sy = result["synthesis"]
        if sy.get("error"):
            _show_agent_error(sy)
        else:
            overall = sy.get("overall_confidence", "—")
            st.markdown(
                f"**Overall confidence:** "
                f"{_pill(overall, _CONF_COLOR.get(overall, '#8B8FA8'))}&nbsp;&nbsp;"
                f"**Recommended human review:** {sy.get('recommended_human_review', False)}",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Final routing:** {sy.get('final_routing','—')}")
            st.markdown(f"**Routing validation:** {sy.get('routing_validation','—')}")
            low_flags = sy.get("low_confidence_flags") or []
            if low_flags:
                st.markdown("**Low confidence flags:**")
                for flag in low_flags:
                    st.markdown(f"- {flag}")
            conflicts = sy.get("conflicts_detected") or []
            if conflicts:
                st.markdown("**Conflicts detected:**")
                for conflict in conflicts:
                    st.markdown(f"- {conflict}")
            st.markdown(f"**Supervisor notes:** {sy.get('supervisor_notes','—')}")

    # ── Re-task log ───────────────────────────────────────────────────────────
    re_task_log = result.get("re_task_log") or []
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    if re_task_log:
        _sec_hdr("Re-task Log")
        for entry in re_task_log:
            st.markdown(
                f"- **{entry['agent']}** re-tasked (attempt {entry['attempt']}) — "
                f"triggered by: {entry['trigger']}. "
                f"Low confidence fields: {', '.join(entry['low_confidence_fields']) or 'none listed'}"
            )
    else:
        st.markdown(
            "<p style='color:#8B8FA8; font-size:0.85rem;'>No agent was re-tasked — "
            "every agent reported sufficient confidence on its first attempt.</p>",
            unsafe_allow_html=True,
        )

    # ── Debug: raw agent responses ────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    with st.expander("Debug: Raw Agent Responses"):
        st.markdown(
            "<p style='color:#8B8FA8; font-size:0.83rem; margin-bottom:0.75rem;'>"
            "The exact, unparsed text each agent returned — useful for seeing "
            "what went wrong when a response fails to parse as JSON.</p>",
            unsafe_allow_html=True,
        )
        raw_responses = result.get("raw_responses") or {}
        if not raw_responses:
            st.markdown(
                "<p style='color:#8B8FA8; font-size:0.85rem;'>No raw responses recorded.</p>",
                unsafe_allow_html=True,
            )
        for agent_name, raw_text in raw_responses.items():
            st.markdown(f"**{agent_name}**")
            st.code(raw_text or "(empty response)", language="text")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — COMPARISON
# Two things worth comparing in a multi-agent system: (1) how the PO-BASED
# and NON-PO validation paths differ in general, and (2) — once a pipeline
# has actually run — how confident each of the six agent calls was on this
# particular invoice, side by side.
# ══════════════════════════════════════════════════════════════════════════════
def page_comparison():
    st.title("Comparison")

    _sec_hdr("Validation Path: PO-BASED vs NON-PO")
    st.markdown(
        "<p style='color:#8B8FA8; font-size:0.85rem; margin-bottom:0.75rem;'>"
        "The Supervisor's PO-BASED / NON-PO call at planning time sends "
        "ProcessorIQ down one of two very different checklists.</p>",
        unsafe_allow_html=True,
    )
    comp_rows = [
        ("Vendor validation", "Exact then fuzzy match", "Exact then fuzzy match"),
        ("Reference document", "PO must exist, be open, within 10% tolerance",
         "Blanket PO / framework agreement check"),
        ("Receipt evidence", "GRN match — full or partial", "Recurring pattern vs invoice_history"),
        ("Routing", "Standard approval limit check", "Cost centre owner approval"),
        ("GL code", "Validated against the PO line", "Assigned from vendor category + line description"),
        ("Threshold", "Vendor approval limit", f"Non-PO limit ₹{NON_PO_LIMIT_INR:,} — above needs dual approval"),
    ]
    rows_html = ""
    for i, (dim, po_based, non_po) in enumerate(comp_rows):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_html += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.55rem 0.9rem; color:#8B8FA8; font-size:0.83rem; "
            f"font-weight:600;'>{dim}</td>"
            f"<td style='padding:0.55rem 0.9rem; color:#E8EAF0; font-size:0.83rem;'>{po_based}</td>"
            f"<td style='padding:0.55rem 0.9rem; color:#E8EAF0; font-size:0.83rem;'>{non_po}</td>"
            f"</tr>"
        )
    th = ("padding:0.55rem 0.9rem; text-align:left; color:#8B8FA8; font-size:0.77rem; "
          "font-weight:600; letter-spacing:0.05em; text-transform:uppercase;")
    st.markdown(
        f"<div style='background:#1E2130; border-radius:8px; overflow:hidden; "
        f"border:1px solid #2A2D3E;'>"
        f"<table style='width:100%; border-collapse:collapse;'>"
        f"<thead><tr style='background:#161929;'>"
        f"<th style='{th}'>Check</th>"
        f"<th style='{th}'>{_pill('PO-BASED', '#4F8EF7')}</th>"
        f"<th style='{th}'>{_pill('NON-PO', '#FFB547')}</th>"
        f"</tr></thead><tbody>{rows_html}</tbody></table></div>",
        unsafe_allow_html=True,
    )

    result = st.session_state.oiq_result
    if not result:
        st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            "<div style='background:#1E2130; border-radius:8px; padding:1.5rem; "
            "text-align:center; color:#8B8FA8;'>"
            "Run the pipeline on the <strong style='color:#E8EAF0;'>Pipeline</strong> page "
            "to compare this invoice's actual agent confidence scores here."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
    _sec_hdr("This Run: Agent Confidence Side by Side")
    conf_rows = [
        ("ExtractIQ",              result["extracted"].get("overall_confidence", "—")),
        ("ProcessorIQ",            result["processoriq"].get("confidence", "—")),
        ("AuditIQ",                result["auditiq"].get("confidence", "—")),
        ("HelpDeskIQ",             result["helpdeskiq"].get("confidence", "—")),
        ("Supervisor (Synthesis)", result["synthesis"].get("overall_confidence", "—")),
    ]
    rows_html2 = ""
    for i, (agent, conf) in enumerate(conf_rows):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_html2 += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.55rem 0.9rem; color:#E8EAF0; font-size:0.85rem; "
            f"font-weight:600;'>{agent}</td>"
            f"<td style='padding:0.55rem 0.9rem;'>"
            f"{_pill(conf, _CONF_COLOR.get(conf, '#8B8FA8'))}</td>"
            f"</tr>"
        )
    st.markdown(
        f"<div style='background:#1E2130; border-radius:8px; overflow:hidden; "
        f"border:1px solid #2A2D3E;'>"
        f"<table style='width:100%; border-collapse:collapse;'>"
        f"<thead><tr style='background:#161929;'>"
        f"<th style='{th}'>Agent</th><th style='{th}'>Confidence</th>"
        f"</tr></thead><tbody>{rows_html2}</tbody></table></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='color:#8B8FA8; font-size:0.83rem; margin-top:0.75rem;'>"
        f"Validation path taken: {_pill(result['processoriq'].get('validation_path','—'), '#4F8EF7')}"
        f"&nbsp;&nbsp;Final routing: {_pill(result['synthesis'].get('final_routing','—'), '#00C48C')}</p>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — MASTER DATA
# The same 5 master CSVs InvoiceIQ reads, shown here for reference.
# ══════════════════════════════════════════════════════════════════════════════
def page_master_data():
    st.title("Master Data")

    def _md_pill(val: str, cmap: dict) -> str:
        v = str(val).strip().lower()
        fg, bg = cmap.get(v, ("#8B8FA8", "rgba(139,143,168,0.12)"))
        lbl = v.replace("_", " ").replace("-", "‑").title()
        return (
            f"<span style='background:{bg}; color:{fg}; border:1px solid {fg}; "
            f"border-radius:12px; padding:2px 9px; font-size:0.74rem; "
            f"font-weight:600; white-space:nowrap;'>{lbl}</span>"
        )

    def _md_tbl(col_defs: list, rows_html: str) -> str:
        th_b = (
            "padding:0.5rem 0.9rem; color:#8B8FA8; font-size:0.77rem; "
            "font-weight:600; letter-spacing:0.05em; text-transform:uppercase; "
            "border-bottom:1px solid #2A2D3E; white-space:nowrap;"
        )
        ths = ""
        for lbl, ra in col_defs:
            align = "right" if ra else "left"
            ths += f"<th style='{th_b} text-align:{align};'>{lbl}</th>"
        return (
            "<div style='background:#1E2130; border-radius:8px; overflow:auto; "
            "border:1px solid #2A2D3E; margin-bottom:0.4rem;'>"
            "<table style='width:100%; border-collapse:collapse;'>"
            f"<thead><tr style='background:#161929;'>{ths}</tr></thead>"
            f"<tbody>{rows_html}</tbody></table></div>"
        )

    if not _masters_ok():
        st.markdown(
            "<div style='background:rgba(255,92,92,0.09); border-left:4px solid #FF5C5C; "
            "border-radius:6px; padding:0.7rem 1.1rem; color:#FF5C5C; font-size:0.88rem;'>"
            "Master CSVs not found in this folder.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Vendors ───────────────────────────────────────────────────────────────
    _sec_hdr("Vendors")
    _vc = {
        "active":       ("#00C48C", "rgba(0,196,140,0.12)"),
        "inactive":     ("#8B8FA8", "rgba(139,143,168,0.12)"),
        "under_review": ("#FFB547", "rgba(255,181,71,0.12)"),
        "blacklisted":  ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    vr = _csv_rows("vendor_master.csv")
    rows_h = ""
    for i, r in enumerate(vr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        lim = _indian_fmt(r.get("approval_limit_inr", 0))
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; white-space:nowrap;'>"
            f"{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-size:0.84rem;'>"
            f"{r.get('category','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-weight:600; "
            f"text-align:right; white-space:nowrap;'>{lim}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>{_md_pill(r.get('status',''), _vc)}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('suggested_gl_code','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("Vendor Name", False), ("Category", False),
             ("Approval Limit (₹)", True), ("Status", False), ("GL Code", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )

    # ── Purchase Orders ───────────────────────────────────────────────────────
    _sec_hdr("Purchase Orders")
    _pc = {
        "open":      ("#4F8EF7", "rgba(79,142,247,0.12)"),
        "closed":    ("#00C48C", "rgba(0,196,140,0.12)"),
        "cancelled": ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    por = _csv_rows("po_master.csv")
    rows_h = ""
    for i, r in enumerate(por):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        amt = _indian_fmt(r.get("po_amount_inr", 0))
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('po_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0;'>{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-weight:600; "
            f"text-align:right; white-space:nowrap;'>{amt}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>{_md_pill(r.get('status',''), _pc)}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('gl_code','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("PO Number", False), ("Vendor", False), ("PO Amount (₹)", True),
             ("Status", False), ("GL Code", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )

    # ── GRNs ──────────────────────────────────────────────────────────────────
    _sec_hdr("Goods Receipt Notes")
    _gc = {
        "received": ("#00C48C", "rgba(0,196,140,0.12)"),
        "partial":  ("#FFB547", "rgba(255,181,71,0.12)"),
    }
    gr = _csv_rows("grn_master.csv")
    rows_h = ""
    for i, r in enumerate(gr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('grn_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('po_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0;'>{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-size:0.84rem;'>"
            f"{r.get('received_date','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>{_md_pill(r.get('grn_status',''), _gc)}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("GRN Number", False), ("PO Number", False), ("Vendor", False),
             ("Received Date", False), ("Status", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )

    # ── GL Codes ──────────────────────────────────────────────────────────────
    _sec_hdr("GL Codes")
    gl = _csv_rows("gl_master.csv")
    rows_h = ""
    for i, r in enumerate(gl):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('gl_code','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0;'>{r.get('description','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-size:0.84rem;'>"
            f"{r.get('category','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-size:0.84rem;'>"
            f"{r.get('valid_for_categories','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("GL Code", False), ("Description", False), ("Category", False),
             ("Valid For", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )

    # ── Invoice History ───────────────────────────────────────────────────────
    _sec_hdr("Invoice History")
    _ic = {
        "approved": ("#00C48C", "rgba(0,196,140,0.12)"),
        "paid":     ("#4F8EF7", "rgba(79,142,247,0.12)"),
        "pending":  ("#FFB547", "rgba(255,181,71,0.12)"),
        "on-hold":  ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    hist = _csv_rows("invoices.csv")
    rows_h = ""
    for i, r in enumerate(hist):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        amt = _indian_fmt(r.get("amount_inr", 0))
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-family:monospace; "
            f"font-size:0.84rem;'>{r.get('invoice_id','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0;'>{r.get('vendor','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-weight:600; "
            f"text-align:right; white-space:nowrap;'>{amt}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>{_md_pill(r.get('status',''), _ic)}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; font-size:0.84rem;'>"
            f"{r.get('invoice_date','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("Invoice ID", False), ("Vendor", False), ("Amount (₹)", True),
             ("Status", False), ("Date", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if page == "Pipeline":
    page_pipeline()
elif page == "Agent Reports":
    page_agent_reports()
elif page == "Comparison":
    page_comparison()
elif page == "Master Data":
    page_master_data()
