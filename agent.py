# =============================================================================
# agent.py — AP Invoice Processing Agent using Claude tool_use
# =============================================================================
#
# WHAT IS tool_use?
# -----------------
# Normally when you call Claude, it just replies with text.
# tool_use changes this: you give Claude a list of *tools* (Python functions)
# and Claude can decide to *call* one of them mid-conversation.
#
# The flow looks like this:
#
#   You  ──► Claude: "Here is invoice INV-9001 from Wipro for ₹85,000"
#   Claude ──► You:  "I want to call check_vendor('Wipro')"   ← tool_use block
#   You  ──► Claude: "check_vendor returned: 'approved'"      ← tool_result
#   Claude ──► You:  "I want to call check_duplicate(...)"    ← tool_use block
#   You  ──► Claude: "check_duplicate returned: 'no duplicate'"
#   ... (Claude keeps calling tools until it has enough info) ...
#   Claude ──► You:  "Final answer: Decision is Approve because ..."
#
# Claude never runs your Python code itself — it just *asks* you to run it.
# Your script reads Claude's request, calls the real function, and sends the
# result back. This loop repeats until Claude says it is done (stop_reason="end_turn").
#
# =============================================================================

import sys
import os
import json          # json.dumps() converts Python dicts to text Claude can read.
import pandas as pd  # pandas reads the invoices.csv file.
from dotenv import load_dotenv
import anthropic

# Load ANTHROPIC_API_KEY from the .env file.
load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# =============================================================================
# SECTION 1 — TOOL FUNCTIONS (plain Python)
# These are ordinary functions. Claude cannot see their code — it only sees
# the descriptions you provide in the tool schema below. You write the logic;
# Claude decides *when* to call each one.
# =============================================================================

# Hardcoded vendor registry.
APPROVED_VENDORS    = {"tata consultancy", "infosys bpo", "siemens india", "wipro", "mahindra logistics"}
BLACKLISTED_VENDORS = {"shadow invoices ltd", "ghost vendor co"}   # Example blacklist.

def check_vendor(vendor_name: str) -> str:
    """Return 'approved', 'blacklisted', or 'unknown' for a given vendor name."""
    key = vendor_name.strip().lower()
    if key in BLACKLISTED_VENDORS:
        return "blacklisted"
    if key in APPROVED_VENDORS:
        return "approved"
    return "unknown"


def check_duplicate(invoice_id: str, vendor: str, amount: float) -> str:
    """
    Read invoices.csv and check whether any existing invoice has the same
    vendor AND the same amount (regardless of invoice_id).
    Returns 'duplicate found' or 'no duplicate'.
    """
    try:
        df = pd.read_csv("invoices.csv")
        # Look for rows where vendor matches AND amount matches.
        # We use str.lower() so "Wipro" == "wipro".
        vendor_match = df["vendor"].str.lower() == vendor.strip().lower()
        amount_match = df["amount_inr"].astype(float).round(2) == round(float(amount), 2)
        duplicates   = df[vendor_match & amount_match]
        if len(duplicates) > 0:
            return f"duplicate found (matched invoice_id(s): {duplicates['invoice_id'].tolist()})"
        return "no duplicate"
    except FileNotFoundError:
        return "no duplicate (invoices.csv not found — treated as clean)"


# Simple keyword-based GL code rules.
IT_VENDORS       = {"wipro", "infosys bpo", "tata consultancy", "hcl", "cognizant"}
LOGISTICS_VENDORS = {"mahindra logistics", "global freight co", "dhl", "fedex"}
UTILITY_KEYWORDS = {"electricity", "water", "power", "utility", "gas"}

