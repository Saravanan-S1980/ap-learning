"""
pipeline.py — Full AP (Accounts Payable) Processing Pipeline
-------------------------------------------------------------
Reads every extracted JSON file from extracted_data/ and runs each
invoice through 4 clearly separated stages:

  Stage 1  EXTRACTIQ   — Display key fields from the extracted JSON.
  Stage 2  PROCESSORIQ — 3-way match: PO, GRN, GL code, approval limit.
  Stage 3  AUDITIQ     — Fraud checks: duplicate invoice, amount anomaly.
  Stage 4  HELPDESKIQ  — Claude writes the final decision and action note.

At the end a summary table shows the decision and SLA for every invoice.

Usage:
    python pipeline.py
"""

# ── STANDARD LIBRARY IMPORTS ─────────────────────────────────────────────────
import sys      # used immediately below to set UTF-8 output on Windows
import os       # file/folder operations
import json     # read extracted JSON files, serialise tool results
import csv      # read the master CSV reference files
import glob     # find all JSON files in extracted_data/
from datetime import datetime, timedelta  # used in duplicate date comparison

# Windows terminals default to cp1252 which cannot display the emoji and
# Unicode characters that Claude's responses contain. reconfigure() switches
# stdout to UTF-8 for this process; errors='replace' prints '?' for any
# remaining unencodable characters instead of crashing.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── THIRD-PARTY IMPORTS ───────────────────────────────────────────────────────
from dotenv import load_dotenv   # reads ANTHROPIC_API_KEY from .env
import anthropic                 # official Anthropic Python SDK

# ── 1. INITIALISE CLIENT ─────────────────────────────────────────────────────
# load_dotenv() sets ANTHROPIC_API_KEY as an environment variable so the
# Anthropic client can pick it up automatically without us hard-coding it.
load_dotenv()
client = anthropic.Anthropic()

# ── 2. CSV HELPER ─────────────────────────────────────────────────────────────
def read_csv(filename: str) -> list[dict]:
    """
    Opens a CSV file and returns its rows as a list of dictionaries.
    Each dictionary represents one row, with column headers as keys.

    Example — for vendor_master.csv:
        [{"vendor_name": "Wipro Limited", "category": "IT Services", ...}, ...]
    """
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ── 3. TOOL FUNCTIONS ─────────────────────────────────────────────────────────
# These are real Python functions that do the actual data lookups.
# Claude decides WHEN to call them; our code decides HOW they run.
# Every function returns a plain Python dict — we convert it to JSON
# before sending the result back to Claude.

def lookup_vendor(vendor_name: str) -> dict:
    """
    Reads vendor_master.csv.
    Returns the vendor's category, approval limit, status, and suggested
    GL code. Returns an error dict if the vendor is not on the master list.
    """
    rows = read_csv("vendor_master.csv")
    # Case-insensitive search so minor name differences don't break the lookup
    for row in rows:
        if row["vendor_name"].strip().lower() == vendor_name.strip().lower():
            return {
                "found": True,
                "vendor_name":        row["vendor_name"],
                "category":           row["category"],
                "approval_limit_inr": float(row["approval_limit_inr"]),
                "status":             row["status"],
                "suggested_gl_code":  row["suggested_gl_code"],
            }
    return {"found": False, "error": f"Vendor '{vendor_name}' not found in vendor master."}


