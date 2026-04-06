"""
capture.py — AP Pipeline: ExtractIQ Stage
----------------------------------------
Automatically finds every PDF in the sample_invoices/ folder, extracts
the raw text, sends it to Claude, and saves the structured field data as
a JSON file in extracted_data/.

At the end it prints a summary:
  - how many invoices succeeded
  - how many failed (with the reason)
  - the list of JSON files created

Usage:
    python capture.py
"""

import os           # lets us create folders and build file paths
import json         # lets us parse and save JSON data
import glob         # lets us search for files matching a pattern (e.g. *.pdf)

# python-dotenv loads the ANTHROPIC_API_KEY from the .env file
# into the environment so the Anthropic SDK can find it automatically.
from dotenv import load_dotenv

# PyPDF2 is used to open PDF files and extract their text content.
import PyPDF2

# The Anthropic SDK is the official Python client for Claude.
import anthropic


# ── 1. LOAD THE API KEY ──────────────────────────────────────────────────────
# load_dotenv() reads the .env file in the current directory and sets
# each key=value line as an environment variable for this process.
load_dotenv()

# Now create the Anthropic client. It automatically reads ANTHROPIC_API_KEY
# from the environment — no need to pass the key manually.
client = anthropic.Anthropic()


# ── 2. THE PROMPT WE SEND TO CLAUDE ─────────────────────────────────────────
# This exact prompt tells Claude what fields to look for and how to respond.
# Returning ONLY JSON (no extra text) makes it easy to parse the response.
EXTRACTION_PROMPT = (
    "You are an AP invoice parser. "
    "Extract the following fields from this invoice text and return ONLY a valid "
    "JSON object with these exact keys: "
    "invoice_number, vendor_name, vendor_gst, invoice_date, due_date, po_reference, "
    "line_items (array with keys: description, quantity, unit_price_inr, total_inr), "
    "subtotal_inr, shipping_charges_inr, "
    "gst_type (CGST+SGST or IGST), gst_rate_percent, gst_amount_inr, grand_total_inr, "
    "payment_terms, bank_account, ifsc_code, hsn_sac_code. "
    "If any field is not found return null for that field. "
    "Return JSON only — no explanation, no markdown."
)