def recommend_gl_code(vendor: str, description: str) -> str:
    """
    Return a GL account code based on vendor type and description keywords.
      620100 — IT / Software services
      630200 — Logistics / Freight
      640100 — Utilities
      600000 — General / Unclassified
    """
    v = vendor.strip().lower()
    d = description.strip().lower()

    if v in IT_VENDORS or any(kw in d for kw in ["software", "it ", "infrastructure", "tech", "saas"]):
        return "620100 (IT / Software services)"
    if v in LOGISTICS_VENDORS or any(kw in d for kw in ["freight", "shipping", "logistics", "courier"]):
        return "630200 (Logistics / Freight)"
    if v in {"siemens india"} or any(kw in d for kw in UTILITY_KEYWORDS):
        return "640100 (Utilities)"
    return "600000 (General / Unclassified)"


def get_approval_limit(vendor: str) -> str:
    """
    Return the monetary approval limit for a vendor.
    Known (approved) vendors: ₹1,00,000
    Unknown vendors:          ₹25,000
    """
    key = vendor.strip().lower()
    if key in APPROVED_VENDORS:
        return "₹1,00,000 (approved vendor limit)"
    return "₹25,000 (unknown vendor limit)"


# =============================================================================
# SECTION 2 — TOOL SCHEMAS (what Claude sees)
# Each entry is a dict that describes one tool to Claude.
# Claude reads the 'description' and 'input_schema' fields to understand:
#   • What the tool does (description)
#   • What arguments to pass (input_schema — standard JSON Schema format)
# Claude never sees your Python code, only this metadata.
# =============================================================================

TOOLS = [
    {
        "name": "check_vendor",
        "description": (
            "Check whether a vendor is approved, blacklisted, or unknown. "
            "Always call this first before making any AP decision."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor_name": {
                    "type": "string",
                    "description": "The exact vendor name from the invoice."
                }
            },
            "required": ["vendor_name"]
        }
    },
    {
        "name": "check_duplicate",
        "description": (
            "Check invoices.csv to see if an invoice with the same vendor and amount "
            "already exists. Call this to detect accidental double submissions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "invoice_id": {
                    "type": "string",
                    "description": "The invoice ID being checked (e.g. INV-9001)."
                },
                "vendor": {
                    "type": "string",
                    "description": "Vendor name from the invoice."
                },
                "amount": {
                    "type": "number",
                    "description": "Invoice amount in INR (numeric, no currency symbol)."
                }
            },
            "required": ["invoice_id", "vendor", "amount"]
        }
    },
    {
        "name": "recommend_gl_code",
        "description": (
            "Suggest the correct GL (General Ledger) account code based on the vendor "
            "type and invoice description. Returns the code and a short label."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Vendor name from the invoice."
                },
                "description": {
                    "type": "string",
                    "description": "Short description of what the invoice is for."
                }
            },
            "required": ["vendor", "description"]
        }
    },
    {
        "name": "get_approval_limit",
        "description": (
            "Return the maximum amount that can be auto-approved for this vendor. "
            "Use this to decide whether to Approve or Escalate based on the invoice amount."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "vendor": {
                    "type": "string",
                    "description": "Vendor name from the invoice."
                }
            },
            "required": ["vendor"]
        }
    }
]


# =============================================================================
# SECTION 3 — TOOL DISPATCHER
# When Claude asks to call a tool, it gives us:
#   tool_name  — which function to run (e.g. "check_vendor")
#   tool_input — the arguments as a dict (e.g. {"vendor_name": "Wipro"})
# This function maps the name to the real Python function and calls it.
# =============================================================================

def run_tool(tool_name: str, tool_input: dict) -> str:
    """Call the matching Python function and return its result as a string."""
    if tool_name == "check_vendor":
        return check_vendor(**tool_input)

    if tool_name == "check_duplicate":
        return check_duplicate(**tool_input)

    if tool_name == "recommend_gl_code":
        return recommend_gl_code(**tool_input)

    if tool_name == "get_approval_limit":
        return get_approval_limit(**tool_input)

    # Safety net — should never happen if tool schemas match function names.
    return f"ERROR: unknown tool '{tool_name}'"