def match_po(po_number: str, vendor_name: str, amount_inr: float) -> dict:
    """
    Reads po_master.csv.
    Checks three things:
      1. Does this PO number exist?
      2. Is the PO still open (not closed/cancelled)?
      3. Is the invoice amount within 10% of the PO amount?

    Returns match_status: "full" | "partial" | "none"
    "full"    — PO exists, open, and amount is within ±10 %
    "partial" — PO exists and is open but amount differs by more than 10 %
    "none"    — PO not found or PO is closed
    """
    rows = read_csv("po_master.csv")
    for row in rows:
        if row["po_number"].strip().upper() == po_number.strip().upper():
            # PO found — now check status
            if row["status"].strip().lower() != "open":
                return {
                    "match_status": "none",
                    "reason": f"PO {po_number} exists but status is '{row['status']}' (not open).",
                }
            # Check vendor name (case-insensitive)
            if row["vendor_name"].strip().lower() != vendor_name.strip().lower():
                return {
                    "match_status": "none",
                    "reason": f"PO {po_number} is assigned to '{row['vendor_name']}', not '{vendor_name}'.",
                }
            # Compare amounts — allow ±10 % tolerance
            po_amount   = float(row["po_amount_inr"])
            difference  = abs(amount_inr - po_amount)
            pct_diff    = (difference / po_amount) * 100
            if pct_diff <= 10:
                return {
                    "match_status":   "full",
                    "po_amount_inr":  po_amount,
                    "invoice_amount": amount_inr,
                    "variance_pct":   round(pct_diff, 2),
                    "reason":         f"Invoice amount is {pct_diff:.1f}% from PO amount — within 10% tolerance.",
                }
            else:
                return {
                    "match_status":   "partial",
                    "po_amount_inr":  po_amount,
                    "invoice_amount": amount_inr,
                    "variance_pct":   round(pct_diff, 2),
                    "reason":         f"Invoice amount is {pct_diff:.1f}% from PO amount — exceeds 10% tolerance.",
                }
    # PO number was not found at all
    return {
        "match_status": "none",
        "reason": f"PO '{po_number}' not found in PO master. Invoice may have been submitted without a valid PO.",
    }


def match_grn(po_number: str) -> dict:
    """
    Reads grn_master.csv.
    Checks whether goods/services were received for this PO.

    Returns grn_status: "received" | "partial" | "not_received"
    "received"     — GRN exists and is fully received
    "partial"      — GRN exists but only partially received
    "not_received" — No GRN found for this PO
    """
    rows = read_csv("grn_master.csv")
    for row in rows:
        if row["po_number"].strip().upper() == po_number.strip().upper():
            return {
                "grn_status":    row["grn_status"],
                "grn_number":    row["grn_number"],
                "received_date": row["received_date"],
                "vendor_name":   row["vendor_name"],
            }
    return {
        "grn_status": "not_received",
        "reason": f"No Goods Receipt Note found for PO '{po_number}'.",
    }


def validate_gl_code(gl_code: str, vendor_category: str) -> dict:
    """
    Reads gl_master.csv.
    Checks that the proposed GL code is appropriate for this vendor's category.
    For example, GL 5200 (Freight & Logistics) is valid for a Logistics vendor
    but not for an IT Services vendor.

    Returns status: "valid" | "invalid"
    """
    rows = read_csv("gl_master.csv")
    for row in rows:
        if str(row["gl_code"]).strip() == str(gl_code).strip():
            # The valid_for_categories column is a comma-separated list
            valid_cats = [c.strip() for c in row["valid_for_categories"].split(",")]
            if vendor_category.strip() in valid_cats:
                return {
                    "status":      "valid",
                    "gl_code":     gl_code,
                    "description": row["description"],
                    "reason":      f"GL {gl_code} ({row['description']}) is valid for '{vendor_category}'.",
                }
            else:
                return {
                    "status":      "invalid",
                    "gl_code":     gl_code,
                    "description": row["description"],
                    "reason":      f"GL {gl_code} ({row['description']}) is not valid for '{vendor_category}'. Valid categories: {row['valid_for_categories']}.",
                }
    return {
        "status": "invalid",
        "gl_code": gl_code,
        "reason":  f"GL code '{gl_code}' not found in GL master.",
    }


def check_approval_limit(vendor_name: str, amount_inr: float) -> dict:
    """
    Reads vendor_master.csv.
    Compares the invoice grand total against the vendor's pre-approved
    spending limit. Anything above the limit must go to a senior approver.

    Returns status: "within_limit" | "exceeds_limit"
    """
    rows = read_csv("vendor_master.csv")
    for row in rows:
        if row["vendor_name"].strip().lower() == vendor_name.strip().lower():
            limit = float(row["approval_limit_inr"])
            if amount_inr <= limit:
                return {
                    "status":             "within_limit",
                    "amount_inr":         amount_inr,
                    "approval_limit_inr": limit,
                    "headroom_inr":       round(limit - amount_inr, 2),
                }
            else:
                excess = round(amount_inr - limit, 2)
                return {
                    "status":             "exceeds_limit",
                    "amount_inr":         amount_inr,
                    "approval_limit_inr": limit,
                    "excess_inr":         excess,
                    "reason":             f"Invoice exceeds approval limit by INR {excess:,.2f}.",
                }
    return {"status": "unknown", "reason": f"Vendor '{vendor_name}' not found in vendor master."}


