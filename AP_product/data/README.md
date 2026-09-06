# Data

Synthetic data for a manufacturing buyer, Nordwerk, across three plants: Stuttgart (EUR), Cleveland (USD), and Pune (INR). Everything here is internally consistent, so the matching and validation logic has real ground truth to check against.

## Master data (`master/`)

| File | What it holds |
|------|---------------|
| company_codes.csv | Legal entities, plants, currencies |
| vendors.csv | 12 vendors with category, terms, critical flag |
| materials.csv | Materials with UoM and base price |
| purchase_orders.csv | PO headers |
| po_lines.csv | PO line items with price and tax code |
| goods_receipts.csv | Receipts, including one deliberately partial |
| tax_codes.csv | VAT, use tax, and GST codes by country |
| gl_accounts.csv | GL chart for inventory, expense, tax |
| cost_centers.csv | Cost centers by plant |
| routing_matrix.csv | Who resolves each exception type, with fallback chain |

## Sample invoices (`sample_invoices/`)

Seven PDFs that cover the cases the pipeline has to handle. `ground_truth.csv` records the expected outcome for each, so we can score the system later.

| File | Scenario | Expected |
|------|----------|----------|
| INV-2026-1001_clean_po | Clean PO, full receipt | Auto-post |
| INV-2026-1002_price_mismatch | Billed 9.20 vs PO 8.50 | Price mismatch exception |
| INV-2026-1003_pending_grn | Billed 50, only 40 received | Pending GRN exception |
| INV-2026-2001_non_po_consulting | No PO, services | Coding queue, needs requester |
| INV-2026-1005_german_rechnung | German language, clean PO | Auto-post, tests language detection |
| INV-2026-3001_india_gst | INR, GST, clean PO | Auto-post, tests multi-currency |
| INV-2026-1001-DUP_duplicate | Resend of 1001 | Duplicate exception |

The mismatches are intentional. They're how we'll prove the matching engine actually works rather than passing everything.