# =============================================================================
# SECTION 4 — THE AGENTIC LOOP
# This is the heart of tool_use. Here is what happens each iteration:
#
#   1. We send our messages list to Claude.
#   2. Claude replies. Two possible outcomes:
#        a. stop_reason == "tool_use"  → Claude wants to call a tool.
#           We run the tool, add both Claude's request AND our result to messages,
#           then loop back to step 1 so Claude can continue reasoning.
#        b. stop_reason == "end_turn"  → Claude is done. We print the final answer.
#
# The messages list grows each iteration, preserving the full conversation so
# Claude always has context for what tools have already been called.
# =============================================================================

def process_invoice(invoice_id: str, vendor: str, amount: float, description: str):
    """Run the full AP agent loop for one invoice and print the result."""

    print(f"\n{'='*60}")
    print(f"  AP AGENT — Processing Invoice {invoice_id}")
    print(f"{'='*60}")
    print(f"  Vendor      : {vendor}")
    print(f"  Amount      : ₹{amount:,.0f}")
    print(f"  Description : {description}")
    print(f"{'='*60}\n")

    # The system prompt tells Claude its role and what final output to produce.
    system_prompt = """You are an AP (Accounts Payable) invoice processing agent.

Your job is to validate a new invoice by calling the available tools in a sensible order, then produce a final structured verdict.

Steps to follow:
1. Call check_vendor to verify the vendor status.
2. Call check_duplicate to check for double submission.
3. Call recommend_gl_code to get the right GL account.
4. Call get_approval_limit to know the auto-approve threshold.
5. Based on all tool results, produce your final output in this EXACT format:

---
Vendor Status     : <approved | unknown | blacklisted>
Duplicate Check   : <no duplicate | duplicate found>
Recommended GL    : <code and label>
Decision          : <Approve | Escalate | Return to Vendor>
Reason            : <one clear sentence explaining the decision>
---

Decision rules:
- Return to Vendor  if vendor is blacklisted OR a duplicate is found.
- Escalate          if amount exceeds the vendor's approval limit.
- Approve           if vendor is approved, no duplicate, and amount is within limit.
"""

    # Build the first user message describing the invoice.
    user_message = (
        f"Please process this invoice:\n"
        f"Invoice ID  : {invoice_id}\n"
        f"Vendor      : {vendor}\n"
        f"Amount (INR): {amount}\n"
        f"Description : {description}"
    )

    # messages is the conversation history we send to Claude on every API call.
    # It grows as Claude calls tools and we send results back.
    messages = [{"role": "user", "content": user_message}]

    iteration = 0   # Safety counter — prevents an infinite loop if something goes wrong.

    # ── Agentic loop ──────────────────────────────────────────────────────────
    while iteration < 10:
        iteration += 1

        # Call Claude with the full conversation history and tool definitions.
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,          # Hand Claude the list of tool schemas.
            messages=messages,
        )

        print(f"[Loop {iteration}] Claude stop_reason: {response.stop_reason}")

        # ── CASE A: Claude wants to call one or more tools ────────────────────
        if response.stop_reason == "tool_use":

            # response.content is a list; it may contain text blocks and/or tool_use blocks.
            # We add the entire assistant response to messages so Claude remembers it.
            messages.append({"role": "assistant", "content": response.content})

            # Collect results for ALL tool calls Claude made in this turn.
            # (Claude can request multiple tools at once — we handle each one.)
            tool_results = []

            for block in response.content:

                # Only process tool_use blocks; skip any text blocks.
                if block.type != "tool_use":
                    continue

                print(f"           → Calling tool: {block.name}({block.input})")

                # Actually run the Python function.
                result = run_tool(block.name, block.input)

                print(f"           ← Result: {result}")

                # A tool_result must include the tool_use_id so Claude knows
                # which tool call this result belongs to.
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,   # Must match the id Claude sent.
                    "content": result,          # The string our function returned.
                })

            # Send all tool results back to Claude as a user message.
            messages.append({"role": "user", "content": tool_results})

        # ── CASE B: Claude is done — print the final answer ───────────────────
        elif response.stop_reason == "end_turn":

            # Extract the text from the final response.
            final_text = next(
                (block.text for block in response.content if block.type == "text"),
                "(no text response)"
            )

            print(f"\n{'='*60}")
            print("  AGENT VERDICT")
            print(f"{'='*60}")
            print(final_text)
            print(f"{'='*60}\n")
            break   # Exit the loop — we are done.

        else:
            # Unexpected stop reason — log it and exit cleanly.
            print(f"Unexpected stop_reason: {response.stop_reason}. Stopping.")
            break

    else:
        # The while loop exhausted all 10 iterations without Claude finishing.
        print("ERROR: Agent did not finish within 10 iterations. Check your tools and prompt.")