def check_duplicate(vendor_name: str, amount_inr: float, invoice_date: str) -> dict:
    """
    Reads invoices.csv (historical paid/pending invoices).
    Flags as a duplicate if another invoice from the SAME vendor with the
    SAME amount exists within 30 days of this invoice's date.

    Returns result: "duplicate" | "no_duplicate"
    """
    # Parse the invoice date — handles two formats:
    #   "15-Mar-2026"  (from our extracted JSON)
    #   "2026-01-10"   (from historical invoices.csv)
    def parse_date(date_str: str) -> datetime:
        for fmt in ("%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: '{date_str}'")

    try:
        current_date = parse_date(invoice_date)
    except ValueError:
        return {"result": "error", "reason": f"Could not parse invoice date: {invoice_date}"}

    rows   = read_csv("invoices.csv")
    window = timedelta(days=30)

    for row in rows:
        # Skip rows whose vendor name doesn't match (case-insensitive)
        if row["vendor"].strip().lower() != vendor_name.strip().lower():
            continue
        try:
            hist_date   = parse_date(row["invoice_date"])
            hist_amount = float(row["amount_inr"])
        except (ValueError, KeyError):
            continue  # skip malformed rows

        # Check: same amount AND within 30-day window
        if abs(hist_amount - amount_inr) < 0.01 and abs((hist_date - current_date).days) <= 30:
            return {
                "result":       "duplicate",
                "matched_id":   row["invoice_id"],
                "matched_date": row["invoice_date"],
                "matched_amount": hist_amount,
                "reason":       f"Duplicate of {row['invoice_id']} (same vendor, same amount, within 30 days).",
            }

    return {"result": "no_duplicate", "vendor": vendor_name, "amount_checked": amount_inr}


def check_anomaly(vendor_name: str, amount_inr: float) -> dict:
    """
    Reads invoices.csv (historical data).
    Computes the average invoice amount for this vendor from past invoices.
    Flags as an anomaly if the current invoice is more than 2x that average.

    Returns result: "anomaly" | "normal" | "insufficient_data"
    """
    rows = read_csv("invoices.csv")
    historical_amounts = []

    for row in rows:
        if row["vendor"].strip().lower() == vendor_name.strip().lower():
            try:
                historical_amounts.append(float(row["amount_inr"]))
            except ValueError:
                continue

    if len(historical_amounts) == 0:
        return {
            "result": "insufficient_data",
            "reason": f"No historical invoices found for vendor '{vendor_name}'.",
        }

    average = sum(historical_amounts) / len(historical_amounts)
    ratio   = amount_inr / average

    if ratio > 2.0:
        return {
            "result":           "anomaly",
            "current_amount":   amount_inr,
            "average_amount":   round(average, 2),
            "ratio":            round(ratio, 2),
            "reason":           f"Invoice amount is {ratio:.1f}x the vendor average of INR {average:,.2f}.",
        }

    return {
        "result":          "normal",
        "current_amount":  amount_inr,
        "average_amount":  round(average, 2),
        "ratio":           round(ratio, 2),
    }


# ── 4. TOOL DEFINITIONS (Anthropic format) ────────────────────────────────────
# The Anthropic API uses these JSON descriptions to let Claude know WHAT
# tools are available and what parameters each tool needs.
# Claude reads the "description" fields to decide which tool to call and when.

