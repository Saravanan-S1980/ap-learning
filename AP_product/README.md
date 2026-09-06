# AP Suite

An AI-native accounts payable product. Invoices arrive as PDF or image by email or shared folder, and the system extracts, validates, matches, codes, routes, and posts them to an ERP. Built to learn the full AI stack while building something real.

## What this is

A production-foundation build, not a toy. The architecture is meant to grow: real database, real API, real vector search, real agents. We build it in thin vertical slices so each slice teaches one part of the stack and leaves you with working software.

See `ROADMAP.md` for the module-by-module plan and `docs/architecture.md` for how the pieces fit.

## Repo layout

```
AP_product/
  backend/        Python + FastAPI service (the brain)
  frontend/       React validation UI (added in a later module)
  data/
    master/       Master data CSVs (vendors, materials, POs, GRNs, tax, GL, cost centers, routing)
    sample_invoices/  Test invoice PDFs
  docs/           Architecture and design notes
  ROADMAP.md      The learning + build curriculum
```

## Stack

- Python 3.11+, FastAPI
- PostgreSQL with the pgvector extension (business data and embeddings in one place)
- Claude (Anthropic API) for extraction, classification, and coding
- React for the validation UI
- Docker for a reproducible environment
- GitHub for version control

## Status

Module 1 complete: data foundation. Master data and sample invoices exist. Next: environment and the first extraction slice.