# =============================================================================
# SECTION 5 — GENERATOR VERSION FOR UI (used by app.py)
# =============================================================================
# process_invoice() above uses print() — fine for the terminal.
# Streamlit can't capture print() calls, so this generator version *yields*
# one dict per agent step instead. The caller (app.py) decides how to display each step.
#
# Yield shapes:
#   {"type": "tool_call",   "name": str, "args": dict}   — Claude requested a tool
#   {"type": "tool_result", "name": str, "result": str}  — tool ran, here is the output
#   {"type": "final",       "text": str}                 — Claude's finished verdict text
#   {"type": "error",       "message": str}              — something went wrong
# =============================================================================

def process_invoice_steps(invoice_id: str, vendor: str, amount: float, description: str):
    """Generator: runs the agent loop and yields step-by-step events for UI display."""

    # Same system prompt and rules as process_invoice() above.
    system_prompt = """You are an AP (Accounts Payable) invoice processing agent.

Your job is to validate a new invoice by calling the available tools in a sensible order, then produce a final structured verdict.

Steps to follow:
1. Call check_vendor to verify the vendor status.
2. Call check_duplicate to check for double submission.
3. Call recommend_gl_code to get the right GL account.
4. Call get_approval_limit to know the auto-approve threshold.
5. Based on all tool results, produce your final output in this EXACT format:

---
Vendor Status     : <approved | unknown | blacklisted>
Duplicate Check   : <no duplicate | duplicate found>
Recommended GL    : <code and label>
Decision          : <Approve | Escalate | Return to Vendor>
Reason            : <one clear sentence explaining the decision>
---

Decision rules:
- Return to Vendor  if vendor is blacklisted OR a duplicate is found.
- Escalate          if amount exceeds the vendor's approval limit.
- Approve           if vendor is approved, no duplicate, and amount is within limit.
"""

    user_message = (
        f"Please process this invoice:\n"
        f"Invoice ID  : {invoice_id}\n"
        f"Vendor      : {vendor}\n"
        f"Amount (INR): {amount}\n"
        f"Description : {description}"
    )

    messages = [{"role": "user", "content": user_message}]

    for _ in range(10):   # Safety cap — same as process_invoice().

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "tool_use":
            # Add Claude's full response (with tool_use blocks) to the conversation.
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                # Yield the call so the UI can show "Claude is calling X..."
                yield {"type": "tool_call", "name": block.name, "args": block.input}

                result = run_tool(block.name, block.input)

                # Yield the result so the UI can show what came back.
                yield {"type": "tool_result", "name": block.name, "result": result}

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            final_text = next(
                (block.text for block in response.content if block.type == "text"),
                "(no text response)"
            )
            yield {"type": "final", "text": final_text}
            return   # Generator is done — stop iteration.

        else:
            yield {"type": "error", "message": f"Unexpected stop_reason: {response.stop_reason}"}
            return

    # If we exit the for-loop without returning, we hit the cap.
    yield {"type": "error", "message": "Agent did not finish within 10 iterations."}


# =============================================================================
# SECTION 6 — RUN THE TEST INVOICE (CLI only)
# =============================================================================

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Allow ₹ symbol in Windows terminal.
    process_invoice(
        invoice_id  = "INV-9001",
        vendor      = "Wipro",
        amount      = 85000,
        description = "IT infrastructure maintenance",
    )