TOOLS_STAGE2 = [
    {
        "name":        "lookup_vendor",
        "description": "Look up a vendor in vendor_master.csv. Returns the vendor's category, approval limit, active/inactive status, and the GL code suggested for this vendor type.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Exact vendor name as it appears on the invoice."}
            },
            "required": ["vendor_name"],
        },
    },
    {
        "name":        "match_po",
        "description": "Check if a Purchase Order exists in po_master.csv, is open, and the invoice amount is within 10% of the PO amount. Returns match_status: full/partial/none.",
        "input_schema": {
            "type": "object",
            "properties": {
                "po_number":   {"type": "string",  "description": "PO reference number from the invoice (e.g. PO-001)."},
                "vendor_name": {"type": "string",  "description": "Vendor name as on the invoice."},
                "amount_inr":  {"type": "number",  "description": "Invoice grand total in INR (including GST and shipping)."},
            },
            "required": ["po_number", "vendor_name", "amount_inr"],
        },
    },
    {
        "name":        "match_grn",
        "description": "Check grn_master.csv to see if goods or services for this PO have been received. Returns grn_status: received/partial/not_received.",
        "input_schema": {
            "type": "object",
            "properties": {
                "po_number": {"type": "string", "description": "PO reference number to look up."}
            },
            "required": ["po_number"],
        },
    },
    {
        "name":        "validate_gl_code",
        "description": "Validate that the proposed GL account code is appropriate for this vendor's category by checking gl_master.csv. Returns valid/invalid with a reason.",
        "input_schema": {
            "type": "object",
            "properties": {
                "gl_code":         {"type": "string", "description": "The GL account code to validate (e.g. '6100')."},
                "vendor_category": {"type": "string", "description": "The vendor category returned by lookup_vendor."},
            },
            "required": ["gl_code", "vendor_category"],
        },
    },
    {
        "name":        "check_approval_limit",
        "description": "Compare the invoice grand total against the vendor's pre-approved spending limit in vendor_master.csv. Returns within_limit or exceeds_limit.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Vendor name."},
                "amount_inr":  {"type": "number", "description": "Invoice grand total in INR."},
            },
            "required": ["vendor_name", "amount_inr"],
        },
    },
]

TOOLS_STAGE3 = [
    {
        "name":        "check_duplicate",
        "description": "Search invoices.csv for another invoice from the same vendor with the same amount within 30 days of the given invoice date. Returns duplicate or no_duplicate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name":   {"type": "string", "description": "Vendor name."},
                "amount_inr":    {"type": "number", "description": "Invoice grand total in INR."},
                "invoice_date":  {"type": "string", "description": "Invoice date as it appears on the invoice (e.g. '15-Mar-2026')."},
            },
            "required": ["vendor_name", "amount_inr", "invoice_date"],
        },
    },
    {
        "name":        "check_anomaly",
        "description": "Calculate the average invoice amount for this vendor from invoices.csv. Flag as anomaly if the current amount is more than 2x the historical average.",
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {"type": "string", "description": "Vendor name."},
                "amount_inr":  {"type": "number", "description": "Invoice grand total in INR."},
            },
            "required": ["vendor_name", "amount_inr"],
        },
    },
]

# Map each tool name to the actual Python function that runs it.
# This dict is used inside run_agent_with_tools() to dispatch calls.
TOOL_FUNCTIONS = {
    "lookup_vendor":       lookup_vendor,
    "match_po":            match_po,
    "match_grn":           match_grn,
    "validate_gl_code":    validate_gl_code,
    "check_approval_limit": check_approval_limit,
    "check_duplicate":     check_duplicate,
    "check_anomaly":       check_anomaly,
}


