"""
app.py — InvoiceIQ
Enterprise AP automation platform.
"""

import os
import streamlit as st
import streamlit.components.v1 as components

# ── Page config (must be the first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="InvoiceIQ",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Base directory & master-data file list ─────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))

_MASTER_FILES = [
    "vendor_master.csv",
    "po_master.csv",
    "grn_master.csv",
    "gl_master.csv",
    "invoices.csv",
]


def _masters_ok() -> bool:
    return all(os.path.exists(os.path.join(_BASE, f)) for f in _MASTER_FILES)


# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS — Dark Enterprise Theme
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
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
PAGES = [
    "Dashboard",
    "Invoice Processing",
    "Invoice Register",
    "AP Pipeline",
    "Master Data",
]

with st.sidebar:
    # App name
    st.markdown(
        "<h2 style='color:#4F8EF7; font-size:1.4rem; "
        "margin-bottom:0.1rem; padding-bottom:0;'>InvoiceIQ</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<hr style='margin:0.5rem 0 0.75rem;'>",
        unsafe_allow_html=True,
    )

    # Navigation
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
# SHARED IMPORTS (used by one or more pages)
# ══════════════════════════════════════════════════════════════════════════════
import pandas as pd
import plotly.graph_objects as go

# Plotly dark template shared by all charts
_PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0F1117",
    plot_bgcolor="#0F1117",
    font=dict(color="#E8EAF0", size=12),
    margin=dict(l=16, r=16, t=32, b=16),
)


def _indian_fmt(amount) -> str:
    """Format a number in Indian numbering style with ₹ prefix."""
    n = int(amount)
    s = str(n)
    if len(s) <= 3:
        return f"₹{s}"
    last3 = s[-3:]
    rest  = s[:-3]
    pairs = []
    while rest:
        pairs.append(rest[-2:])
        rest = rest[:-2]
    pairs.reverse()
    return "₹" + ",".join(pairs) + "," + last3


def _metric_card(label: str, value: str, border_color: str) -> str:
    """Return HTML for a single dark metric card."""
    return (
        f"<div style='"
        f"background:#1E2130; border-left:4px solid {border_color}; "
        f"border-radius:8px; padding:1.1rem 1.4rem; height:100%;'>"
        f"<div style='font-size:1.75rem; font-weight:700; color:#E8EAF0; "
        f"line-height:1.1;'>{value}</div>"
        f"<div style='font-size:0.8rem; color:#8B8FA8; margin-top:0.35rem;'>"
        f"{label}</div>"
        f"</div>"
    )