# ── 3. EXTRACT TEXT FROM THE PDF ─────────────────────────────────────────────
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file and concatenates the text from every page.

    PyPDF2 reads the PDF page by page. Each page has an extract_text()
    method that returns the visible text on that page as a plain string.
    We join all pages with a newline so the text flows naturally.
    """
    text_pages = []

    # 'rb' means "read binary" — PDFs are binary files, not plain text.
    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)

        print(f"  PDF has {len(reader.pages)} page(s). Extracting text...")

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:                        # skip blank pages
                text_pages.append(page_text)
                print(f"  Page {page_num}: extracted {len(page_text)} characters.")

    # Join all pages into one big string separated by newlines.
    return "\n".join(text_pages)


# ── 4. CALL CLAUDE TO PARSE THE INVOICE ──────────────────────────────────────
def extract_fields_with_claude(invoice_text: str) -> dict:
    """
    Sends the raw invoice text to Claude and asks it to return a JSON
    object containing every invoice field we care about.

    We use streaming here so the response arrives incrementally — this
    prevents request timeouts if Claude takes a while to generate the JSON.
    get_final_message() waits until the full response is ready and
    returns a single complete message object.
    """
    print("\n  Sending text to Claude for field extraction (streaming)...")

    # Build the user message: the extraction prompt + the raw invoice text.
    user_message = f"{EXTRACTION_PROMPT}\n\n--- INVOICE TEXT START ---\n{invoice_text}\n--- INVOICE TEXT END ---"

    # client.messages.stream() opens a streaming connection to the API.
    # Inside the 'with' block we receive tokens as they arrive.
    # get_final_message() collects everything and returns it once done.
    with client.messages.stream(
        model="claude-opus-4-6",   # most capable model — best for extraction accuracy
        max_tokens=2048,           # enough room for a detailed JSON response
        messages=[
            {"role": "user", "content": user_message}
        ],
    ) as stream:
        final_message = stream.get_final_message()

    # The response content is a list of blocks. We want the one whose
    # type is "text" — that contains Claude's JSON reply.
    raw_response = ""
    for block in final_message.content:
        if block.type == "text":
            raw_response = block.text
            break

    print(f"  Claude replied ({len(raw_response)} characters). Parsing JSON...")

    # Claude was told to return ONLY JSON, but sometimes it wraps it in
    # markdown code fences (```json ... ```). Strip those if present.
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        # Remove the opening fence (e.g. ```json) and the closing ```
        lines = cleaned.splitlines()
        lines = [l for l in lines if not l.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    # Parse the JSON string into a Python dictionary.
    extracted_data = json.loads(cleaned)
    return extracted_data


# ── 5. PRINT THE EXTRACTED FIELDS ────────────────────────────────────────────
def print_extracted_fields(data: dict) -> None:
    """
    Prints every extracted field in a readable labelled format.
    Line items (the table rows) are printed as a sub-list.
    """
    # Fields we print individually — in a natural reading order.
    simple_fields = [
        ("Invoice Number",       "invoice_number"),
        ("Vendor Name",          "vendor_name"),
        ("Vendor GST",           "vendor_gst"),
        ("Invoice Date",         "invoice_date"),
        ("Due Date",             "due_date"),
        ("PO Reference",         "po_reference"),
        ("Payment Terms",        "payment_terms"),
        ("Subtotal (INR)",       "subtotal_inr"),
        ("Shipping & Handling",  "shipping_charges_inr"),
        ("GST Type",             "gst_type"),
        ("GST Rate (%)",         "gst_rate_percent"),
        ("GST Amount (INR)",     "gst_amount_inr"),
        ("Grand Total (INR)",    "grand_total_inr"),
        ("Bank Account",         "bank_account"),
        ("IFSC Code",            "ifsc_code"),
        ("HSN / SAC Code",       "hsn_sac_code"),
    ]

    print("\n" + "=" * 60)
    print("  EXTRACTED INVOICE FIELDS")
    print("=" * 60)

    for label, key in simple_fields:
        value = data.get(key)
        # Show "—" when Claude returned null / field was missing.
        display = value if value is not None else "—"
        print(f"  {label:<26}: {display}")

    # Line items need special handling because they are a list of dicts.
    print(f"\n  {'Line Items':<26}:")
    line_items = data.get("line_items") or []
    if line_items:
        for i, item in enumerate(line_items, start=1):
            desc      = item.get("description", "—")
            qty       = item.get("quantity", "—")
            unit_p    = item.get("unit_price_inr", "—")
            total     = item.get("total_inr", "—")
            print(f"    [{i}] {desc}")
            print(f"        Qty: {qty}  |  Unit Price: {unit_p}  |  Total: {total}")
    else:
        print("    (no line items found)")

    print("=" * 60)


# ── 6. SAVE THE JSON TO DISK ──────────────────────────────────────────────────
def save_to_json(data: dict, invoice_number: str) -> str:
    """
    Saves the extracted dictionary to a JSON file inside extracted_data/.
    The filename is  extracted_<invoice_number>.json  (e.g. extracted_INV-5001.json).
    Returns the full file path so we can tell the user where it was saved.
    """
    output_dir = "extracted_data"
    os.makedirs(output_dir, exist_ok=True)   # create the folder if it doesn't exist

    filename  = f"extracted_{invoice_number}.json"
    file_path = os.path.join(output_dir, filename)

    # indent=2 makes the JSON file nicely formatted and human-readable.
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return file_path


# ── 7. PROCESS A SINGLE PDF ──────────────────────────────────────────────────
def process_invoice(pdf_path: str) -> str:
    """
    Runs the full extraction pipeline for one PDF file.

    Returns the path of the saved JSON file on success.
    Raises an exception on any failure so the caller can catch it and
    record it as a failed invoice without stopping the whole batch.
    """
    print(f"\n{'='*60}")
    print(f"  Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*60}")

    # Step A: pull raw text out of the PDF.
    invoice_text = extract_text_from_pdf(pdf_path)

    if not invoice_text.strip():
        # raise stops this function immediately and sends the error message
        # up to whoever called process_invoice().
        raise ValueError("No text could be extracted from the PDF.")

    # Step B: ask Claude to identify every field.
    extracted_data = extract_fields_with_claude(invoice_text)

    # Step C: show the fields on screen.
    print_extracted_fields(extracted_data)

    # Step D: save to JSON.
    # Prefer the invoice number Claude found; fall back to the PDF filename.
    invoice_number = extracted_data.get("invoice_number") or os.path.splitext(
        os.path.basename(pdf_path)
    )[0]

    saved_path = save_to_json(extracted_data, invoice_number)
    print(f"\n  JSON saved to: {saved_path}")
    return saved_path


# ── 8. MAIN — LOOP OVER ALL PDFs AND PRINT SUMMARY ───────────────────────────
def main():
    """
    Entry point for batch mode.

    1. Finds every .pdf file in sample_invoices/ (sorted alphabetically).
    2. Processes each one, catching errors individually so one bad PDF
       doesn't stop the rest from being processed.
    3. Prints a final summary table.
    """
    input_folder = "sample_invoices"

    # glob.glob() returns a list of file paths that match the pattern.
    # The ** wildcard is not needed here — we just want the top-level folder.
    # sorted() ensures we always process files in alphabetical order.
    pdf_files = sorted(glob.glob(os.path.join(input_folder, "*.pdf")))

    if not pdf_files:
        print(f"No PDF files found in '{input_folder}/'. Nothing to process.")
        return

    print(f"\n{'='*60}")
    print(f"  EXTRACTIQ STAGE — BATCH MODE")
    print(f"  Found {len(pdf_files)} PDF(s) in '{input_folder}/'")
    print(f"{'='*60}")

    # These lists track the outcome of every file so we can summarise at the end.
    successes = []   # list of (pdf filename, saved json path) tuples
    failures  = []   # list of (pdf filename, error message) tuples

    # Loop through every PDF one at a time.
    for pdf_path in pdf_files:
        pdf_name = os.path.basename(pdf_path)
        try:
            # Try to process the invoice. If anything goes wrong inside
            # process_invoice() an exception is raised and we jump to 'except'.
            saved_path = process_invoice(pdf_path)
            successes.append((pdf_name, saved_path))

        except Exception as e:
            # Something went wrong (bad PDF, API error, JSON parse error, etc.).
            # Record the failure with the error message and keep going.
            print(f"\n  [FAILED] {pdf_name}: {e}")
            failures.append((pdf_name, str(e)))

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  BATCH COMPLETE — SUMMARY")
    print(f"{'='*60}")
    print(f"  Total invoices found  : {len(pdf_files)}")
    print(f"  Successfully processed: {len(successes)}")
    print(f"  Failed                : {len(failures)}")

    # List every JSON file that was created.
    if successes:
        print(f"\n  JSON files created in extracted_data/:")
        for pdf_name, json_path in successes:
            json_file = os.path.basename(json_path)
            print(f"    + {json_file}  (from {pdf_name})")

    # List every failure with its reason so the user knows what to fix.
    if failures:
        print(f"\n  Failed invoices:")
        for pdf_name, reason in failures:
            print(f"    x {pdf_name}: {reason}")

    print(f"{'='*60}\n")


# This block only runs when the script is executed directly (not imported).
if __name__ == "__main__":
    main()