# ── 5. GENERIC AGENTIC LOOP ───────────────────────────────────────────────────
def run_agent_with_tools(system_prompt: str, user_prompt: str,
                          tools: list, stage_label: str) -> str:
    """
    Runs a complete Claude agentic loop for one stage.

    How the loop works:
      1. Send the user prompt + available tools to Claude.
      2. If Claude replies with stop_reason "tool_use", it wants to call
         one or more tools. We execute them and send the results back.
      3. Repeat until Claude's stop_reason is "end_turn", meaning it is
         finished and has written its final text answer.
      4. Return that final text.

    Arguments:
        system_prompt  — tells Claude what role it plays in this stage
        user_prompt    — the specific task (invoice details + instructions)
        tools          — list of Anthropic tool definitions for this stage
        stage_label    — used only for printing (e.g. "Stage 2 ProcessorIQ")
    """
    # The messages list is the full conversation history.
    # We always start with just the user's message.
    messages = [{"role": "user", "content": user_prompt}]

    # Loop until Claude stops on its own ("end_turn")
    while True:
        response = client.messages.create(
            model      = "claude-opus-4-6",
            max_tokens = 2048,
            system     = system_prompt,
            tools      = tools,
            messages   = messages,
        )

        # ── CASE A: Claude is done ────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            # Extract the text block from the response and return it
            for block in response.content:
                if block.type == "text":
                    return block.text
            return ""   # shouldn't happen, but safe fallback

        # ── CASE B: Claude wants to call tools ────────────────────────────────
        if response.stop_reason == "tool_use":
            # First, append Claude's response (which contains tool_use blocks)
            # to the conversation. This is required by the API.
            messages.append({"role": "assistant", "content": response.content})

            # Now execute every tool Claude asked for and collect the results
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue  # skip text blocks in this response

                tool_name  = block.name
                tool_input = block.input    # dict of arguments Claude chose

                # Print the tool call so the user can see what's happening
                args_str = ", ".join(f"{k}={v!r}" for k, v in tool_input.items())
                print(f"    [Tool] {tool_name}({args_str})")

                # Look up and call the real Python function
                fn     = TOOL_FUNCTIONS.get(tool_name)
                result = fn(**tool_input) if fn else {"error": f"Unknown tool: {tool_name}"}

                print(f"    [Result] {result}")

                # Package the result in the format the API expects
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,       # must match the tool_use block id
                    "content":     json.dumps(result),
                })

            # Send all tool results back to Claude as a user message
            messages.append({"role": "user", "content": tool_results})

        # Any other stop reason (shouldn't normally occur) — exit the loop
        else:
            break

    return ""


# ── 6. STAGE 1 — EXTRACTIQ ──────────────────────────────────────────────────────
def stage_1_capture(inv: dict) -> None:
    """
    Stage 1 is already done (capture.py did the PDF extraction).
    Here we simply read the extracted JSON and display the key fields.
    No API call is made in this stage.
    """
    print("\n  === STAGE 1: EXTRACTIQ ===")
    # Print the key fields a human reviewer would check at a glance
    fields = [
        ("Vendor",          inv.get("vendor_name")),
        ("Invoice Number",  inv.get("invoice_number")),
        ("Invoice Date",    inv.get("invoice_date")),
        ("Due Date",        inv.get("due_date")),
        ("PO Reference",    inv.get("po_reference")),
        ("GST Rate",        f"{inv.get('gst_rate_percent')}%"),
        ("GST Type",        inv.get("gst_type")),
        ("Grand Total",     f"INR {inv.get('grand_total_inr'):,.2f}"),
    ]
    for label, value in fields:
        print(f"  {label:<18}: {value}")


# ── 7. STAGE 2 — PROCESSORIQ (3-WAY MATCH) ────────────────────────────────────
def stage_2_ap_advance(inv: dict) -> str:
    """
    Stage 2 uses Claude + 5 tools to perform the 3-way match:
      • Vendor lookup     — is this vendor approved and active?
      • PO match          — does the PO exist, is it open, is the amount right?
      • GRN match         — were the goods/services actually received?
      • GL code check     — is the accounting code correct for this vendor type?
      • Approval limit    — does this invoice need senior sign-off?

    Returns Claude's written summary of all 5 checks.
    """
    print("\n  === STAGE 2: PROCESSORIQ — 3-WAY MATCH ===")

    system = (
        "You are an AP (Accounts Payable) validation agent performing a 3-way match. "
        "You must call ALL of the following tools in order: "
        "1) lookup_vendor, 2) match_po, 3) match_grn, "
        "4) validate_gl_code (use the suggested_gl_code from lookup_vendor), "
        "5) check_approval_limit. "
        "After all tool calls are complete, write a concise bullet-point summary "
        "of what each check found. Use PASS or FAIL labels."
    )

    # The user prompt gives Claude all the invoice data it needs to call the tools
    user = (
        f"Process this invoice through the 3-way match:\n"
        f"  Vendor:        {inv.get('vendor_name')}\n"
        f"  PO Reference:  {inv.get('po_reference')}\n"
        f"  Grand Total:   {inv.get('grand_total_inr')} INR\n"
        f"  Invoice Date:  {inv.get('invoice_date')}\n"
        f"  Invoice No:    {inv.get('invoice_number')}\n"
    )

    result = run_agent_with_tools(system, user, TOOLS_STAGE2, "Stage 2 ProcessorIQ")
    print(f"\n{result}")
    return result