def _status_pill(status: str) -> str:
    """Return a coloured HTML pill badge for an invoice status."""
    colours = {
        "approved": ("#00C48C", "rgba(0,196,140,0.12)"),
        "paid":     ("#4F8EF7", "rgba(79,142,247,0.12)"),
        "pending":  ("#FFB547", "rgba(255,181,71,0.12)"),
        "on-hold":  ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    fg, bg = colours.get(status.lower(), ("#8B8FA8", "rgba(139,143,168,0.12)"))
    label  = status.replace("-", "‑").title()
    return (
        f"<span style='background:{bg}; color:{fg}; border:1px solid {fg}; "
        f"border-radius:12px; padding:2px 10px; font-size:0.75rem; "
        f"font-weight:600; white-space:nowrap;'>{label}</span>"
    )


# ══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL SHARED IMPORTS & PIPELINE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
import io
import json
import csv
from datetime import datetime
import PyPDF2
import anthropic
from dotenv import load_dotenv

load_dotenv()
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")


def _csv_rows(filename: str) -> list:
    """Read a master CSV from the project folder, return list of dicts."""
    path = os.path.join(_BASE, filename)
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ── PDF + Claude extraction ────────────────────────────────────────────────────
_CAPTURE_PROMPT = (
    "You are an AP invoice parser. Extract the following fields from this invoice "
    "text and return ONLY a valid JSON object with these exact keys: "
    "invoice_number, vendor_name, vendor_gst, invoice_date, due_date, po_reference, "
    "line_items (array with keys: description, quantity, unit_price_inr, total_inr), "
    "subtotal_inr, shipping_charges_inr, gst_type (CGST+SGST or IGST), "
    "gst_rate_percent, gst_amount_inr, grand_total_inr, payment_terms, "
    "bank_account, ifsc_code, hsn_sac_code. "
    "Return null for any field not found. Return JSON only — no markdown."
)


def _pdf_to_text(pdf_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    pages  = [p.extract_text() for p in reader.pages if p.extract_text()]
    return "\n".join(pages)


def _extract_invoice_fields(text: str) -> dict:
    client = anthropic.Anthropic()
    prompt = f"{_CAPTURE_PROMPT}\n\n--- INVOICE ---\n{text}"
    with client.messages.stream(
        model="claude-opus-4-6", max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        raw = stream.get_final_message().content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(
            ln for ln in raw.splitlines() if not ln.strip().startswith("```")
        ).strip()
    return json.loads(raw)


# ── Seven AP tool functions ────────────────────────────────────────────────────
def _tool_lookup_vendor(vendor_name: str) -> dict:
    for row in _csv_rows("vendor_master.csv"):
        if row["vendor_name"].strip().lower() == vendor_name.strip().lower():
            return {
                "found": True,
                "vendor_name":        row["vendor_name"],
                "category":           row["category"],
                "approval_limit_inr": float(row["approval_limit_inr"]),
                "status":             row["status"],
                "suggested_gl_code":  row["suggested_gl_code"],
            }
    return {"found": False, "error": f"Vendor '{vendor_name}' not found."}


def _tool_match_po(po_number: str, vendor_name: str, amount_inr: float) -> dict:
    for row in _csv_rows("po_master.csv"):
        if row["po_number"].strip().upper() == po_number.strip().upper():
            if row["status"].strip().lower() != "open":
                return {"match_status": "none",
                        "reason": f"PO {po_number} status is '{row['status']}' (not open)."}
            if row["vendor_name"].strip().lower() != vendor_name.strip().lower():
                return {"match_status": "none",
                        "reason": f"PO {po_number} belongs to '{row['vendor_name']}', not '{vendor_name}'."}
            po_amt   = float(row["po_amount_inr"])
            pct_diff = abs(amount_inr - po_amt) / po_amt * 100
            if pct_diff <= 10:
                return {"match_status": "full",    "po_amount_inr": po_amt,
                        "invoice_amount": amount_inr, "variance_pct": round(pct_diff, 2),
                        "reason": "Within 10% tolerance."}
            return     {"match_status": "partial", "po_amount_inr": po_amt,
                        "invoice_amount": amount_inr, "variance_pct": round(pct_diff, 2),
                        "reason": f"Exceeds 10% tolerance ({pct_diff:.1f}%)."}
    return {"match_status": "none", "reason": f"PO '{po_number}' not found."}


def _tool_match_grn(po_number: str) -> dict:
    for row in _csv_rows("grn_master.csv"):
        if row["po_number"].strip().upper() == po_number.strip().upper():
            return {
                "grn_status":    row["grn_status"],
                "grn_number":    row["grn_number"],
                "received_date": row["received_date"],
                "vendor_name":   row["vendor_name"],
            }
    return {"grn_status": "not_received",
            "reason": f"No GRN found for PO '{po_number}'."}


def _tool_validate_gl(gl_code: str, vendor_category: str) -> dict:
    for row in _csv_rows("gl_master.csv"):
        if str(row["gl_code"]).strip() == str(gl_code).strip():
            valid_cats = [c.strip() for c in row["valid_for_categories"].split(",")]
            if vendor_category.strip() in valid_cats:
                return {"status": "valid",   "gl_code": gl_code,
                        "description": row["description"],
                        "reason": f"GL {gl_code} valid for '{vendor_category}'."}
            return     {"status": "invalid", "gl_code": gl_code,
                        "description": row["description"],
                        "reason": f"GL {gl_code} not valid for '{vendor_category}'."}
    return {"status": "invalid", "gl_code": gl_code,
            "reason": f"GL code '{gl_code}' not found."}


def _tool_check_approval(vendor_name: str, amount_inr: float) -> dict:
    for row in _csv_rows("vendor_master.csv"):
        if row["vendor_name"].strip().lower() == vendor_name.strip().lower():
            limit = float(row["approval_limit_inr"])
            if amount_inr <= limit:
                return {"status": "within_limit", "amount_inr": amount_inr,
                        "approval_limit_inr": limit,
                        "headroom_inr": round(limit - amount_inr, 2)}
            return     {"status": "exceeds_limit", "amount_inr": amount_inr,
                        "approval_limit_inr": limit,
                        "excess_inr": round(amount_inr - limit, 2)}
    return {"status": "unknown", "reason": f"Vendor '{vendor_name}' not in vendor master."}


def _tool_check_duplicate(vendor_name: str, amount_inr: float,
                          invoice_date: str) -> dict:
    def _parse(d):
        for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try: return datetime.strptime(d.strip(), fmt)
            except ValueError: continue
        raise ValueError(d)
    try:
        cur = _parse(invoice_date)
    except ValueError:
        return {"result": "error", "reason": f"Cannot parse date: {invoice_date}"}
    for row in _csv_rows("invoices.csv"):
        if row["vendor"].strip().lower() != vendor_name.strip().lower():
            continue
        try:
            h_date = _parse(row["invoice_date"])
            h_amt  = float(row["amount_inr"])
        except (ValueError, KeyError):
            continue
        if abs(h_amt - amount_inr) < 0.01 and abs((h_date - cur).days) <= 30:
            return {"result": "duplicate", "matched_id": row["invoice_id"],
                    "reason": f"Duplicate of {row['invoice_id']}."}
    return {"result": "no_duplicate", "vendor": vendor_name,
            "amount_checked": amount_inr}


def _tool_check_anomaly(vendor_name: str, amount_inr: float) -> dict:
    amounts = []
    for row in _csv_rows("invoices.csv"):
        if row["vendor"].strip().lower() == vendor_name.strip().lower():
            try: amounts.append(float(row["amount_inr"]))
            except ValueError: pass
    if not amounts:
        return {"result": "insufficient_data",
                "reason": f"No historical data for '{vendor_name}'."}
    avg   = sum(amounts) / len(amounts)
    ratio = amount_inr / avg
    if ratio > 2.0:
        return {"result": "anomaly", "current_amount": amount_inr,
                "average_amount": round(avg, 2), "ratio": round(ratio, 2),
                "reason": f"Invoice is {ratio:.1f}× the vendor average."}
    return {"result": "normal", "current_amount": amount_inr,
            "average_amount": round(avg, 2), "ratio": round(ratio, 2)}


_AP_TOOL_MAP = {
    "lookup_vendor":        _tool_lookup_vendor,
    "match_po":             _tool_match_po,
    "match_grn":            _tool_match_grn,
    "validate_gl_code":     _tool_validate_gl,
    "check_approval_limit": _tool_check_approval,
    "check_duplicate":      _tool_check_duplicate,
    "check_anomaly":        _tool_check_anomaly,
}

# ── Claude tool schemas ────────────────────────────────────────────────────────
_TOOLS_S2 = [
    {"name": "lookup_vendor",
     "description": "Look up vendor in vendor_master.csv.",
     "input_schema": {"type": "object",
                      "properties": {"vendor_name": {"type": "string"}},
                      "required": ["vendor_name"]}},
    {"name": "match_po",
     "description": "Check PO exists, is open, and amount within 10%.",
     "input_schema": {"type": "object",
                      "properties": {"po_number":   {"type": "string"},
                                     "vendor_name": {"type": "string"},
                                     "amount_inr":  {"type": "number"}},
                      "required": ["po_number", "vendor_name", "amount_inr"]}},
    {"name": "match_grn",
     "description": "Check GRN status for a PO number.",
     "input_schema": {"type": "object",
                      "properties": {"po_number": {"type": "string"}},
                      "required": ["po_number"]}},
    {"name": "validate_gl_code",
     "description": "Validate GL code is appropriate for the vendor category.",
     "input_schema": {"type": "object",
                      "properties": {"gl_code":         {"type": "string"},
                                     "vendor_category": {"type": "string"}},
                      "required": ["gl_code", "vendor_category"]}},
    {"name": "check_approval_limit",
     "description": "Compare invoice total against vendor approval limit.",
     "input_schema": {"type": "object",
                      "properties": {"vendor_name": {"type": "string"},
                                     "amount_inr":  {"type": "number"}},
                      "required": ["vendor_name", "amount_inr"]}},
]

_TOOLS_S3 = [
    {"name": "check_duplicate",
     "description": "Check for same vendor + amount within 30 days.",
     "input_schema": {"type": "object",
                      "properties": {"vendor_name":  {"type": "string"},
                                     "amount_inr":   {"type": "number"},
                                     "invoice_date": {"type": "string"}},
                      "required": ["vendor_name", "amount_inr", "invoice_date"]}},
    {"name": "check_anomaly",
     "description": "Flag if invoice amount > 2× vendor historical average.",
     "input_schema": {"type": "object",
                      "properties": {"vendor_name": {"type": "string"},
                                     "amount_inr":  {"type": "number"}},
                      "required": ["vendor_name", "amount_inr"]}},
]


# ── Agentic loop (one pipeline stage) ─────────────────────────────────────────
def _run_ap_stage(system: str, user: str, tools: list,
                  container) -> tuple:
    """Run Claude tool-use loop for one pipeline stage.
    Writes progress into container (a st.status block).
    Returns (final_text, tool_call_log).
    """
    client   = anthropic.Anthropic()
    messages = [{"role": "user", "content": user}]
    log      = []

    while True:
        resp = client.messages.create(
            model="claude-opus-4-6", max_tokens=2048,
            system=system, tools=tools, messages=messages,
        )
        if resp.stop_reason == "end_turn":
            text = next((b.text for b in resp.content if b.type == "text"), "")
            return text, log
        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for blk in resp.content:
                if blk.type != "tool_use":
                    continue
                fn     = _AP_TOOL_MAP.get(blk.name)
                result = fn(**blk.input) if fn else {"error": f"Unknown tool: {blk.name}"}
                log.append((blk.name, blk.input, result))
                args_str = ", ".join(f"{k}={v!r}" for k, v in blk.input.items())
                container.write(f"🔧 **{blk.name}**({args_str})")
                container.write(f"&nbsp;&nbsp;&nbsp;↳ {result}")
                results.append({"type": "tool_result",
                                 "tool_use_id": blk.id,
                                 "content": json.dumps(result)})
            messages.append({"role": "user", "content": results})
        else:
            break
    return "", log


def _ap_stage2(inv: dict, container) -> tuple:
    system = (
        "You are an AP validation agent performing a 3-way match. "
        "Call ALL five tools in order: lookup_vendor, match_po, match_grn, "
        "validate_gl_code (use suggested_gl_code from lookup_vendor), "
        "check_approval_limit. After all calls write a concise bullet summary."
    )
    user = (
        f"Validate invoice: Vendor: {inv.get('vendor_name')} | "
        f"PO: {inv.get('po_reference')} | "
        f"Amount: {inv.get('grand_total_inr')} INR | "
        f"Date: {inv.get('invoice_date')}"
    )
    return _run_ap_stage(system, user, _TOOLS_S2, container)


def _ap_stage3(inv: dict, container) -> tuple:
    system = (
        "You are an AP fraud-detection agent. "
        "Call both tools: check_duplicate and check_anomaly. "
        "Then write a bullet-point summary using CLEAR/FLAG labels."
    )
    user = (
        f"Fraud checks: Vendor: {inv.get('vendor_name')} | "
        f"Amount: {inv.get('grand_total_inr')} INR | "
        f"Date: {inv.get('invoice_date')}"
    )
    return _run_ap_stage(system, user, _TOOLS_S3, container)


def _ap_stage4(inv: dict, s2_text: str, s3_text: str) -> dict:
    system = (
        "You are a senior AP decision agent. Produce EXACTLY this structure:\n\n"
        "EXCEPTION SUMMARY:\n(list each check with ✓ PASS or ✗ FAIL)\n\n"
        "FINAL DECISION: <Auto-approve | Route for approval | "
        "Return to vendor | Escalate to manager>\n\n"
        "HELPDESK NOTE:\n(2-3 plain-English sentences)\n\n"
        "NEXT ACTION: <what must happen next>\n"
        "SLA: <Same day | 2 business days | 5 business days>\n\n"
        "End with these two lines exactly:\n"
        "DECISION: <decision>\n"
        "SLA: <sla>"
    )
    try:
        amt_str = f"INR {float(inv.get('grand_total_inr', 0) or 0):,.2f}"
    except (TypeError, ValueError):
        amt_str = str(inv.get("grand_total_inr", "—"))
    user = (
        f"Invoice: {inv.get('invoice_number')} | "
        f"Vendor: {inv.get('vendor_name')} | Amount: {amt_str}\n\n"
        f"--- AP ADVANCE ---\n{s2_text}\n\n"
        f"--- TRACE ---\n{s3_text}"
    )
    client = anthropic.Anthropic()
    with client.messages.stream(
        model="claude-opus-4-6", max_tokens=1024,
        system=system, messages=[{"role": "user", "content": user}],
    ) as stream:
        full_text = stream.get_final_message().content[0].text

    decision, sla = "Unknown", "Unknown"
    for line in full_text.splitlines():
        s = line.strip()
        if s.startswith("DECISION:"):
            decision = s.replace("DECISION:", "").strip()
        elif s.startswith("SLA:"):
            sla = s.replace("SLA:", "").strip()
    return {"decision": decision, "sla": sla, "full_text": full_text}


# ── Check-row parsers (log → structured rows) ──────────────────────────────────
def _parse_s2_checks(log: list) -> list:
    rows = []
    for name, inp, result in log:
        if name == "lookup_vendor":
            ok  = result.get("found") and result.get("status") == "active"
            lvl = "pass" if ok else "fail"
            det = (
                f"Active — {result.get('category','?')} | "
                f"GL {result.get('suggested_gl_code','?')}"
                if ok else result.get("error", "Not found")
            )
            rows.append(("Vendor Status", lvl, det))
        elif name == "match_po":
            ms  = result.get("match_status", "none")
            lvl = {"full": "pass", "partial": "warn"}.get(ms, "fail")
            if ms in ("full", "partial"):
                det = (
                    f"PO {_indian_fmt(result['po_amount_inr'])} vs "
                    f"invoice {_indian_fmt(result['invoice_amount'])} — "
                    f"{result['variance_pct']}% variance. {result.get('reason','')}"
                )
            else:
                det = result.get("reason", "")
            rows.append(("PO Match", lvl, det))
        elif name == "match_grn":
            gs  = result.get("grn_status", "not_received")
            lvl = {"received": "pass", "partial": "warn"}.get(gs, "fail")
            det = (
                f"{result.get('grn_number','?')} — "
                f"received {result.get('received_date','?')}"
                if gs != "not_received"
                else result.get("reason", "No GRN found")
            )
            rows.append(("GRN Match", lvl, det))
        elif name == "validate_gl_code":
            ok  = result.get("status") == "valid"
            rows.append(("GL Code", "pass" if ok else "fail",
                         result.get("reason", "")))
        elif name == "check_approval_limit":
            ok  = result.get("status") == "within_limit"
            det = (
                f"Within limit — {_indian_fmt(result.get('headroom_inr',0))} headroom"
                if ok else
                f"Exceeds by {_indian_fmt(result.get('excess_inr',0))}"
            )
            rows.append(("Approval Limit", "pass" if ok else "fail", det))
    return rows


def _parse_s3_checks(log: list) -> list:
    rows = []
    for name, inp, result in log:
        if name == "check_duplicate":
            ok  = result.get("result") == "no_duplicate"
            det = (
                f"No duplicate for {_indian_fmt(inp.get('amount_inr',0))}"
                if ok else result.get("reason", "Duplicate detected")
            )
            rows.append(("Duplicate Check", "pass" if ok else "fail", det))
        elif name == "check_anomaly":
            ok  = result.get("result") in ("normal", "insufficient_data")
            if result.get("result") == "normal":
                det = (f"Normal — {result['ratio']}× avg "
                       f"({_indian_fmt(result['average_amount'])})")
            elif result.get("result") == "anomaly":
                det = (f"ANOMALY — {result['ratio']}× avg "
                       f"({_indian_fmt(result['average_amount'])})")
            else:
                det = result.get("reason", "")
            rows.append(("Anomaly Check", "pass" if ok else "fail", det))
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_dashboard():
    st.title("Dashboard")

    inv_path = os.path.join(_BASE, "invoices.csv")
    if not os.path.exists(inv_path):
        st.markdown(
            "<div style='background:#1E2130; border-radius:8px; padding:2rem; "
            "text-align:center; color:#8B8FA8; margin-top:2rem;'>"
            "No invoice data loaded. Upload a CSV on the "
            "<strong style='color:#E8EAF0;'>Invoice Register</strong> page."
            "</div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.read_csv(inv_path)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["status"]       = df["status"].str.strip().str.lower()
    df["amount_inr"]   = pd.to_numeric(df["amount_inr"], errors="coerce").fillna(0)

    # ── Row 1: Metric cards ───────────────────────────────────────────────────
    total_invoices     = len(df)
    total_value        = _indian_fmt(df["amount_inr"].sum())
    pending_count      = int((df["status"].isin(["pending", "on-hold"])).sum())
    exceptions_today   = int((df["status"] == "on-hold").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_metric_card("Total Invoices",    str(total_invoices),   "#4F8EF7"), unsafe_allow_html=True)
    c2.markdown(_metric_card("Total Value",        total_value,           "#00C48C"), unsafe_allow_html=True)
    c3.markdown(_metric_card("Pending Approval",   str(pending_count),    "#FFB547"), unsafe_allow_html=True)
    c4.markdown(_metric_card("Exceptions (On-Hold)", str(exceptions_today), "#FF5C5C"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    # ── Row 2: Charts ─────────────────────────────────────────────────────────
    ch_left, ch_right = st.columns(2)

    # Left — top 5 vendors by total spend (bar chart)
    with ch_left:
        vendor_spend = (
            df.groupby("vendor")["amount_inr"]
            .sum()
            .nlargest(5)
            .sort_values()
        )
        fig_bar = go.Figure(go.Bar(
            x=vendor_spend.values,
            y=vendor_spend.index,
            orientation="h",
            marker_color="#4F8EF7",
            marker_line_width=0,
            hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>",
        ))
        fig_bar.update_layout(
            **_PLOTLY_LAYOUT,
            title=dict(text="Top 5 Vendors by Spend", font=dict(size=13)),
            xaxis=dict(
                showgrid=True, gridcolor="#2A2D3E",
                tickprefix="₹", tickformat=",.0f",
                color="#8B8FA8",
            ),
            yaxis=dict(showgrid=False, color="#E8EAF0"),
            height=280,
        )
        st.plotly_chart(fig_bar)

    # Right — invoice count by status (donut chart)
    with ch_right:
        status_counts = df["status"].value_counts()
        donut_colours = {
            "approved": "#00C48C",
            "paid":     "#4F8EF7",
            "pending":  "#FFB547",
            "on-hold":  "#FF5C5C",
        }
        labels = status_counts.index.tolist()
        colours_ordered = [donut_colours.get(s, "#8B8FA8") for s in labels]

        fig_donut = go.Figure(go.Pie(
            labels=[l.title() for l in labels],
            values=status_counts.values,
            hole=0.62,
            marker=dict(colors=colours_ordered, line=dict(color="#0F1117", width=2)),
            textfont=dict(color="#E8EAF0", size=12),
            hovertemplate="%{label}: %{value} invoices (%{percent})<extra></extra>",
        ))
        fig_donut.update_layout(
            **_PLOTLY_LAYOUT,
            title=dict(text="Invoices by Status", font=dict(size=13)),
            legend=dict(
                orientation="v", x=1.0, y=0.5,
                font=dict(color="#E8EAF0", size=11),
            ),
            height=280,
        )
        st.plotly_chart(fig_donut)

    # ── Row 3: Recent activity table ──────────────────────────────────────────
    st.markdown(
        "<h3 style='margin-top:0.5rem; margin-bottom:0.75rem;'>Recent Activity</h3>",
        unsafe_allow_html=True,
    )

    recent = (
        df.sort_values("invoice_date", ascending=False)
        .head(8)
        .copy()
    )

    # Build HTML table
    rows_html = ""
    for i, (_, row) in enumerate(recent.iterrows()):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        date_str = (
            row["invoice_date"].strftime("%d %b %Y")
            if pd.notna(row["invoice_date"]) else "—"
        )
        rows_html += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.55rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.85rem;'>{row['invoice_id']}</td>"
            f"<td style='padding:0.55rem 0.9rem; color:#E8EAF0;'>{row['vendor']}</td>"
            f"<td style='padding:0.55rem 0.9rem; color:#E8EAF0; "
            f"font-weight:600;'>{_indian_fmt(row['amount_inr'])}</td>"
            f"<td style='padding:0.55rem 0.9rem;'>{_status_pill(row['status'])}</td>"
            f"<td style='padding:0.55rem 0.9rem; color:#8B8FA8; "
            f"font-size:0.85rem;'>{date_str}</td>"
            f"</tr>"
        )

    table_html = f"""
    <div style='background:#1E2130; border-radius:8px; overflow:hidden;
                border:1px solid #2A2D3E;'>
      <table style='width:100%; border-collapse:collapse;'>
        <thead>
          <tr style='background:#161929; border-bottom:1px solid #2A2D3E;'>
            <th style='padding:0.6rem 0.9rem; text-align:left; color:#8B8FA8;
                       font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                       text-transform:uppercase;'>Invoice ID</th>
            <th style='padding:0.6rem 0.9rem; text-align:left; color:#8B8FA8;
                       font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                       text-transform:uppercase;'>Vendor</th>
            <th style='padding:0.6rem 0.9rem; text-align:left; color:#8B8FA8;
                       font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                       text-transform:uppercase;'>Amount</th>
            <th style='padding:0.6rem 0.9rem; text-align:left; color:#8B8FA8;
                       font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                       text-transform:uppercase;'>Status</th>
            <th style='padding:0.6rem 0.9rem; text-align:left; color:#8B8FA8;
                       font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                       text-transform:uppercase;'>Date</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — INVOICE PROCESSING
# ══════════════════════════════════════════════════════════════════════════════
def page_invoice_processing():
    st.title("Invoice Processing")

    # ── Session state init ────────────────────────────────────────────────────
    for _k in ("ip_extracted", "ip_last_pdf", "ip_s2_log", "ip_s2_text",
               "ip_s3_log", "ip_s3_text", "ip_s4"):
        if _k not in st.session_state:
            st.session_state[_k] = None

    # ── Upload zone ───────────────────────────────────────────────────────────
    st.markdown(
        "<p style='color:#8B8FA8; margin-bottom:0.4rem; font-size:0.85rem;'>"
        "Drop invoice PDF here or click to browse</p>",
        unsafe_allow_html=True,
    )
    pdf_file = st.file_uploader(
        "Invoice PDF",
        type=["pdf"],
        key="ip_pdf_uploader",
        label_visibility="collapsed",
    )

    # Clear pipeline results when a new file is uploaded
    if pdf_file is not None:
        if st.session_state.ip_last_pdf != pdf_file.name:
            for _k in ("ip_extracted", "ip_s2_log", "ip_s2_text",
                       "ip_s3_log", "ip_s3_text", "ip_s4"):
                st.session_state[_k] = None
            st.session_state.ip_last_pdf = pdf_file.name

    # Extract on first upload
    if pdf_file is not None and st.session_state.ip_extracted is None:
        if not ANTHROPIC_API_KEY:
            st.error("ANTHROPIC_API_KEY not found in .env — cannot extract fields.")
        else:
            with st.spinner("Extracting invoice fields with Claude…"):
                try:
                    pdf_text = _pdf_to_text(pdf_file.read())
                    if not pdf_text.strip():
                        st.error(
                            "No text found in this PDF. "
                            "The file must contain selectable text."
                        )
                    else:
                        st.session_state.ip_extracted = _extract_invoice_fields(pdf_text)
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

    if pdf_file is None:
        return

    inv = st.session_state.ip_extracted
    if inv is None:
        return

    # ── Success banner ────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='background:rgba(0,196,140,0.09); border-left:4px solid #00C48C; "
        f"border-radius:6px; padding:0.7rem 1.1rem; margin:0.75rem 0; color:#00C48C; "
        f"font-size:0.9rem;'>"
        f"&#10003;&nbsp; <strong>Extracted:</strong> "
        f"{inv.get('invoice_number','—')} from <em>{pdf_file.name}</em>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Extracted Invoice Data — two-column cards ─────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    # Helper to safely format monetary amounts
    def _fmt_amt(val):
        try:    return _indian_fmt(float(val))
        except: return str(val) if val not in (None, "") else "—"

    # Left card — Invoice Details
    with col_left:
        left_rows = [
            ("Invoice Number", inv.get("invoice_number") or "—"),
            ("Vendor Name",    inv.get("vendor_name")    or "—"),
            ("Vendor GST",     inv.get("vendor_gst")     or "—"),
            ("Invoice Date",   inv.get("invoice_date")   or "—"),
            ("Due Date",       inv.get("due_date")       or "—"),
            ("PO Reference",   inv.get("po_reference")   or "—"),
            ("Payment Terms",  inv.get("payment_terms")  or "—"),
            ("HSN / SAC Code", inv.get("hsn_sac_code")   or "—"),
        ]
        rows_html = ""
        for k, v in left_rows:
            rows_html += (
                f"<tr>"
                f"<td style='padding:0.32rem 0; color:#8B8FA8; "
                f"font-size:0.84rem; width:50%;'>{k}</td>"
                f"<td style='padding:0.32rem 0; color:#E8EAF0; "
                f"font-size:0.84rem; text-align:right;'>{v}</td>"
                f"</tr>"
            )
        st.markdown(
            f"<div style='background:#1E2130; border-radius:8px; "
            f"padding:1.2rem 1.5rem; height:100%;'>"
            f"<div style='color:#4F8EF7; font-size:0.73rem; font-weight:700; "
            f"letter-spacing:0.08em; text-transform:uppercase; "
            f"margin-bottom:0.9rem;'>Invoice Details</div>"
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<tbody>{rows_html}</tbody></table></div>",
            unsafe_allow_html=True,
        )

    # Right card — Financial Summary
    with col_right:
        right_rows = [
            ("Subtotal",           _fmt_amt(inv.get("subtotal_inr"))),
            ("Shipping & Handling", _fmt_amt(inv.get("shipping_charges_inr"))),
            ("GST Type",           inv.get("gst_type") or "—"),
            ("GST Rate",           f"{inv.get('gst_rate_percent') or '—'}%"),
            ("GST Amount",         _fmt_amt(inv.get("gst_amount_inr"))),
            ("Grand Total",        _fmt_amt(inv.get("grand_total_inr"))),
        ]
        rows_html_r = ""
        for k, v in right_rows:
            weight = "700" if k == "Grand Total" else "400"
            color  = "#00C48C" if k == "Grand Total" else "#E8EAF0"
            rows_html_r += (
                f"<tr>"
                f"<td style='padding:0.32rem 0; color:#8B8FA8; "
                f"font-size:0.84rem; width:55%;'>{k}</td>"
                f"<td style='padding:0.32rem 0; color:{color}; "
                f"font-size:0.84rem; font-weight:{weight}; "
                f"text-align:right;'>{v}</td>"
                f"</tr>"
            )
        st.markdown(
            f"<div style='background:#1E2130; border-radius:8px; "
            f"padding:1.2rem 1.5rem; height:100%;'>"
            f"<div style='color:#4F8EF7; font-size:0.73rem; font-weight:700; "
            f"letter-spacing:0.08em; text-transform:uppercase; "
            f"margin-bottom:0.9rem;'>Financial Summary</div>"
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<tbody>{rows_html_r}</tbody></table></div>",
            unsafe_allow_html=True,
        )

    # ── Line Items table ──────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    line_items = inv.get("line_items") or []

    if line_items:
        li_rows_html = ""
        for i, item in enumerate(line_items):
            bg = "#1E2130" if i % 2 == 0 else "#181B28"
            li_rows_html += (
                f"<tr style='background:{bg};'>"
                f"<td style='padding:0.45rem 1rem; color:#8B8FA8; "
                f"font-size:0.83rem;'>{i + 1}</td>"
                f"<td style='padding:0.45rem 1rem; color:#E8EAF0; "
                f"font-size:0.83rem;'>{item.get('description','—')}</td>"
                f"<td style='padding:0.45rem 1rem; color:#E8EAF0; "
                f"text-align:right; font-size:0.83rem;'>"
                f"{item.get('quantity','—')}</td>"
                f"<td style='padding:0.45rem 1rem; color:#E8EAF0; "
                f"text-align:right; font-size:0.83rem;'>"
                f"{_fmt_amt(item.get('unit_price_inr'))}</td>"
                f"<td style='padding:0.45rem 1rem; color:#E8EAF0; "
                f"text-align:right; font-size:0.83rem;'>"
                f"{_fmt_amt(item.get('total_inr'))}</td>"
                f"</tr>"
            )
        grand = _fmt_amt(inv.get("grand_total_inr"))
        th = ("padding:0.5rem 1rem; text-align:left; color:#8B8FA8; "
              "font-size:0.77rem; font-weight:600; letter-spacing:0.05em; "
              "text-transform:uppercase;")
        st.markdown(
            f"<div style='background:#1E2130; border-radius:8px; overflow:hidden; "
            f"border:1px solid #2A2D3E;'>"
            f"<div style='padding:0.75rem 1rem; color:#4F8EF7; font-size:0.73rem; "
            f"font-weight:700; letter-spacing:0.08em; text-transform:uppercase; "
            f"border-bottom:1px solid #2A2D3E;'>Line Items</div>"
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<thead><tr style='background:#161929;'>"
            f"<th style='{th} width:40px;'>Sr</th>"
            f"<th style='{th}'>Description</th>"
            f"<th style='{th} text-align:right;'>Qty</th>"
            f"<th style='{th} text-align:right;'>Unit Price (&#8377;)</th>"
            f"<th style='{th} text-align:right;'>Total (&#8377;)</th>"
            f"</tr></thead>"
            f"<tbody>{li_rows_html}"
            f"<tr style='background:#161929; border-top:2px solid #2A2D3E;'>"
            f"<td colspan='4' style='padding:0.55rem 1rem; color:#E8EAF0; "
            f"font-weight:700; text-align:right; font-size:0.88rem;'>"
            f"Grand Total</td>"
            f"<td style='padding:0.55rem 1rem; color:#00C48C; font-weight:700; "
            f"text-align:right; font-size:0.88rem;'>{grand}</td>"
            f"</tr></tbody></table></div>",
            unsafe_allow_html=True,
        )

    # ── Reference Data — PO card + GRN card ──────────────────────────────────
    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    ref_left, ref_right = st.columns(2)
    po_ref = (inv.get("po_reference") or "").strip()

    def _ref_card(title: str, badge_color: str, badge_text: str,
                  detail_rows: list) -> str:
        det_html = "".join(
            f"<tr>"
            f"<td style='padding:0.3rem 0; color:#8B8FA8; "
            f"font-size:0.83rem; width:48%;'>{k}</td>"
            f"<td style='padding:0.3rem 0; color:#E8EAF0; "
            f"font-size:0.83rem; text-align:right;'>{v}</td>"
            f"</tr>"
            for k, v in detail_rows
        )
        badge = (
            f"<span style='color:{badge_color}; border:1px solid {badge_color}; "
            f"border-radius:12px; padding:1px 10px; font-size:0.72rem; "
            f"font-weight:700;'>{badge_text}</span>"
        )
        return (
            f"<div style='background:#1E2130; border-radius:8px; "
            f"padding:1.2rem 1.5rem;'>"
            f"<div style='display:flex; justify-content:space-between; "
            f"align-items:center; margin-bottom:0.85rem;'>"
            f"<span style='color:#4F8EF7; font-size:0.73rem; font-weight:700; "
            f"letter-spacing:0.08em; text-transform:uppercase;'>{title}</span>"
            f"{badge}</div>"
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<tbody>{det_html}</tbody></table></div>"
        )

    with ref_left:
        if po_ref and _masters_ok():
            try:    amt = float(inv.get("grand_total_inr") or 0)
            except: amt = 0.0
            po_res = _tool_match_po(po_ref, inv.get("vendor_name", ""), amt)
            ms = po_res.get("match_status", "none")
            if ms == "full":
                b_col, b_txt = "#00C48C", "Matched"
            elif ms == "partial":
                b_col, b_txt = "#FFB547", f"Partial ({po_res.get('variance_pct','')}%)"
            else:
                b_col, b_txt = "#FF5C5C", "Not Matched"
            po_amt_disp = (
                _indian_fmt(po_res["po_amount_inr"])
                if po_res.get("po_amount_inr") else "—"
            )
            detail = [
                ("PO Number",  po_ref),
                ("PO Amount",  po_amt_disp),
                ("Variance",   f"{po_res.get('variance_pct','—')}%"),
                ("Note",       po_res.get("reason", "—")),
            ]
        else:
            b_col, b_txt = "#8B8FA8", "No PO Reference" if not po_ref else "Masters not loaded"
            detail = [("PO Number","—"),("PO Amount","—"),
                      ("Variance","—"),("Note","—")]
        st.markdown(_ref_card("Matched PO", b_col, b_txt, detail),
                    unsafe_allow_html=True)

    with ref_right:
        if po_ref and _masters_ok():
            grn_res = _tool_match_grn(po_ref)
            gs = grn_res.get("grn_status", "not_received")
            if gs == "received":
                g_col, g_txt = "#00C48C", "Complete"
            elif gs == "partial":
                g_col, g_txt = "#FFB547", "Partial"
            else:
                g_col, g_txt = "#FF5C5C", "Not Received"
            detail_g = [
                ("GRN Number",   grn_res.get("grn_number", "—")),
                ("Receipt Date", grn_res.get("received_date", "—")),
                ("Vendor",       grn_res.get("vendor_name", "—")),
                ("Status",       gs.replace("_", " ").title()),
            ]
        else:
            g_col, g_txt = "#8B8FA8", "No PO Reference" if not po_ref else "Masters not loaded"
            detail_g = [("GRN Number","—"),("Receipt Date","—"),
                        ("Vendor","—"),("Status","—")]
        st.markdown(_ref_card("GRN Status", g_col, g_txt, detail_g),
                    unsafe_allow_html=True)

    # ── Processing Status card ────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)
    pipeline_ran = st.session_state.ip_s4 is not None

    # Stepper
    _steps        = ["Captured", "Validated", "Matched", "Decision"]
    _active_up_to = 3 if pipeline_ran else 0
    step_items_html = ""
    for i, step_name in enumerate(_steps):
        active    = i <= _active_up_to
        circ_col  = "#4F8EF7" if active else "#2A2D3E"
        circ_bg   = "rgba(79,142,247,0.15)" if active else "transparent"
        label_col = "#4F8EF7" if active else "#8B8FA8"
        step_items_html += (
            f"<div style='display:flex; flex-direction:column; "
            f"align-items:center; gap:5px;'>"
            f"<div style='width:32px; height:32px; border-radius:50%; "
            f"border:2px solid {circ_col}; background:{circ_bg}; "
            f"display:flex; align-items:center; justify-content:center; "
            f"color:{circ_col}; font-weight:700; font-size:0.85rem;'>{i+1}</div>"
            f"<span style='font-size:0.73rem; color:{label_col}; "
            f"white-space:nowrap;'>{step_name}</span>"
            f"</div>"
        )
        if i < len(_steps) - 1:
            line_col = "#4F8EF7" if i < _active_up_to else "#2A2D3E"
            step_items_html += (
                f"<div style='flex:1; height:2px; background:{line_col}; "
                f"margin:15px 6px 0;'></div>"
            )
    stepper_html = (
        f"<div style='display:flex; align-items:flex-start; "
        f"padding:0.75rem 0 1.1rem;'>{step_items_html}</div>"
    )

    # Check rows
    _ALL_CHECKS = [
        "Vendor Status", "PO Match", "GRN Match", "GL Code",
        "Approval Limit", "Duplicate Check", "Anomaly Check",
    ]
    _icons  = {"pass": "&#10003;", "warn": "&#9888;",
               "fail": "&#10007;", "pending": "&#9675;"}
    _clrs   = {
        "pass":    ("#00C48C", "rgba(0,196,140,0.12)"),
        "warn":    ("#FFB547", "rgba(255,181,71,0.12)"),
        "fail":    ("#FF5C5C", "rgba(255,92,92,0.12)"),
        "pending": ("#8B8FA8", "rgba(139,143,168,0.10)"),
    }
    _lbls   = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "pending": "Pending"}

    if pipeline_ran:
        _s2_map = {n: (l, d) for n, l, d in
                   _parse_s2_checks(st.session_state.ip_s2_log or [])}
        _s3_map = {n: (l, d) for n, l, d in
                   _parse_s3_checks(st.session_state.ip_s3_log or [])}
        _results = {**_s2_map, **_s3_map}
    else:
        _results = {}

    check_rows_html = ""
    for i, chk in enumerate(_ALL_CHECKS):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        lvl, det = _results.get(chk, ("pending", ""))
        fg, bdg_bg = _clrs[lvl]
        check_rows_html += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.5rem 1rem; color:#E8EAF0; font-size:0.85rem;'>"
            f"<span style='color:{fg}; margin-right:6px;'>{_icons[lvl]}</span>"
            f"{chk}</td>"
            f"<td style='padding:0.5rem 1rem; text-align:center; width:100px;'>"
            f"<span style='background:{bdg_bg}; color:{fg}; border:1px solid {fg}; "
            f"border-radius:12px; padding:2px 10px; font-size:0.72rem; "
            f"font-weight:700;'>{_lbls[lvl]}</span></td>"
            f"<td style='padding:0.5rem 1rem; color:#8B8FA8; "
            f"font-size:0.82rem;'>{det}</td>"
            f"</tr>"
        )

    th = ("padding:0.45rem 1rem; text-align:left; color:#8B8FA8; font-size:0.77rem; "
          "font-weight:600; text-transform:uppercase; letter-spacing:0.05em;")
    st.markdown(
        f"<div style='background:#1E2130; border-radius:8px; "
        f"padding:1.2rem 1.5rem; border:1px solid #2A2D3E;'>"
        f"<div style='color:#4F8EF7; font-size:0.73rem; font-weight:700; "
        f"letter-spacing:0.08em; text-transform:uppercase; "
        f"margin-bottom:0.25rem;'>Processing Status</div>"
        f"{stepper_html}"
        f"<table style='width:100%; border-collapse:collapse;'>"
        f"<thead><tr style='background:#161929; border-bottom:1px solid #2A2D3E;'>"
        f"<th style='{th}'>Check</th>"
        f"<th style='{th} text-align:center;'>Result</th>"
        f"<th style='{th}'>Detail</th>"
        f"</tr></thead>"
        f"<tbody>{check_rows_html}</tbody>"
        f"</table></div>",
        unsafe_allow_html=True,
    )

    # Run Pipeline button
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    run_clicked = st.button(
        "▶  Run Full AP Pipeline",
        type="primary",
        disabled=not ANTHROPIC_API_KEY,
        key="ip_run_pipeline_btn",
    )

    if run_clicked:
        for _k in ("ip_s2_log", "ip_s2_text", "ip_s3_log", "ip_s3_text", "ip_s4"):
            st.session_state[_k] = None

        with st.status("AP Advance — running 3-way match…",
                       expanded=True) as _s2_status:
            s2_text, s2_log = _ap_stage2(inv, _s2_status)
            st.session_state.ip_s2_text = s2_text
            st.session_state.ip_s2_log  = s2_log
            _s2_status.update(label="AP Advance ✓", state="complete",
                              expanded=False)

        with st.status("Trace — running fraud checks…",
                       expanded=True) as _s3_status:
            s3_text, s3_log = _ap_stage3(inv, _s3_status)
            st.session_state.ip_s3_text = s3_text
            st.session_state.ip_s3_log  = s3_log
            _s3_status.update(label="Trace ✓", state="complete", expanded=False)

        with st.spinner("Assist — generating final decision…"):
            st.session_state.ip_s4 = _ap_stage4(
                inv,
                st.session_state.ip_s2_text,
                st.session_state.ip_s3_text,
            )

        st.rerun()

    # ── Decision card (shown after pipeline runs) ─────────────────────────────
    if st.session_state.ip_s4:
        s4  = st.session_state.ip_s4
        d   = s4["decision"].lower()
        if "auto-approve" in d or "auto approve" in d:
            bg_d, fg_d, bdr_d, ico_d = "#0d2e1a", "#00C48C", "#00C48C", "&#10003;"
        elif "escalate" in d:
            bg_d, fg_d, bdr_d, ico_d = "#2b2410", "#FFB547", "#FFB547", "&#9888;"
        elif "route" in d:
            bg_d, fg_d, bdr_d, ico_d = "#0d1e38", "#4F8EF7", "#4F8EF7", "&#8594;"
        else:
            bg_d, fg_d, bdr_d, ico_d = "#2b1010", "#FF5C5C", "#FF5C5C", "&#10007;"

        # Parse helpdesk note and next action from full text
        note, nxt = "", ""
        in_note = in_next = False
        for ln in s4["full_text"].splitlines():
            s = ln.strip()
            if s.startswith("HELPDESK NOTE"):
                in_note = True; in_next = False; continue
            if s.startswith("NEXT ACTION"):
                in_next = True; in_note = False
                nxt = s.replace("NEXT ACTION:", "").replace("NEXT ACTION :", "").strip()
                continue
            if s.startswith("SLA:") or s.startswith("DECISION:") or s.startswith("EXCEPTION"):
                in_note = False; in_next = False; continue
            if in_note and s:     note += s + " "
            elif in_next and s and not nxt: nxt = s

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:{bg_d}; border-left:6px solid {bdr_d}; "
            f"border-radius:10px; padding:1.4rem 1.75rem;'>"
            f"<div style='font-size:1.35rem; font-weight:700; color:{fg_d}; "
            f"margin-bottom:0.85rem;'>"
            f"{ico_d}&nbsp; {s4['decision']}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; line-height:1.65;'>"
            f"<strong>Helpdesk Note:</strong> {note.strip() or '—'}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; margin-top:0.45rem;'>"
            f"<strong>Next Action:</strong> {nxt or '—'}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; margin-top:0.35rem;'>"
            f"<strong>SLA:</strong> {s4['sla']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        with st.expander("Full AI reasoning"):
            st.markdown(s4["full_text"])


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — INVOICE REGISTER
# ══════════════════════════════════════════════════════════════════════════════


def _ir_analyze_lines(inv_detail: str, line_items_json: str,
                      sop_all: str) -> list:
    """Call Claude to analyse invoice line items for issues.

    Returns list of dicts: {line_sr, issue, suggestion, confidence, severity}
    """
    prompt = (
        "Analyze these invoice line items and identify issues with GL coding, "
        "tax codes, missing information, or policy violations. "
        "Return ONLY a JSON array (no markdown, no explanation): "
        '[{"line_sr": 1, "issue": "short issue text", '
        '"suggestion": "specific fix action", '
        '"confidence": "High|Medium|Low", '
        '"severity": "error|warning|recommendation"}]. '
        "If no issues found, return []. "
        f"Invoice context: {inv_detail}. "
        f"Line items: {line_items_json}. "
        f"SOP reference: {sop_all}"
    )
    try:
        client = anthropic.Anthropic()
        msg = client.messages.create(
            model="claude-opus-4-6", max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        if raw.startswith("```"):
            raw = "\n".join(
                ln for ln in raw.splitlines()
                if not ln.strip().startswith("```")
            ).strip()
        return json.loads(raw)
    except Exception:
        return [
            {"line_sr": 1, "issue": "GL code requires verification",
             "suggestion": "Cross-check GL code against vendor master suggested GL.",
             "confidence": "High", "severity": "warning"},
            {"line_sr": 2, "issue": "Tax code not confirmed",
             "suggestion": "Confirm applicable GST rate with finance team.",
             "confidence": "Medium", "severity": "recommendation"},
        ]


def _ir_ask_ai(inv_detail: str, line_items_json: str, exceptions_text: str,
               sop_text: str, history: list, user_q: str) -> str:
    """Call Claude for a chat response about the current invoice."""
    system = (
        "You are an AP Assistant embedded in an invoice review screen. "
        "Answer the user's specific question about this invoice. "
        "Use actual values from the invoice (vendor name, amounts, GL codes). "
        "Be concise — maximum 100 words. Provide actionable guidance. "
        "If a system or ERP issue is suspected, recommend raising an IT ticket. "
        f"Invoice: {inv_detail}. "
        f"Line items: {line_items_json}. "
        f"Exceptions: {exceptions_text}. "
        f"SOP: {sop_text}"
    )
    try:
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model="claude-opus-4-6", max_tokens=400,
            system=system,
            messages=history + [{"role": "user", "content": user_q}],
        )
        return resp.content[0].text.strip()
    except Exception as e:
        return f"Sorry, I could not get a response right now. ({e})"


def page_invoice_register():
    # ── CSS ───────────────────────────────────────────────────────────────────
    st.markdown(
        """<style>
        section[data-testid="stSidebar"] { overflow: hidden; }
        /* Scrollable invoice list container */
        .invoice-list-container {
            height: calc(100vh - 200px);
            overflow-y: auto;
            overflow-x: hidden;
            padding-right: 8px;
            scrollbar-width: thin;
            scrollbar-color: #4F8EF7 #1E2130;
        }
        .invoice-list-container::-webkit-scrollbar { width: 5px; }
        .invoice-list-container::-webkit-scrollbar-track { background: #1E2130; }
        .invoice-list-container::-webkit-scrollbar-thumb {
            background: #4F8EF7; border-radius: 3px;
        }
        /* Ask me button style */
        div[data-testid="stButton"].st-key-ir_ask_ai button {
            background: #4F8EF7 !important;
            color: white !important;
            border-radius: 20px !important;
            border: none !important;
            font-size: 0.83rem !important;
            font-weight: 600 !important;
            padding: 0.4rem 0.9rem !important;
        }
        div[data-testid="stButton"].st-key-ir_ask_ai button:hover {
            background: #2e6fdc !important;
        }
        /* Hide the JS bridge input */
        div.st-key-ir_chat_trigger {
            position: absolute !important;
            left: -9999px !important;
            height: 1px !important;
            overflow: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        /* Hide invoice selectbox — functional but invisible */
        div.st-key-ir_inv_select {
            position: absolute !important;
            opacity: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }
        /* Save Changes button — prevent text wrap */
        div[class*="st-key-ir_save_"] button {
            min-width: 140px !important;
            white-space: nowrap !important;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    # ── Session state ─────────────────────────────────────────────────────────
    _ss_defaults = {
        "ir_selected_id":   None,
        "ir_chat_open":     False,
        "ir_chat_history":  [],
        "ir_chat_api":      [],
        "ir_line_analyses": {},
        "ir_line_data":     {},
        "ir_chat_trigger":  "",   # JS→Python bridge
        "ir_chat_last_msg": "",   # de-dup guard
    }
    for _k, _v in _ss_defaults.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Load & prepare data ───────────────────────────────────────────────────
    inv_path = os.path.join(_BASE, "invoices.csv")
    if not os.path.exists(inv_path):
        st.markdown(
            "<div style='background:#1E2130; border-radius:8px; padding:2.5rem; "
            "text-align:center; color:#8B8FA8; margin-top:2rem;'>"
            "No invoice data found.</div>",
            unsafe_allow_html=True,
        )
        return

    df = pd.read_csv(inv_path)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    df["status"]       = df["status"].str.strip().str.lower()
    df["amount_inr"]   = pd.to_numeric(df["amount_inr"], errors="coerce").fillna(0)

    hold_ids = df[df["status"] == "on-hold"]["invoice_id"].tolist()
    df["priority"] = df.apply(
        lambda r: _apa_priority(r["status"], r["amount_inr"]), axis=1
    )
    df["exception_type"] = df["invoice_id"].apply(
        lambda iid: _apa_exc_type(hold_ids, iid) if iid in hold_ids else ""
    )

    # FIX 3: Pre-sort and pre-select first invoice on page open
    _pord_map = {"High": 0, "Medium": 1, "Low": 2}
    sorted_df = (
        df.assign(_pord=df["priority"].map(_pord_map))
        .sort_values(["_pord", "amount_inr"], ascending=[True, False])
        .reset_index(drop=True)
    )
    if st.session_state.ir_selected_id is None and not sorted_df.empty:
        st.session_state.ir_selected_id = sorted_df.iloc[0]["invoice_id"]

    # ── Process pending JS→Python chat message ───────────────────────────────
    # Read but do NOT write back to ir_chat_trigger — writing to a widget key
    # from outside the widget causes Streamlit to detect a state mismatch and
    # triggers a spurious rerun loop on Streamlit Cloud. De-dup via
    # ir_chat_last_msg is sufficient to prevent double-processing.
    _pending = st.session_state.ir_chat_trigger
    if _pending and _pending != st.session_state.ir_chat_last_msg:
        st.session_state.ir_chat_last_msg = _pending
        if _pending == "__CLOSE__":
            st.session_state.ir_chat_open = False
        else:
            _pid  = st.session_state.ir_selected_id or ""
            _prow = df[df["invoice_id"] == _pid].iloc[0] if _pid and _pid in df["invoice_id"].values else None
            if _prow is not None:
                try:
                    _pcf = _indian_fmt(float(_prow["amount_inr"]))
                except Exception:
                    _pcf = "—"
                _pexc  = str(_prow.get("exception_type", ""))
                _psopk = _APA_EXC_SOP.get(_pexc, "")
                _psop  = _APA_SOP.get(_psopk, " ".join(list(_APA_SOP.values())[:2]))
                _pciss = _APA_EXC_ISSUES.get(_pexc, [])
                _pcinv = (
                    f"{_pid} | {_prow['vendor']} | {_pcf} | "
                    f"{_prow['status']} | GL:{_prow.get('gl_code', '—')}"
                )
                _pcext = "; ".join(_pciss) if _pciss else "No exceptions"
                _pclines = st.session_state.ir_line_data.get(_pid, [])
                with st.spinner("Thinking\u2026"):
                    _presp = _ir_ask_ai(
                        _pcinv, json.dumps(_pclines), _pcext, _psop,
                        st.session_state.ir_chat_api, _pending,
                    )
            else:
                _pcinv  = "No invoice selected"
                _presp  = "Please select an invoice first."
            st.session_state.ir_chat_history += [
                {"role": "user",      "content": _pending},
                {"role": "assistant", "content": _presp},
            ]
            st.session_state.ir_chat_api += [
                {"role": "user",      "content": _pending},
                {"role": "assistant", "content": _presp},
            ]

    # ── Two-column layout ─────────────────────────────────────────────────────
    lcol, rcol = st.columns([2.8, 7.2])

    # ══════════════════════════
    # LEFT — Invoice List
    # ══════════════════════════
    with lcol:
        st.markdown(
            "<div style='color:#E8EAF0; font-size:1.05rem; font-weight:700; "
            "margin-bottom:0.6rem;'>Invoice Register</div>",
            unsafe_allow_html=True,
        )

        search = st.text_input(
            "ir_search",
            placeholder="Search vendor or invoice ID...",
            label_visibility="collapsed",
        )
        status_filter = st.selectbox(
            "ir_status",
            ["All", "Approved", "Paid", "Pending", "On-Hold"],
            label_visibility="collapsed",
        )

        # Apply filters to sorted_df
        fdf = sorted_df.copy()
        if search.strip():
            q    = search.strip()
            mask = (
                fdf["invoice_id"].str.contains(q, case=False, na=False)
                | fdf["vendor"].str.contains(q, case=False, na=False)
            )
            fdf = fdf[mask]
        if status_filter != "All":
            fdf = fdf[fdf["status"] == status_filter.lower()]

        # AI suggestion banner — first High priority invoice
        hi_rows = fdf[fdf["priority"] == "High"]
        if not hi_rows.empty:
            hi_inv = hi_rows.iloc[0]["invoice_id"]
            st.markdown(
                f"<div style='background:rgba(79,142,247,0.10); "
                f"border-left:3px solid #4F8EF7; border-radius:6px; "
                f"padding:0.5rem 0.7rem; margin:0.3rem 0 0.5rem; font-size:0.77rem;'>"
                f"<span style='color:#4F8EF7; font-weight:700;'>AI Suggestion</span><br>"
                f"<span style='color:#E8EAF0;'>Process {hi_inv} next — "
                f"High priority, SLA expires in 2 days.</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            f"<p style='color:#8B8FA8; font-size:0.78rem; margin:0.1rem 0 0.3rem;'>"
            f"{len(fdf)} invoices</p>",
            unsafe_allow_html=True,
        )

        # ── Invoice selection via selectbox ──────────────────────────────────
        _inv_ids = fdf["invoice_id"].tolist() if not fdf.empty else []
        _cur_sel = st.session_state.ir_selected_id
        _sel_idx = _inv_ids.index(_cur_sel) if _cur_sel in _inv_ids else 0
        if _inv_ids:
            _chosen = st.selectbox(
                "Select invoice",
                options=_inv_ids,
                index=_sel_idx,
                key="ir_inv_select",
                label_visibility="collapsed",
            )
            if _chosen != st.session_state.ir_selected_id:
                st.session_state.ir_selected_id = _chosen
                st.session_state.ir_chat_open   = False
                st.rerun()

        # ── Build all cards as one HTML string ────────────────────────────────
        _sel_now = st.session_state.ir_selected_id

        _pc_border = {"High": "#FF5C5C", "Medium": "#FFB547", "Low": "#4F8EF7"}
        _pc_bg     = {"High": "#2D1515", "Medium": "#2D2415", "Low": "#151E2D"}
        _pc_badge_bg = {
            "High":   "rgba(255,92,92,0.18)",
            "Medium": "rgba(255,181,71,0.18)",
            "Low":    "rgba(79,142,247,0.18)",
        }
        _sc_col = {
            "approved": "#00C48C",
            "paid":     "#4F8EF7",
            "pending":  "#FFB547",
            "on-hold":  "#FF5C5C",
        }

        _all_cards = []
        for _, crow in fdf.iterrows():
            c_inv_id   = str(crow["invoice_id"])
            c_vendor   = str(crow["vendor"])
            c_status   = str(crow["status"])
            c_priority = str(crow["priority"])
            c_exc      = str(crow.get("exception_type", ""))
            try:
                c_amt = _indian_fmt(float(crow["amount_inr"]))
            except Exception:
                c_amt = "—"

            c_status_label = c_status.replace("-", "\u2011").title()
            c_bdr    = _pc_border.get(c_priority, "#4F8EF7")
            c_bg     = _pc_bg.get(c_priority, "#151E2D")
            c_pbg    = _pc_badge_bg.get(c_priority, "rgba(79,142,247,0.18)")
            c_sdot   = _sc_col.get(c_status, "#8B8FA8")
            is_sel   = (_sel_now == c_inv_id)
            card_bg  = "#1E2130" if is_sel else c_bg
            card_bdr = "#4F8EF7" if is_sel else c_bdr
            sel_ring = f"box-shadow:0 0 0 2px #4F8EF7;" if is_sel else ""

            _pbadge = (
                f"<span style='background:{c_pbg}; color:{c_bdr}; "
                f"border:1px solid {c_bdr}; border-radius:9px; "
                f"padding:1px 6px; font-size:0.68rem; font-weight:600;'>"
                f"{c_priority}</span>"
            )
            _ebadge = ""
            if c_exc:
                _ebadge = (
                    f"&nbsp;<span style='background:rgba(255,92,92,0.14); "
                    f"color:#FF5C5C; border:1px solid #FF5C5C; border-radius:9px; "
                    f"padding:1px 6px; font-size:0.68rem; font-weight:600;'>"
                    f"{c_exc}</span>"
                )
            _sdot_html = (
                f"<span style='display:inline-block; width:6px; height:6px; "
                f"border-radius:50%; background:{c_sdot}; margin-right:4px; "
                f"vertical-align:middle;'></span>"
                f"<span style='color:{c_sdot}; font-size:0.74rem;'>"
                f"{c_status_label}</span>"
            )

            _all_cards.append(
                f"<div style='background:{card_bg}; "
                f"border:1px solid {card_bdr}; "
                f"border-left:3px solid {card_bdr}; "
                f"border-radius:8px; {sel_ring}"
                f"padding:0.6rem 0.8rem; margin-bottom:0.45rem;'>"
                f"<div style='display:flex; justify-content:space-between; "
                f"align-items:flex-start; margin-bottom:0.18rem;'>"
                f"<span style='font-size:0.73rem; font-family:monospace; "
                f"color:#8B8FA8;'>{c_inv_id}</span>"
                f"<span>{_pbadge}{_ebadge}</span>"
                f"</div>"
                f"<div style='color:#E8EAF0; font-size:0.84rem; font-weight:600; "
                f"margin-bottom:0.15rem; white-space:nowrap; overflow:hidden; "
                f"text-overflow:ellipsis;'>{c_vendor}</div>"
                f"<div style='display:flex; justify-content:space-between; "
                f"align-items:center;'>"
                f"<span style='color:#00C48C; font-size:0.81rem; font-weight:700;'>"
                f"&#8377;{c_amt}</span>"
                f"<span>{_sdot_html}</span>"
                f"</div></div>"
            )

        _cards_html = "".join(_all_cards)
        st.markdown(
            f'<div class="invoice-list-container">{_cards_html}</div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════
    # RIGHT — Invoice Detail
    # ══════════════════════════
    with rcol:
        sel_id = st.session_state.ir_selected_id

        if not sel_id or sel_id not in df["invoice_id"].values:
            st.markdown(
                "<div style='background:#1E2130; border-radius:8px; "
                "padding:5rem 2rem; text-align:center; margin-top:1rem;'>"
                "<div style='font-size:2.5rem; margin-bottom:1rem;'>&#128203;</div>"
                "<div style='color:#8B8FA8; font-size:0.95rem;'>"
                "Select an invoice from the list to view details.</div>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            sel_row    = df[df["invoice_id"] == sel_id].iloc[0]
            r_status   = str(sel_row["status"])
            r_vendor   = str(sel_row["vendor"])
            r_gl       = str(sel_row.get("gl_code", "—"))
            r_priority = str(sel_row.get("priority", "Low"))
            r_exc      = str(sel_row.get("exception_type", ""))
            r_currency = str(sel_row.get("currency", "INR"))
            try:
                r_amount  = float(sel_row["amount_inr"])
                r_amt_fmt = _indian_fmt(r_amount)
            except Exception:
                r_amount  = 0.0
                r_amt_fmt = "—"

            r_inv_dt = sel_row.get("invoice_date")
            r_date   = r_inv_dt.strftime("%d %b %Y") if pd.notna(r_inv_dt) else "—"

            _s_col = {
                "approved": ("#00C48C", "rgba(0,196,140,0.12)"),
                "paid":     ("#4F8EF7", "rgba(79,142,247,0.12)"),
                "pending":  ("#FFB547", "rgba(255,181,71,0.12)"),
                "on-hold":  ("#FF5C5C", "rgba(255,92,92,0.12)"),
            }
            r_sfg, r_sbg = _s_col.get(r_status, ("#8B8FA8", "rgba(139,143,168,0.12)"))

            # GL description
            r_gl_desc = "—"
            try:
                for _gr in _csv_rows("gl_master.csv"):
                    if str(_gr["gl_code"]).strip() == r_gl.strip():
                        r_gl_desc = _gr["description"]
                        break
            except Exception:
                pass

            # ── Section 1: Header card + Ask me button (FIX 6) ───────────────
            r_status_label = r_status.replace("-", "\u2011").title()
            _hdr_col, _ask_col = st.columns([8, 2])
            with _hdr_col:
                st.markdown(
                    f"<div style='background:#1E2130; border-radius:8px; "
                    f"padding:1.1rem 1.5rem; border-left:4px solid {r_sfg};'>"
                    f"<div style='display:flex; justify-content:space-between; "
                    f"align-items:flex-start; flex-wrap:wrap; gap:0.5rem;'>"
                    f"<div>"
                    f"<div style='font-size:0.7rem; color:#8B8FA8; "
                    f"text-transform:uppercase; letter-spacing:0.08em;'>Invoice</div>"
                    f"<div style='font-size:1.25rem; font-weight:700; "
                    f"color:#E8EAF0; font-family:monospace; margin-top:2px;'>{sel_id}</div>"
                    f"<div style='color:#8B8FA8; font-size:0.83rem; margin-top:4px;'>"
                    f"{r_vendor}</div>"
                    f"</div>"
                    f"<div style='text-align:right;'>"
                    f"<div style='font-size:1.4rem; font-weight:700; color:#00C48C;'>"
                    f"&#8377;{r_amt_fmt}</div>"
                    f"<div style='margin-top:5px;'>"
                    f"<span style='background:{r_sbg}; color:{r_sfg}; "
                    f"border:1px solid {r_sfg}; border-radius:12px; "
                    f"padding:2px 10px; font-size:0.75rem; font-weight:700;'>"
                    f"{r_status_label}</span></div>"
                    f"</div></div>"
                    f"<div style='display:flex; gap:2rem; margin-top:0.85rem; flex-wrap:wrap;'>"
                    f"<div><div style='color:#8B8FA8; font-size:0.72rem;'>Date</div>"
                    f"<div style='color:#E8EAF0; font-size:0.84rem;'>{r_date}</div></div>"
                    f"<div><div style='color:#8B8FA8; font-size:0.72rem;'>GL Code</div>"
                    f"<div style='color:#E8EAF0; font-size:0.84rem;'>{r_gl}</div></div>"
                    f"<div><div style='color:#8B8FA8; font-size:0.72rem;'>GL Desc</div>"
                    f"<div style='color:#E8EAF0; font-size:0.84rem;'>{r_gl_desc}</div></div>"
                    f"<div><div style='color:#8B8FA8; font-size:0.72rem;'>Currency</div>"
                    f"<div style='color:#E8EAF0; font-size:0.84rem;'>{r_currency}</div></div>"
                    f"<div><div style='color:#8B8FA8; font-size:0.72rem;'>Priority</div>"
                    f"<div style='color:#E8EAF0; font-size:0.84rem;'>{r_priority}</div></div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            with _ask_col:
                st.markdown(
                    "<div style='height:0.7rem;'></div>", unsafe_allow_html=True
                )
                # Ask me button — toggles the floating chat overlay
                if st.button("\U0001f4ac Ask me", key="ir_ask_ai",
                             use_container_width=True):
                    st.session_state.ir_chat_open = (
                        not st.session_state.ir_chat_open
                    )
                    st.rerun()

            # ── FIX 3: Hidden JS→Python bridge input ─────────────────────────
            # (made invisible via CSS targeting .st-key-ir_chat_trigger)
            st.text_input(
                "\u200B",
                key="ir_chat_trigger",
                label_visibility="collapsed",
            )

            # ── FIX 3: Floating draggable chat overlay via components.html() ──
            _chat_is_open = st.session_state.ir_chat_open
            _chat_ctx     = f"{sel_id} \u00b7 {r_vendor}"
            _chat_hist_json = json.dumps(
                st.session_state.ir_chat_history, ensure_ascii=False
            )

            # Build message HTML for injection
            _msg_html_parts = []
            for _hm in st.session_state.ir_chat_history:
                _hcontent = (
                    _hm["content"]
                    .replace("\\", "\\\\")
                    .replace("`", "\\`")
                    .replace("$", "\\$")
                )
                if _hm["role"] == "user":
                    _msg_html_parts.append(
                        f"<div style='display:flex;justify-content:flex-end;"
                        f"margin-bottom:8px;'>"
                        f"<div style='background:#1D3557;color:#E8EAF0;"
                        f"border-radius:12px 12px 2px 12px;padding:8px 12px;"
                        f"max-width:75%;font-size:0.81rem;line-height:1.45;"
                        f"font-family:sans-serif;'>{_hcontent}</div></div>"
                    )
                else:
                    _msg_html_parts.append(
                        f"<div style='display:flex;gap:6px;margin-bottom:8px;"
                        f"align-items:flex-start;'>"
                        f"<div style='width:22px;height:22px;border-radius:50%;"
                        f"background:#4F8EF7;display:flex;align-items:center;"
                        f"justify-content:center;font-size:0.58rem;font-weight:700;"
                        f"color:white;flex-shrink:0;font-family:sans-serif;'>AI</div>"
                        f"<div style='background:#252840;color:#E8EAF0;"
                        f"border-radius:2px 12px 12px 12px;padding:8px 12px;"
                        f"max-width:78%;font-size:0.81rem;line-height:1.45;"
                        f"font-family:sans-serif;'>{_hcontent}</div></div>"
                    )
            _msgs_html = "".join(_msg_html_parts)
            _placeholder_html = (
                "" if _msgs_html else
                "<div style='color:#8B8FA8;font-size:0.81rem;font-family:sans-serif;"
                "padding:8px 0;'>Ask me anything about this invoice\u2026</div>"
            )

            _open_flag  = "true" if _chat_is_open else "false"
            _ctx_safe   = _chat_ctx.replace("'", "\\'")

            components.html(
                f"""<!DOCTYPE html>
<html><head><style>body{{margin:0;padding:0;background:transparent;}}</style></head>
<body>
<script>
(function() {{
  var isOpen = {_open_flag};

  // Always remove previous instance so it refreshes with new history
  var old = window.parent.document.getElementById('ap-float-chat');
  if (old) old.remove();

  if (!isOpen) return;

  // Create box
  var box = window.parent.document.createElement('div');
  box.id = 'ap-float-chat';
  box.style.cssText = [
    'position:fixed','bottom:20px','right:20px','width:360px','height:480px',
    'background:#1E2130','border:1px solid #4F8EF7','border-radius:12px',
    'z-index:9999','display:flex','flex-direction:column',
    'box-shadow:0 8px 32px rgba(0,0,0,0.55)','font-family:sans-serif'
  ].join(';');

  // Restore saved position
  try {{
    var sp = JSON.parse(localStorage.getItem('ap-chat-pos') || 'null');
    if (sp) {{
      box.style.left   = sp.left;
      box.style.top    = sp.top;
      box.style.bottom = 'auto';
      box.style.right  = 'auto';
    }}
  }} catch(e) {{}}

  box.innerHTML = `
    <div id="ap-fc-hdr" style="background:#151E2D;border-radius:12px 12px 0 0;
      padding:10px 14px;display:flex;justify-content:space-between;
      align-items:center;cursor:move;flex-shrink:0;user-select:none;">
      <div>
        <span style="color:#4F8EF7;font-size:0.77rem;font-weight:700;
          text-transform:uppercase;letter-spacing:0.07em;">AP Assistant</span>
        <span style="color:#8B8FA8;font-size:0.71rem;margin-left:8px;">{_ctx_safe}</span>
      </div>
      <button id="ap-fc-close" style="background:none;border:none;color:#8B8FA8;
        font-size:1.05rem;cursor:pointer;padding:0 2px;line-height:1;">&#x2715;</button>
    </div>
    <div id="ap-fc-msgs" style="flex:1;overflow-y:auto;padding:12px;
      background:#13162A;display:flex;flex-direction:column;">
      {_msgs_html}{_placeholder_html}
    </div>
    <div style="padding:10px 12px;background:#1E2130;
      border-top:1px solid #2A2D3E;border-radius:0 0 12px 12px;flex-shrink:0;">
      <div style="display:flex;gap:8px;">
        <input id="ap-fc-inp" type="text"
          placeholder="Ask about this invoice\u2026"
          style="flex:1;background:#252840;border:1px solid #2A2D3E;
          border-radius:8px;padding:8px 11px;color:#E8EAF0;font-size:0.81rem;
          outline:none;font-family:sans-serif;" />
        <button id="ap-fc-send" style="background:#4F8EF7;border:none;
          border-radius:8px;padding:8px 14px;color:white;font-size:0.81rem;
          font-weight:600;cursor:pointer;">Send</button>
      </div>
    </div>
  `;

  window.parent.document.body.appendChild(box);

  // Scroll messages to bottom
  var msgsDiv = window.parent.document.getElementById('ap-fc-msgs');
  if (msgsDiv) msgsDiv.scrollTop = msgsDiv.scrollHeight;

  // Helper: find hidden bridge input (placeholder = zero-width space \\u200B)
  function getBridge() {{
    var inputs = window.parent.document.querySelectorAll('input[type="text"]');
    for (var i = 0; i < inputs.length; i++) {{
      if (inputs[i].placeholder === '\\u200B') return inputs[i];
    }}
    return null;
  }}

  // Helper: set bridge value and fire React input event
  function fireBridge(value) {{
    var inp = getBridge();
    if (!inp) return;
    var setter = Object.getOwnPropertyDescriptor(
      window.HTMLInputElement.prototype, 'value').set;
    setter.call(inp, value);
    inp.dispatchEvent(new Event('input', {{bubbles: true}}));
  }}

  // Close button
  window.parent.document.getElementById('ap-fc-close')
    .addEventListener('click', function() {{
      fireBridge('__CLOSE__');
    }});

  // Send
  function doSend() {{
    var inp = window.parent.document.getElementById('ap-fc-inp');
    var msg = (inp ? inp.value : '').trim();
    if (!msg) return;
    inp.value = '';
    fireBridge(msg);
  }}
  window.parent.document.getElementById('ap-fc-send')
    .addEventListener('click', doSend);
  window.parent.document.getElementById('ap-fc-inp')
    .addEventListener('keydown', function(e) {{
      if (e.key === 'Enter') doSend();
    }});

  // Drag
  var hdr = window.parent.document.getElementById('ap-fc-hdr');
  var dragging = false, sx, sy, bx0, by0;
  hdr.addEventListener('mousedown', function(e) {{
    dragging = true;
    sx = e.clientX; sy = e.clientY;
    var r = box.getBoundingClientRect();
    bx0 = r.left; by0 = r.top;
    e.preventDefault();
  }});
  window.parent.document.addEventListener('mousemove', function(e) {{
    if (!dragging) return;
    box.style.left   = (bx0 + e.clientX - sx) + 'px';
    box.style.top    = (by0 + e.clientY - sy) + 'px';
    box.style.bottom = 'auto';
    box.style.right  = 'auto';
  }});
  window.parent.document.addEventListener('mouseup', function() {{
    if (dragging) {{
      dragging = false;
      try {{
        localStorage.setItem('ap-chat-pos', JSON.stringify({{
          left: box.style.left, top: box.style.top
        }}));
      }} catch(e) {{}}
    }}
  }});
}})();
</script>
</body></html>""",
                height=0,
                scrolling=False,
            )

            # ── Section 2: Line Items (FIX 4 + FIX 5) ────────────────────────
            st.markdown(
                "<div style='color:#4F8EF7; font-size:0.72rem; font-weight:700; "
                "letter-spacing:0.08em; text-transform:uppercase; "
                "margin:0.75rem 0 0.45rem;'>Line Items</div>",
                unsafe_allow_html=True,
            )

            if sel_id not in st.session_state.ir_line_data:
                st.session_state.ir_line_data[sel_id] = _apa_line_items(
                    r_amount, r_gl, r_exc
                )
            lines = st.session_state.ir_line_data[sel_id]

            # FIX 4: compute per-line exception badge
            def _line_exc(idx: int, ld: dict, et: str) -> str:
                _gl  = str(ld.get("GL Code",  "") or "").strip()
                _tc  = str(ld.get("Tax Code", "") or "").strip()
                if et == "PO Missing":
                    return "PO Unlinked"
                if et == "GL Coding Required":
                    return "GL Missing" if not _gl else ""
                if et == "Vendor Mismatch":
                    return "Vendor Mismatch" if idx == 0 else ""
                if et == "Tax Code Missing":
                    return "Tax Missing" if not _tc else ""
                if et == "Line Tagging Failure":
                    return "Tagging Fail" if idx % 2 == 0 else ""
                return ""

            line_excepts = [_line_exc(i, l, r_exc) for i, l in enumerate(lines)]

            line_df = pd.DataFrame(lines)
            _lcols  = ["Description", "Qty", "Unit Price (\u20b9)",
                       "GL Code", "Tax Code"]
            for _lc in _lcols:
                if _lc not in line_df.columns:
                    line_df[_lc] = ""
            # FIX 4: Exception column — red label or PASS
            line_df["Exception"] = [
                e if e else "PASS" for e in line_excepts
            ]

            # FIX 5: Auto-analyze on selection (no button)
            if sel_id not in st.session_state.ir_line_analyses:
                _inv_det = (
                    f"{sel_id} | {r_vendor} | {r_amt_fmt} | "
                    f"{r_status} | GL:{r_gl}"
                )
                _sop_all = " ".join(_APA_SOP.values())
                with st.spinner("AI analysing lines\u2026"):
                    _result = _ir_analyze_lines(
                        _inv_det,
                        json.dumps(st.session_state.ir_line_data[sel_id]),
                        _sop_all,
                    )
                st.session_state.ir_line_analyses[sel_id] = _result

            analyses = st.session_state.ir_line_analyses.get(sel_id, [])
            _ana_by_line = {
                int(item.get("line_sr", 0)): item for item in analyses
            }

            # FIX 5: Table left (6), callouts right (4) — one card per row
            tbl_col, ai_col = st.columns([6, 4])

            with tbl_col:
                edited_df = st.data_editor(
                    line_df[_lcols + ["Exception"]],
                    key=f"ir_de_{sel_id}",
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Description":           st.column_config.TextColumn(
                            "Description", disabled=True),
                        "Qty":                   st.column_config.NumberColumn(
                            "Qty", disabled=True),
                        "Unit Price (\u20b9)":   st.column_config.TextColumn(
                            "Unit Price", disabled=True),
                        "GL Code":               st.column_config.TextColumn(
                            "GL Code"),
                        "Tax Code":              st.column_config.SelectboxColumn(
                            "Tax Code",
                            options=["GST 5%", "GST 12%",
                                     "GST 18%", "Exempt"],
                        ),
                        "Exception":             st.column_config.TextColumn(
                            "Exception", disabled=True),
                    },
                )
                if edited_df is not None:
                    st.session_state.ir_line_data[sel_id] = (
                        edited_df[_lcols].to_dict("records")
                    )
                _ba, _ = st.columns([1, 4])
                with _ba:
                    if st.button("Save Changes", key=f"ir_save_{sel_id}"):
                        st.success("Saved.")

            with ai_col:
                # FIX 5: one callout per line row, vertically aligned
                _sev_c = {
                    "error":          ("#FF5C5C", "rgba(255,92,92,0.10)"),
                    "warning":        ("#FFB547", "rgba(255,181,71,0.10)"),
                    "recommendation": ("#4F8EF7", "rgba(79,142,247,0.10)"),
                }
                # Spacer to align with the data_editor header row
                st.markdown(
                    "<div style='height:2.1rem;'></div>",
                    unsafe_allow_html=True,
                )
                for _i, _l in enumerate(lines):
                    _lsr  = _i + 1
                    _item = _ana_by_line.get(_lsr)
                    if _item:
                        _sev  = str(_item.get("severity",
                                              "recommendation")).lower()
                        _cfg, _cbg = _sev_c.get(
                            _sev, ("#8B8FA8", "rgba(139,143,168,0.10)")
                        )
                        _sugg = _item.get("suggestion", "")
                        _wds  = _sugg.split()
                        if len(_wds) > 20:
                            _sugg = " ".join(_wds[:20]) + "\u2026"
                        _conf = _item.get("confidence", "")
                        st.markdown(
                            f"<div style='background:{_cbg}; "
                            f"border-left:3px solid {_cfg}; border-radius:6px; "
                            f"padding:0.45rem 0.6rem; margin-bottom:0.4rem; "
                            f"min-height:36px;'>"
                            f"<div style='display:flex; "
                            f"justify-content:space-between; "
                            f"align-items:center; margin-bottom:0.1rem;'>"
                            f"<span style='color:{_cfg}; font-size:0.67rem; "
                            f"font-weight:700;'>Line {_lsr}</span>"
                            f"<span style='color:{_cfg}; font-size:0.63rem; "
                            f"border:1px solid {_cfg}; border-radius:8px; "
                            f"padding:0 4px;'>{_conf}</span>"
                            f"</div>"
                            f"<div style='color:#E8EAF0; font-size:0.75rem; "
                            f"line-height:1.35;'>{_sugg}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div style='color:#3A3D52; font-size:0.71rem; "
                            f"padding:0.45rem 0.6rem; min-height:36px; "
                            f"margin-bottom:0.4rem;'>"
                            f"Line {_lsr}: no issues</div>",
                            unsafe_allow_html=True,
                        )

            # ── Section 3: Exception Summary ──────────────────────────────────
            st.markdown(
                "<div style='margin-top:0.75rem;'></div>",
                unsafe_allow_html=True,
            )
            if r_status in ("on-hold", "pending"):
                _sop_k  = _APA_EXC_SOP.get(r_exc, "")
                _sop_t  = _APA_SOP.get(_sop_k, "")
                _issues = _APA_EXC_ISSUES.get(r_exc, [])
                _elabel = r_exc if r_exc else "Exception"
                _iss_html = "".join(
                    f"<div style='display:flex; gap:0.5rem; margin-bottom:0.3rem;'>"
                    f"<span style='color:#FF5C5C;'>&#10007;</span>"
                    f"<span style='color:#E8EAF0; font-size:0.83rem;'>{_iss}</span>"
                    f"</div>"
                    for _iss in _issues
                )
                _sop_html = ""
                if _sop_t:
                    _sop_html = (
                        "<div style='background:rgba(79,142,247,0.07); "
                        "border-radius:6px; padding:0.65rem 0.8rem; "
                        "margin-top:0.7rem;'>"
                        "<div style='color:#4F8EF7; font-size:0.7rem; "
                        "font-weight:700; letter-spacing:0.07em; "
                        "text-transform:uppercase; margin-bottom:0.3rem;'>"
                        "SOP Guidance</div>"
                        f"<div style='color:#8B8FA8; font-size:0.79rem; "
                        f"line-height:1.5;'>{_sop_t}</div></div>"
                    )
                _exc_hdr = "Exception Summary"
                if _elabel != "Exception":
                    _exc_hdr = "Exception Summary \u2014 " + _elabel
                st.markdown(
                    f"<div style='background:rgba(255,92,92,0.07); "
                    f"border-left:4px solid #FF5C5C; border-radius:8px; "
                    f"padding:1rem 1.25rem;'>"
                    f"<div style='color:#FF5C5C; font-size:0.72rem; "
                    f"font-weight:700; letter-spacing:0.08em; "
                    f"text-transform:uppercase; margin-bottom:0.6rem;'>"
                    f"{_exc_hdr}</div>"
                    f"{_iss_html}{_sop_html}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div style='background:rgba(0,196,140,0.07); "
                    "border-left:4px solid #00C48C; border-radius:8px; "
                    "padding:0.85rem 1.25rem;'>"
                    "<div style='color:#00C48C; font-size:0.85rem;'>"
                    "&#10003;&nbsp; No exceptions detected for this invoice."
                    "</div></div>",
                    unsafe_allow_html=True,
                )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — AP PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def page_ap_pipeline():
    st.title("AP Pipeline")

    # ── Master Data Health ────────────────────────────────────────────────────
    def _count_csv(filename: str, filter_col: str = None,
                   filter_val: str = None) -> int:
        path = os.path.join(_BASE, filename)
        if not os.path.exists(path):
            return 0
        try:
            rows = _csv_rows(filename)
            if filter_col and filter_val:
                rows = [r for r in rows
                        if r.get(filter_col, "").strip().lower() == filter_val]
            return len(rows)
        except Exception:
            return 0

    n_vendors = _count_csv("vendor_master.csv")
    n_open_po = _count_csv("po_master.csv", "status", "open")
    n_grn     = _count_csv("grn_master.csv")
    n_gl      = _count_csv("gl_master.csv")

    st.markdown(
        "<p style='color:#8B8FA8; font-size:0.77rem; font-weight:700; "
        "text-transform:uppercase; letter-spacing:0.07em; "
        "margin-bottom:0.7rem;'>Master Data Health</p>",
        unsafe_allow_html=True,
    )
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.markdown(_metric_card("Approved Vendors",     str(n_vendors), "#00C48C"),
                 unsafe_allow_html=True)
    mc2.markdown(_metric_card("Open Purchase Orders", str(n_open_po), "#4F8EF7"),
                 unsafe_allow_html=True)
    mc3.markdown(_metric_card("GRNs Recorded",        str(n_grn),     "#FFB547"),
                 unsafe_allow_html=True)
    mc4.markdown(_metric_card("GL Codes",             str(n_gl),      "#8B8FA8"),
                 unsafe_allow_html=True)

    st.markdown(
        "<hr style='border-color:#2A2D3E; margin:1.4rem 0;'>",
        unsafe_allow_html=True,
    )

    # ── Session state init ────────────────────────────────────────────────────
    for _k in ("pp_extracted", "pp_last_pdf", "pp_s2_log", "pp_s2_text",
               "pp_s3_log", "pp_s3_text", "pp_s4"):
        if _k not in st.session_state:
            st.session_state[_k] = None

    # ── PDF upload zone ───────────────────────────────────────────────────────
    st.markdown(
        "<p style='color:#8B8FA8; margin-bottom:0.4rem; font-size:0.85rem;'>"
        "Drop invoice PDF here or click to browse</p>",
        unsafe_allow_html=True,
    )
    pdf_file = st.file_uploader(
        "Invoice PDF",
        type=["pdf"],
        key="pp_pdf_uploader",
        label_visibility="collapsed",
    )

    if pdf_file is not None:
        if st.session_state.pp_last_pdf != pdf_file.name:
            for _k in ("pp_extracted", "pp_s2_log", "pp_s2_text",
                       "pp_s3_log", "pp_s3_text", "pp_s4"):
                st.session_state[_k] = None
            st.session_state.pp_last_pdf = pdf_file.name

    if pdf_file is not None and st.session_state.pp_extracted is None:
        if not ANTHROPIC_API_KEY:
            st.error("ANTHROPIC_API_KEY not found in .env — cannot extract fields.")
        else:
            with st.spinner("Extracting invoice fields with Claude…"):
                try:
                    pdf_text = _pdf_to_text(pdf_file.read())
                    if not pdf_text.strip():
                        st.error(
                            "No text found in this PDF. "
                            "The file must contain selectable text."
                        )
                    else:
                        st.session_state.pp_extracted = _extract_invoice_fields(pdf_text)
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

    inv = st.session_state.pp_extracted

    if pdf_file is not None and inv is not None:
        st.markdown(
            f"<div style='background:rgba(0,196,140,0.09); border-left:4px solid #00C48C; "
            f"border-radius:6px; padding:0.7rem 1.1rem; margin:0.75rem 0; color:#00C48C; "
            f"font-size:0.9rem;'>"
            f"&#10003;&nbsp; <strong>Extracted:</strong>&nbsp;"
            f"{inv.get('invoice_number', '—')} from <em>{pdf_file.name}</em>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if pdf_file is None or inv is None:
        return

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)

    # ── Pipeline stepper ──────────────────────────────────────────────────────
    _stages = [
        ("CAPTURE",    inv                             is not None),
        ("AP ADVANCE", st.session_state.pp_s2_log     is not None),
        ("TRACE",      st.session_state.pp_s3_log     is not None),
        ("ASSIST",     st.session_state.pp_s4         is not None),
    ]
    step_html = ""
    for i, (label, done) in enumerate(_stages):
        if done:
            circ_col = "#00C48C"
            circ_bg  = "rgba(0,196,140,0.15)"
            content  = "&#10003;"
            lbl_col  = "#00C48C"
        else:
            circ_col = "#2A2D3E"
            circ_bg  = "transparent"
            content  = str(i + 1)
            lbl_col  = "#8B8FA8"
        step_html += (
            f"<div style='display:flex; flex-direction:column; "
            f"align-items:center; gap:6px;'>"
            f"<div style='width:36px; height:36px; border-radius:50%; "
            f"border:2px solid {circ_col}; background:{circ_bg}; "
            f"display:flex; align-items:center; justify-content:center; "
            f"color:{circ_col}; font-weight:700; font-size:0.88rem;'>{content}</div>"
            f"<span style='font-size:0.71rem; color:{lbl_col}; font-weight:600; "
            f"letter-spacing:0.05em; white-space:nowrap;'>{label}</span>"
            f"</div>"
        )
        if i < len(_stages) - 1:
            line_col = "#00C48C" if done else "#2A2D3E"
            step_html += (
                f"<div style='flex:1; height:2px; background:{line_col}; "
                f"margin:17px 8px 0;'></div>"
            )
    st.markdown(
        f"<div style='background:#1E2130; border-radius:8px; "
        f"padding:1.1rem 1.5rem; border:1px solid #2A2D3E; margin-bottom:1.25rem;'>"
        f"<div style='display:flex; align-items:flex-start;'>{step_html}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Run Pipeline button ───────────────────────────────────────────────────
    run_clicked = st.button(
        "▶  Run Full AP Pipeline",
        type="primary",
        disabled=not ANTHROPIC_API_KEY,
        key="pp_run_btn",
    )

    if run_clicked:
        for _k in ("pp_s2_log", "pp_s2_text", "pp_s3_log", "pp_s3_text", "pp_s4"):
            st.session_state[_k] = None

        with st.status("AP Advance — running 3-way match…",
                       expanded=True) as _s2_st:
            s2_text, s2_log = _ap_stage2(inv, _s2_st)
            st.session_state.pp_s2_text = s2_text
            st.session_state.pp_s2_log  = s2_log
            _s2_st.update(label="AP Advance ✓", state="complete", expanded=False)

        with st.status("Trace — running fraud checks…",
                       expanded=True) as _s3_st:
            s3_text, s3_log = _ap_stage3(inv, _s3_st)
            st.session_state.pp_s3_text = s3_text
            st.session_state.pp_s3_log  = s3_log
            _s3_st.update(label="Trace ✓", state="complete", expanded=False)

        with st.spinner("Assist — generating final decision…"):
            st.session_state.pp_s4 = _ap_stage4(
                inv,
                st.session_state.pp_s2_text,
                st.session_state.pp_s3_text,
            )
        st.rerun()

    # ── Shared style constants for stage cards ────────────────────────────────
    _chk_icons = {
        "pass": "&#10003;", "warn": "&#9888;",
        "fail": "&#10007;", "pending": "&#9675;",
    }
    _chk_clrs = {
        "pass":    ("#00C48C", "rgba(0,196,140,0.12)"),
        "warn":    ("#FFB547", "rgba(255,181,71,0.12)"),
        "fail":    ("#FF5C5C", "rgba(255,92,92,0.12)"),
        "pending": ("#8B8FA8", "rgba(139,143,168,0.10)"),
    }
    _chk_lbls = {"pass": "PASS", "warn": "WARN", "fail": "FAIL", "pending": "—"}
    _tbl_th = (
        "padding:0.45rem 0.9rem; text-align:left; color:#8B8FA8; "
        "font-size:0.75rem; font-weight:600; text-transform:uppercase; "
        "letter-spacing:0.05em; border-bottom:1px solid #2A2D3E;"
    )

    def _card_wrap(title: str, badge_text: str, badge_color: str,
                   inner_html: str) -> str:
        badge = ""
        if badge_text:
            badge = (
                f"<span style='background:rgba(0,0,0,0.25); color:{badge_color}; "
                f"border:1px solid {badge_color}; border-radius:12px; "
                f"padding:2px 10px; font-size:0.72rem; font-weight:700;'>"
                f"{badge_text}</span>"
            )
        header = (
            f"<div style='display:flex; justify-content:space-between; "
            f"align-items:center; margin-bottom:0.85rem;'>"
            f"<div style='color:#4F8EF7; font-size:0.72rem; font-weight:700; "
            f"letter-spacing:0.08em; text-transform:uppercase;'>{title}</div>"
            f"{badge}</div>"
        )
        return (
            f"<div style='background:#1E2130; border-radius:8px; "
            f"padding:1.2rem 1.5rem; border:1px solid #2A2D3E; "
            f"overflow:hidden; margin-top:0.85rem;'>"
            f"{header}{inner_html}</div>"
        )

    def _checks_table(checks: list) -> str:
        rows = ""
        for i, (chk, lvl, det) in enumerate(checks):
            bg = "#181B28" if i % 2 == 0 else "#1E2130"
            fg, bdg_bg = _chk_clrs.get(lvl, _chk_clrs["pending"])
            rows += (
                f"<tr style='background:{bg};'>"
                f"<td style='padding:0.45rem 0.9rem; color:#E8EAF0; "
                f"font-size:0.84rem; white-space:nowrap;'>"
                f"<span style='color:{fg}; margin-right:6px;'>{_chk_icons[lvl]}</span>"
                f"{chk}</td>"
                f"<td style='padding:0.45rem 0.9rem; text-align:center; width:90px;'>"
                f"<span style='background:{bdg_bg}; color:{fg}; border:1px solid {fg}; "
                f"border-radius:12px; padding:2px 9px; font-size:0.71rem; "
                f"font-weight:700;'>{_chk_lbls.get(lvl, lvl.upper())}</span></td>"
                f"<td style='padding:0.45rem 0.9rem; color:#8B8FA8; "
                f"font-size:0.81rem;'>{det}</td>"
                f"</tr>"
            )
        return (
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<thead><tr style='background:#161929;'>"
            f"<th style='{_tbl_th}'>Check</th>"
            f"<th style='{_tbl_th} text-align:center;'>Result</th>"
            f"<th style='{_tbl_th}'>Detail</th></tr></thead>"
            f"<tbody>{rows}</tbody></table>"
        )

    # ── Stage 1 — CAPTURE ─────────────────────────────────────────────────────
    def _fmt_a(val):
        try:    return _indian_fmt(float(val))
        except: return str(val) if val not in (None, "") else "—"

    cap_left = [
        ("Invoice Number", inv.get("invoice_number") or "—"),
        ("Vendor Name",    inv.get("vendor_name")    or "—"),
        ("Vendor GST",     inv.get("vendor_gst")     or "—"),
        ("Invoice Date",   inv.get("invoice_date")   or "—"),
        ("Due Date",       inv.get("due_date")        or "—"),
        ("PO Reference",   inv.get("po_reference")   or "—"),
    ]
    cap_right = [
        ("Payment Terms",  inv.get("payment_terms")         or "—"),
        ("HSN/SAC Code",   inv.get("hsn_sac_code")          or "—"),
        ("GST Type",       inv.get("gst_type")               or "—"),
        ("GST Rate",       f"{inv.get('gst_rate_percent') or '—'}%"),
        ("GST Amount",     _fmt_a(inv.get("gst_amount_inr"))),
        ("Grand Total",    _fmt_a(inv.get("grand_total_inr"))),
    ]

    def _kv_tbl(pairs: list, highlight_last: bool = False) -> str:
        rows = ""
        for i, (k, v) in enumerate(pairs):
            is_last = highlight_last and i == len(pairs) - 1
            vc = "#00C48C" if is_last else "#E8EAF0"
            fw = "700"     if is_last else "400"
            rows += (
                f"<tr>"
                f"<td style='padding:0.28rem 0; color:#8B8FA8; "
                f"font-size:0.83rem; width:48%;'>{k}</td>"
                f"<td style='padding:0.28rem 0; color:{vc}; font-size:0.83rem; "
                f"font-weight:{fw}; text-align:right;'>{v}</td>"
                f"</tr>"
            )
        return (
            f"<table style='width:100%; border-collapse:collapse;'>"
            f"<tbody>{rows}</tbody></table>"
        )

    cap_inner = (
        "<div style='display:grid; grid-template-columns:1fr 1fr; gap:1.2rem;'>"
        + _kv_tbl(cap_left)
        + _kv_tbl(cap_right, highlight_last=True)
        + "</div>"
    )
    st.markdown(
        _card_wrap("Stage 1 — Capture", "&#10003; Complete", "#00C48C", cap_inner),
        unsafe_allow_html=True,
    )

    # ── Stage 2 — AP ADVANCE ──────────────────────────────────────────────────
    if st.session_state.pp_s2_log is not None:
        s2_checks = _parse_s2_checks(st.session_state.pp_s2_log)
        pass_count = sum(1 for _, l, _ in s2_checks if l == "pass")
        total      = len(s2_checks)
        if pass_count == total and total > 0:
            match_txt, match_col = "Full Match",    "#00C48C"
        elif pass_count >= (total + 1) // 2:
            match_txt, match_col = "Partial Match", "#FFB547"
        else:
            match_txt, match_col = "No Match",      "#FF5C5C"
        st.markdown(
            _card_wrap("Stage 2 — AP Advance", match_txt, match_col,
                       _checks_table(s2_checks)),
            unsafe_allow_html=True,
        )

    # ── Stage 3 — TRACE ───────────────────────────────────────────────────────
    if st.session_state.pp_s3_log is not None:
        s3_checks   = _parse_s3_checks(st.session_state.pp_s3_log)
        s3_all_pass = all(l == "pass" for _, l, _ in s3_checks)
        s3_txt      = "Clear"   if s3_all_pass else "Flagged"
        s3_col      = "#00C48C" if s3_all_pass else "#FF5C5C"
        st.markdown(
            _card_wrap("Stage 3 — Trace", s3_txt, s3_col,
                       _checks_table(s3_checks)),
            unsafe_allow_html=True,
        )

    # ── Stage 4 — ASSIST ──────────────────────────────────────────────────────
    if st.session_state.pp_s4 is not None:
        s4 = st.session_state.pp_s4
        d  = s4["decision"].lower()
        if "auto-approve" in d or "auto approve" in d:
            bg_d, fg_d, bdr_d, ico_d = "#0d2e1a", "#00C48C", "#00C48C", "&#10003;"
        elif "escalate" in d:
            bg_d, fg_d, bdr_d, ico_d = "#2b2410", "#FFB547", "#FFB547", "&#9888;"
        elif "route" in d:
            bg_d, fg_d, bdr_d, ico_d = "#0d1e38", "#4F8EF7", "#4F8EF7", "&#8594;"
        else:
            bg_d, fg_d, bdr_d, ico_d = "#2b1010", "#FF5C5C", "#FF5C5C", "&#10007;"

        note, nxt = "", ""
        in_note = in_next = False
        for ln in s4["full_text"].splitlines():
            s = ln.strip()
            if s.startswith("HELPDESK NOTE"):
                in_note = True; in_next = False; continue
            if s.startswith("NEXT ACTION"):
                in_next = True; in_note = False
                nxt = s.replace("NEXT ACTION:", "").replace("NEXT ACTION :", "").strip()
                continue
            if s.startswith("SLA:") or s.startswith("DECISION:") or s.startswith("EXCEPTION"):
                in_note = False; in_next = False; continue
            if in_note and s:                  note += s + " "
            elif in_next and s and not nxt:    nxt = s

        decision_banner = (
            f"<div style='background:{bg_d}; border-left:6px solid {bdr_d}; "
            f"border-radius:8px; padding:1.25rem 1.5rem;'>"
            f"<div style='font-size:1.25rem; font-weight:700; color:{fg_d}; "
            f"margin-bottom:0.75rem;'>{ico_d}&nbsp; {s4['decision']}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; line-height:1.65;'>"
            f"<strong>Helpdesk Note:</strong> {note.strip() or '—'}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; margin-top:0.4rem;'>"
            f"<strong>Next Action:</strong> {nxt or '—'}</div>"
            f"<div style='color:{fg_d}; font-size:0.9rem; margin-top:0.35rem;'>"
            f"<strong>SLA:</strong> {s4['sla']}</div>"
            f"</div>"
        )
        st.markdown(
            _card_wrap("Stage 4 — Assist", "", "", decision_banner),
            unsafe_allow_html=True,
        )
        with st.expander("Full AI reasoning"):
            st.markdown(s4["full_text"])

        # ── Download Decision Package ─────────────────────────────────────────
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

        def _build_excel() -> bytes:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                # Sheet 1 — Extracted Invoice Fields
                pd.DataFrame({
                    "Field": [
                        "Invoice Number", "Vendor Name", "Vendor GST",
                        "Invoice Date",   "Due Date",    "PO Reference",
                        "Payment Terms",  "HSN/SAC Code","GST Type",
                        "GST Rate (%)",   "GST Amount (INR)", "Grand Total (INR)",
                    ],
                    "Value": [
                        inv.get("invoice_number")    or "—",
                        inv.get("vendor_name")        or "—",
                        inv.get("vendor_gst")         or "—",
                        inv.get("invoice_date")       or "—",
                        inv.get("due_date")            or "—",
                        inv.get("po_reference")       or "—",
                        inv.get("payment_terms")      or "—",
                        inv.get("hsn_sac_code")       or "—",
                        inv.get("gst_type")            or "—",
                        str(inv.get("gst_rate_percent") or "—"),
                        str(inv.get("gst_amount_inr")   or "—"),
                        str(inv.get("grand_total_inr")  or "—"),
                    ],
                }).to_excel(writer, sheet_name="Invoice Fields", index=False)

                # Sheet 2 — AP Advance checks
                s2r = _parse_s2_checks(st.session_state.pp_s2_log or [])
                pd.DataFrame(s2r, columns=["Check", "Result", "Detail"]).to_excel(
                    writer, sheet_name="AP Advance", index=False)

                # Sheet 3 — Trace checks
                s3r = _parse_s3_checks(st.session_state.pp_s3_log or [])
                pd.DataFrame(s3r, columns=["Check", "Result", "Detail"]).to_excel(
                    writer, sheet_name="Trace", index=False)

                # Sheet 4 — Final Decision
                pd.DataFrame({
                    "Field": ["Decision", "SLA", "Helpdesk Note", "Next Action"],
                    "Value": [s4["decision"], s4["sla"],
                              note.strip() or "—", nxt or "—"],
                }).to_excel(writer, sheet_name="Decision", index=False)

            return buf.getvalue()

        inv_num = (inv.get("invoice_number") or "invoice").replace("/", "_")
        st.download_button(
            label="⬇  Download Decision Package",
            data=_build_excel(),
            file_name=f"decision_{inv_num}.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            type="primary",
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE — MASTER DATA
# ══════════════════════════════════════════════════════════════════════════════
def page_master_data():
    st.title("Master Data")

    # ── Local helpers ─────────────────────────────────────────────────────────
    def _sec_hdr(title: str) -> None:
        st.markdown(
            f"<div style='border-left:3px solid #4F8EF7; padding-left:0.8rem; "
            f"margin:1.75rem 0 0.5rem;'>"
            f"<span style='color:#E8EAF0; font-size:1rem; font-weight:700;'>"
            f"{title}</span></div>",
            unsafe_allow_html=True,
        )

    def _stats_row(items: list) -> str:
        sep = "<span style='color:#2A2D3E; margin:0 0.6rem;'>|</span>"
        parts = []
        for label, count, color in items:
            parts.append(
                f"<span style='color:#8B8FA8; font-size:0.83rem;'>{label}: </span>"
                f"<strong style='color:{color}; font-size:0.83rem;'>{count}</strong>"
            )
        return f"<p style='margin:0 0 0.55rem;'>{sep.join(parts)}</p>"

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
        """col_defs: list of (label, right_align: bool)"""
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

    # ── 1 · Vendors ───────────────────────────────────────────────────────────
    _sec_hdr("Vendors")
    _vc = {
        "active":       ("#00C48C", "rgba(0,196,140,0.12)"),
        "inactive":     ("#8B8FA8", "rgba(139,143,168,0.12)"),
        "under_review": ("#FFB547", "rgba(255,181,71,0.12)"),
        "blacklisted":  ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    try:
        vr       = _csv_rows("vendor_master.csv")
        v_tot    = len(vr)
        v_active = sum(1 for r in vr if r.get("status","").lower() == "active")
        v_inact  = sum(1 for r in vr if r.get("status","").lower() == "inactive")
        v_black  = sum(1 for r in vr if r.get("status","").lower() == "blacklisted")
    except Exception:
        vr = []; v_tot = v_active = v_inact = v_black = 0

    st.markdown(
        _stats_row([
            ("Total",       v_tot,    "#E8EAF0"),
            ("Active",      v_active, "#00C48C"),
            ("Inactive",    v_inact,  "#8B8FA8"),
            ("Blacklisted", v_black,  "#FF5C5C"),
        ]),
        unsafe_allow_html=True,
    )
    rows_h = ""
    for i, r in enumerate(vr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        try:    lim = _indian_fmt(float(r.get("approval_limit_inr", 0)))
        except: lim = "—"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; "
            f"white-space:nowrap;'>{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-size:0.84rem;'>{r.get('category','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-weight:600; "
            f"text-align:right; white-space:nowrap;'>{lim}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>"
            f"{_md_pill(r.get('status',''), _vc)}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.84rem;'>"
            f"{r.get('suggested_gl_code','—')}</td>"
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

    # ── 2 · Purchase Orders ───────────────────────────────────────────────────
    _sec_hdr("Purchase Orders")
    _pc = {
        "open":      ("#4F8EF7", "rgba(79,142,247,0.12)"),
        "closed":    ("#00C48C", "rgba(0,196,140,0.12)"),
        "cancelled": ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    try:
        pr      = _csv_rows("po_master.csv")
        p_tot   = len(pr)
        p_open  = sum(1 for r in pr if r.get("status","").lower() == "open")
        p_clo   = sum(1 for r in pr if r.get("status","").lower() == "closed")
        p_can   = sum(1 for r in pr if r.get("status","").lower() == "cancelled")
    except Exception:
        pr = []; p_tot = p_open = p_clo = p_can = 0

    st.markdown(
        _stats_row([
            ("Total",     p_tot,  "#E8EAF0"),
            ("Open",      p_open, "#4F8EF7"),
            ("Closed",    p_clo,  "#00C48C"),
            ("Cancelled", p_can,  "#FF5C5C"),
        ]),
        unsafe_allow_html=True,
    )
    rows_h = ""
    for i, r in enumerate(pr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        try:    amt = _indian_fmt(float(r.get("po_amount_inr", 0)))
        except: amt = "—"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.85rem;'>{r.get('po_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; "
            f"white-space:nowrap;'>{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; font-weight:600; "
            f"text-align:right; white-space:nowrap;'>{amt}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>"
            f"{_md_pill(r.get('status',''), _pc)}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.84rem;'>{r.get('gl_code','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("PO Number", False), ("Vendor", False),
             ("PO Amount (₹)", True), ("Status", False), ("GL Code", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )

    # ── 3 · GRNs ──────────────────────────────────────────────────────────────
    _sec_hdr("Goods Receipt Notes (GRNs)")
    _gc = {
        "received":     ("#00C48C", "rgba(0,196,140,0.12)"),
        "partial":      ("#FFB547", "rgba(255,181,71,0.12)"),
        "not_received": ("#FF5C5C", "rgba(255,92,92,0.12)"),
    }
    try:
        gr      = _csv_rows("grn_master.csv")
        g_tot   = len(gr)
        g_recv  = sum(1 for r in gr if r.get("grn_status","").lower() == "received")
        g_part  = sum(1 for r in gr if r.get("grn_status","").lower() == "partial")
        g_none  = sum(1 for r in gr if r.get("grn_status","").lower() == "not_received")
    except Exception:
        gr = []; g_tot = g_recv = g_part = g_none = 0

    st.markdown(
        _stats_row([
            ("Total",        g_tot,  "#E8EAF0"),
            ("Received",     g_recv, "#00C48C"),
            ("Partial",      g_part, "#FFB547"),
            ("Not Received", g_none, "#FF5C5C"),
        ]),
        unsafe_allow_html=True,
    )
    rows_h = ""
    for i, r in enumerate(gr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.85rem;'>{r.get('grn_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-size:0.85rem;'>{r.get('po_number','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#E8EAF0; "
            f"white-space:nowrap;'>{r.get('vendor_name','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-size:0.84rem; white-space:nowrap;'>{r.get('received_date','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem;'>"
            f"{_md_pill(r.get('grn_status',''), _gc)}</td>"
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

    # ── 4 · GL Codes ──────────────────────────────────────────────────────────
    _sec_hdr("GL Codes")
    try:
        glr     = _csv_rows("gl_master.csv")
        gl_tot  = len(glr)
        gl_cats = len({r.get("category","") for r in glr if r.get("category","")})
    except Exception:
        glr = []; gl_tot = gl_cats = 0

    st.markdown(
        _stats_row([
            ("Total",      gl_tot,  "#E8EAF0"),
            ("Categories", gl_cats, "#4F8EF7"),
        ]),
        unsafe_allow_html=True,
    )
    rows_h = ""
    for i, r in enumerate(glr):
        bg = "#1E2130" if i % 2 == 0 else "#181B28"
        rows_h += (
            f"<tr style='background:{bg};'>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-family:monospace; font-weight:600; "
            f"font-size:0.85rem;'>{r.get('gl_code','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; "
            f"color:#E8EAF0;'>{r.get('description','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-size:0.84rem;'>{r.get('category','—')}</td>"
            f"<td style='padding:0.48rem 0.9rem; color:#8B8FA8; "
            f"font-size:0.83rem;'>{r.get('valid_for_categories','—')}</td>"
            f"</tr>"
        )
    st.markdown(
        _md_tbl(
            [("GL Code", False), ("Description", False),
             ("Category", False), ("Valid For", False)],
            rows_h,
        ),
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# AGENT HELPERS  (module-level so they aren't redefined on every render)
# ══════════════════════════════════════════════════════════════════════════════
_AGENT_SYSTEM = (
    "You are an AP invoice processing agent. For the invoice provided, run "
    "the following checks IN ORDER:\n"
    "1. lookup_vendor — verify the vendor exists and is active\n"
    "2. check_approval_limit — verify the amount is within the vendor's limit\n"
    "3. check_duplicate — check for duplicate invoices (use the provided date)\n"
    "4. check_anomaly — flag if amount is anomalous vs. vendor history\n\n"
    "After ALL four checks, respond with EXACTLY this format and nothing else:\n"
    "DECISION: <Auto-approve | Route for approval | "
    "Return to vendor | Escalate to manager>\n"
    "REASON: <2-3 sentences explaining the decision based on the check results>\n"
    "SLA: <Same day | 2 business days | 5 business days>"
)

# Only the four core checks — no PO/GRN tools since the form has no PO field
_AGENT_TOOLS = (
    [t for t in _TOOLS_S2 if t["name"] in ("lookup_vendor", "check_approval_limit")]
    + _TOOLS_S3
)


def _run_agent_full(invoice_id: str, vendor: str, amount: float,
                    description: str, container) -> tuple:
    """Run AP agent for manual form input. Writes live progress to container.
    Returns (log, final_text)."""
    today    = datetime.now().strftime("%Y-%m-%d")
    user_msg = (
        f"Process this invoice:\n"
        f"Invoice ID: {invoice_id}\n"
        f"Vendor: {vendor}\n"
        f"Amount: {amount} INR\n"
        f"Date: {today}\n"
        f"Description: {description}"
    )
    client   = anthropic.Anthropic()
    messages = [{"role": "user", "content": user_msg}]
    log      = []

    while True:
        resp = client.messages.create(
            model="claude-opus-4-6", max_tokens=2048,
            system=_AGENT_SYSTEM, tools=_AGENT_TOOLS, messages=messages,
        )
        if resp.stop_reason == "end_turn":
            final = next((b.text for b in resp.content if b.type == "text"), "")
            return log, final
        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            results = []
            for blk in resp.content:
                if blk.type != "tool_use":
                    continue
                fn     = _AP_TOOL_MAP.get(blk.name)
                result = fn(**blk.input) if fn else {"error": f"Unknown: {blk.name}"}
                log.append((blk.name, blk.input, result))
                args_s = ", ".join(f"{k}={v!r}" for k, v in blk.input.items())
                container.write(f"⚙️ **{blk.name}**({args_s})")
                container.write(f"&nbsp;&nbsp;&nbsp;↳ {result}")
                results.append({
                    "type":        "tool_result",
                    "tool_use_id": blk.id,
                    "content":     json.dumps(result),
                })
            messages.append({"role": "user", "content": results})
        else:
            break
    return log, ""


def _agent_result_good(tool_name: str, result: dict) -> bool:
    if tool_name == "lookup_vendor":
        return result.get("found") and result.get("status","").lower() == "active"
    if tool_name == "match_po":
        return result.get("match_status") in ("full", "partial")
    if tool_name == "match_grn":
        return result.get("grn_status") in ("received", "partial")
    if tool_name == "validate_gl_code":
        return result.get("status") == "valid"
    if tool_name == "check_approval_limit":
        return result.get("status") == "within_limit"
    if tool_name == "check_duplicate":
        return result.get("result") == "no_duplicate"
    if tool_name == "check_anomaly":
        return result.get("result") in ("normal", "insufficient_data")
    return False


def _agent_result_summary(tool_name: str, result: dict) -> str:
    if tool_name == "lookup_vendor":
        if result.get("found"):
            return (f"{result.get('vendor_name','?')} — "
                    f"{result.get('category','?')} | "
                    f"status: {result.get('status','?')}")
        return result.get("error", "Not found")
    if tool_name == "match_po":
        ms = result.get("match_status","none")
        if ms in ("full","partial"):
            return f"{ms.title()} match — {result.get('variance_pct','?')}% variance"
        return result.get("reason","No match")
    if tool_name == "match_grn":
        gs = result.get("grn_status","not_received")
        if gs != "not_received":
            return f"{result.get('grn_number','?')} — {gs}"
        return result.get("reason","Not received")
    if tool_name == "validate_gl_code":
        return result.get("reason", str(result.get("status","?")))
    if tool_name == "check_approval_limit":
        s = result.get("status","")
        if s == "within_limit":
            return f"Within limit — {_indian_fmt(result.get('headroom_inr',0))} headroom"
        if s == "exceeds_limit":
            return f"Exceeds by {_indian_fmt(result.get('excess_inr',0))}"
        return result.get("reason", s)
    if tool_name == "check_duplicate":
        if result.get("result") == "no_duplicate":
            return f"No duplicate for {_indian_fmt(result.get('amount_checked',0))}"
        return result.get("reason","Duplicate detected")
    if tool_name == "check_anomaly":
        r = result.get("result","")
        if r == "normal":
            return f"Normal — {result.get('ratio','?')}× vendor average"
        if r == "anomaly":
            return f"ANOMALY — {result.get('ratio','?')}× vendor average"
        return result.get("reason", r)
    return str(result)


# ══════════════════════════════════════════════════════════════════════════════
# AP ASSISTANT — SOP knowledge base + module-level helpers
# ══════════════════════════════════════════════════════════════════════════════
_APA_SOP = {
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
        "GL code assignment rules: IT Services and Software = 620100. "
        "Logistics and Freight = 630200. Utilities = 640100. "
        "Office Supplies = 650200. Consulting = 660100. "
        "Rent and Facilities = 670100. "
        "When in doubt, refer to vendor category in vendor master."
    ),
    "tax_code": (
        "Tax code selection: GST 18% for IT services, consulting, software. "
        "GST 12% for logistics and transport. "
        "GST 5% for utilities and essential services. "
        "GST Exempt for inter-state government transactions. "
        "Always verify HSN/SAC code against tax code selected."
    ),
    "line_tagging": (
        "Line tagging failures: "
        "1) Ensure each line item has a valid GL code. "
        "2) Check that cost centre is assigned. "
        "3) Verify line item description matches PO line description within 80% similarity. "
        "4) For blanket POs, tag against the correct PO line manually. "
        "5) Escalate to finance team if more than 3 lines fail tagging."
    ),
    "erp_mismatch": (
        "When PO exists in ERP but invoice still fails: "
        "1) Check PO status — must be Open not Closed or Partially Closed. "
        "2) Verify PO amount has sufficient remaining balance. "
        "3) Check if GRN has been recorded. "
        "4) If all checks pass and still failing, this is likely a system issue — "
        "raise IT support ticket with PO number, invoice number, and error screenshot."
    ),
}

_APA_EXC_TYPES = [
    "PO Missing", "Vendor Mismatch", "GL Coding Required",
    "Tax Code Missing", "Line Tagging Failure",
]

_APA_EXC_SOP = {
    "PO Missing":           "po_missing",
    "Vendor Mismatch":      "vendor_mismatch",
    "GL Coding Required":   "gl_coding",
    "Tax Code Missing":     "tax_code",
    "Line Tagging Failure": "line_tagging",
}

_APA_EXC_ISSUES = {
    "PO Missing": [
        "No PO reference found on this invoice",
        "Invoice amount exceeds ₹10,000 threshold — PO is mandatory for processing",
        "Invoice on hold pending PO confirmation from requestor",
    ],
    "Vendor Mismatch": [
        "Vendor name on invoice does not match vendor master record",
        "GST number requires verification against vendor master",
        "Check for spelling variations or recent vendor name changes",
    ],
    "GL Coding Required": [
        "GL code not assigned for one or more line items",
        "Current GL code may not match vendor category in vendor master",
        "Verify correct GL code from the suggested GL field in vendor master",
    ],
    "Tax Code Missing": [
        "Tax code not specified for all line items",
        "HSN/SAC code not verified against applicable GST rate",
        "Finance team confirmation required for correct tax rate selection",
    ],
    "Line Tagging Failure": [
        "Line item description does not match PO line description",
        "Cost centre not assigned to one or more line items",
        "Manual tagging required — verify against the correct PO lines",
    ],
}

_APA_TICKET_TRIGGERS = [
    "po exists but still failing", "system issue", "erp error",
    "keeps failing", "still failing", "it ticket", "raise ticket", "erp issue",
]


def _apa_priority(status: str, amount: float) -> str:
    s = status.strip().lower()
    if s == "on-hold" and amount > 100_000:
        return "High"
    if s in ("on-hold", "pending"):
        return "Medium"
    return "Low"


def _apa_exc_type(hold_ids: list, invoice_id: str) -> str:
    try:
        idx = hold_ids.index(invoice_id)
    except ValueError:
        idx = 0
    return _APA_EXC_TYPES[idx % len(_APA_EXC_TYPES)]


def _apa_line_items(amount: float, gl: str, exc_type: str) -> list:
    a1 = round(amount * 0.65, 2)
    a2 = round(amount - a1, 2)
    gl2  = "" if exc_type == "GL Coding Required" else gl
    tax  = None if exc_type == "Tax Code Missing"  else "GST 18%"
    return [
        {"Description": "Professional Services", "Qty": 1,
         "Unit Price (₹)": f"{a1:,.2f}", "GL Code": gl,  "Tax Code": tax},
        {"Description": "Support & Maintenance",  "Qty": 1,
         "Unit Price (₹)": f"{a2:,.2f}", "GL Code": gl2, "Tax Code": tax},
    ]


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    page_dashboard()
elif page == "Invoice Processing":
    page_invoice_processing()
elif page == "Invoice Register":
    page_invoice_register()
elif page == "AP Pipeline":
    page_ap_pipeline()
elif page == "Master Data":
    page_master_data()