# ── 8. STAGE 3 — AUDITIQ (FRAUD CHECKS) ────────────────────────────────────────
def stage_3_trace(inv: dict) -> str:
    """
    Stage 3 uses Claude + 2 tools to look for red flags:
      • Duplicate check  — has this invoice been submitted before?
      • Anomaly check    — is the amount unusually high for this vendor?

    Returns Claude's written summary.
    """
    print("\n  === STAGE 3: AUDITIQ — FRAUD & ANOMALY CHECKS ===")

    system = (
        "You are an AP fraud-detection agent. "
        "Call both tools: 1) check_duplicate and 2) check_anomaly. "
        "After both tool calls, write a concise bullet-point summary "
        "of the findings. Use CLEAR or FLAG labels."
    )

    user = (
        f"Run fraud checks for this invoice:\n"
        f"  Vendor:       {inv.get('vendor_name')}\n"
        f"  Grand Total:  {inv.get('grand_total_inr')} INR\n"
        f"  Invoice Date: {inv.get('invoice_date')}\n"
        f"  Invoice No:   {inv.get('invoice_number')}\n"
    )

    result = run_agent_with_tools(system, user, TOOLS_STAGE3, "Stage 3 AuditIQ")
    print(f"\n{result}")
    return result


# ── 9. STAGE 4 — HELPDESIQ (FINAL DECISION) ─────────────────────────────────────
def stage_4_assist(inv: dict, stage2_summary: str, stage3_summary: str) -> dict:
    """
    Stage 4 uses Claude (no tools) to synthesise all findings and produce:
      • Exception summary  — tick or cross for each check
      • Final decision     — one of four outcomes
      • Helpdesk note      — plain English explanation for a non-expert
      • Next action + SLA  — what should happen and by when

    Returns a dict with keys: decision, sla, full_text
    so main() can build the summary table.
    """
    print("\n  === STAGE 4: HELPDESIQ — FINAL DECISION ===")

    system = (
        "You are a senior AP decision agent. "
        "Based on the validation findings provided, produce EXACTLY this output structure:\n\n"
        "EXCEPTION SUMMARY:\n"
        "(list each check with ✓ PASS or ✗ FAIL)\n\n"
        "FINAL DECISION: <one of: Auto-approve | Route for approval | Return to vendor | Escalate to manager>\n\n"
        "HELPDESK NOTE:\n"
        "(2-3 sentences in plain English a non-accountant can understand)\n\n"
        "NEXT ACTION: <what needs to happen next>\n"
        "SLA: <one of: Same day | 2 business days | 5 business days>\n\n"
        "Always end your response with these two lines on their own:\n"
        "DECISION: <exact decision>\n"
        "SLA: <exact SLA>\n"
    )

    user = (
        f"Invoice: {inv.get('invoice_number')}  |  Vendor: {inv.get('vendor_name')}  "
        f"|  Amount: INR {inv.get('grand_total_inr'):,.2f}\n\n"
        f"--- PROCESSORIQ FINDINGS ---\n{stage2_summary}\n\n"
        f"--- AUDITIQ FINDINGS ---\n{stage3_summary}\n"
    )

    # Stage 4 is a single direct call — no tools needed, just generation
    with client.messages.stream(
        model      = "claude-opus-4-6",
        max_tokens = 1024,
        system     = system,
        messages   = [{"role": "user", "content": user}],
    ) as stream:
        full_text = stream.get_final_message().content[0].text

    print(f"\n{full_text}")

    # ── Parse the two structured lines at the end of Claude's response ────────
    # We asked Claude to always end with "DECISION: ..." and "SLA: ..." lines.
    # This avoids complex text parsing — we just scan the last few lines.
    decision = "Unknown"
    sla      = "Unknown"
    for line in full_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("DECISION:"):
            decision = stripped.replace("DECISION:", "").strip()
        elif stripped.startswith("SLA:"):
            sla = stripped.replace("SLA:", "").strip()

    return {"decision": decision, "sla": sla, "full_text": full_text}


# ── 10. PROCESS ONE INVOICE ───────────────────────────────────────────────────
def process_invoice(json_path: str) -> dict:
    """
    Orchestrates all 4 stages for a single invoice JSON file.
    Returns a result dict for the summary table, or raises an exception
    so the caller can count it as a failure without crashing the batch.
    """
    # Load the extracted JSON produced by capture.py
    with open(json_path, encoding="utf-8") as f:
        inv = json.load(f)

    inv_num  = inv.get("invoice_number", os.path.basename(json_path))
    vendor   = inv.get("vendor_name", "Unknown")

    print(f"\n{'#'*62}")
    print(f"  PROCESSING: {inv_num}  |  {vendor}")
    print(f"{'#'*62}")

    # Run the four stages in order, passing outputs forward
    stage_1_capture(inv)
    s2 = stage_2_ap_advance(inv)
    s3 = stage_3_trace(inv)
    s4 = stage_4_assist(inv, s2, s3)

    return {
        "invoice":  inv_num,
        "vendor":   vendor,
        "decision": s4["decision"],
        "sla":      s4["sla"],
    }


# ── 11. MAIN — BATCH LOOP + SUMMARY TABLE ─────────────────────────────────────
def main():
    """
    Finds all extracted JSON files in extracted_data/, runs each one
    through the 4-stage pipeline, and prints a final summary table.
    """
    # glob.glob returns a sorted list of file paths matching the pattern
    json_files = sorted(glob.glob("extracted_data/*.json"))

    if not json_files:
        print("No JSON files found in extracted_data/. Run capture.py first.")
        return

    print(f"\n{'='*62}")
    print(f"  AP PIPELINE — BATCH START")
    print(f"  {len(json_files)} invoices found in extracted_data/")
    print(f"{'='*62}")

    # Collect one result dict per invoice for the summary table
    results   = []
    successes = 0
    failures  = 0

    for json_path in json_files:
        try:
            result = process_invoice(json_path)
            results.append(result)
            successes += 1
        except Exception as e:
            print(f"\n  [FAILED] {json_path}: {e}")
            failures += 1
            results.append({
                "invoice":  os.path.basename(json_path),
                "vendor":   "—",
                "decision": "ERROR",
                "sla":      "—",
            })

    # ── FINAL SUMMARY TABLE ───────────────────────────────────────────────────
    print(f"\n\n{'='*62}")
    print(f"  PIPELINE COMPLETE — SUMMARY")
    print(f"  Processed: {successes} succeeded, {failures} failed")
    print(f"{'='*62}\n")

    # Column widths — make each column wide enough for its longest value
    w_inv  = max(len(r["invoice"])  for r in results) + 2
    w_vend = max(len(r["vendor"])   for r in results) + 2
    w_dec  = max(len(r["decision"]) for r in results) + 2
    w_sla  = max(len(r["sla"])      for r in results) + 2

    # Helper to build one table row
    def row(inv, vend, dec, sla):
        return (f"  | {inv:<{w_inv}}"
                f"| {vend:<{w_vend}}"
                f"| {dec:<{w_dec}}"
                f"| {sla:<{w_sla}}|")

    sep = f"  +-{'-'*w_inv}+-{'-'*w_vend}+-{'-'*w_dec}+-{'-'*w_sla}+"
    print(sep)
    print(row("Invoice", "Vendor", "Decision", "SLA"))
    print(sep)
    for r in results:
        print(row(r["invoice"], r["vendor"][:w_vend-2], r["decision"], r["sla"]))
    print(sep)
    print()


if __name__ == "__main__":
    main()
