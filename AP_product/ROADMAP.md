# AP Suite: build and learning roadmap

Two goals run in parallel. You ship a working AP product, and you learn the AI stack that an AI-native PM needs. Every module does both. You finish each one with software that runs and a concept you can explain to an engineer.

We build in thin vertical slices. A slice cuts through the whole stack for one narrow case, so you always have something working rather than a half-built layer. We widen the slice over time.

## How to read this

Each module lists what you build, the feature IDs it covers from your inventory, and the AI or engineering concept it teaches. The feature IDs map to `AP_New_Product_Feature_Inventory_v1.pdf`.

## The modules

| # | Module | You build | Feature IDs | What you learn |
|---|--------|-----------|-------------|----------------|
| 1 | Data foundation | Master data and sample invoices | (prereq) | How AP data models fit together: vendor, material, PO, GRN, tax, GL, cost center, routing |
| 2 | Environment and repo | Python env, Postgres, Git, project running locally | PF-04 | Dev environment, version control, containers, secrets |
| 3 | First extraction | Send Claude one PDF, get structured JSON back | EX-01, EX-02, EX-07 | Prompting, vision models, structured output, confidence scoring |
| 4 | The data layer | Postgres schema, load master data, store invoices | PF-02, PF-05 | Relational modeling, migrations, why a database |
| 5 | Email ingestion | Dedicated Gmail, poll it, pull attachments into the pipeline | IN-01, IN-03, IN-04, IN-08 | APIs, OAuth, polling, idempotency |
| 6 | Validation and enrichment | Confidence-gated queue, business rules, vendor lookup | VL-01 to VL-06, IN-06, IN-09 | Decision thresholds, the human-in-the-loop pattern, deduplication |
| 7 | Vectors and matching | Embeddings, semantic PO line matching, 2/3-way match | MT-01 to MT-06, EX-03 | Embeddings, vector search, pgvector, similarity, fuzzy matching |
| 8 | Coding intelligence | GL, tax, dimension suggestions for non-PO invoices | CD-01 to CD-06 | Retrieval-augmented generation, few-shot from history, classification |
| 9 | Exception handling | Routing matrix, fallback cascade, next-best-action | EXC-01 to EXC-07 | Rules plus ML, recommendation from patterns, escalation logic |
| 10 | Self-learning loop | Learn from corrections and past resolutions | EX-09, EXC-06, EXC-08 | Feedback loops, online learning, pattern mining, auto-resolution |
| 11 | The validation UI | React screen for the AP queue with priority sorting | VL-04, VL-07, AG-01, AG-02, PF-03, PF-06 | Frontend basics, prioritization, work allocation, dashboards |
| 12 | Agentic orchestration | A crew of agents that coordinate the pipeline | AG-03 to AG-06 | Multi-agent frameworks, tool use, supervisor patterns, autonomy gates |
| 13 | Evals and quality | Test sets, accuracy scoring, regression checks | EX-07, PF-03 | Evaluations, ground truth, metrics, why evals beat vibes |
| 14 | ERP posting | Post a payment-ready invoice to a mock ERP | PF-01, CD-06 | Integration patterns, idempotent writes, the system boundary |

## The self-learning and autonomy rules (your requirements, woven in)

These run through modules 6, 9, 10, and 12 rather than living in one place.

Auto-process above 90% confidence. For extraction, auto-coding, auto-tax coding, auto-tagging, and auto-PO suggestion, the system acts on its own when confidence clears 0.90. Below that, the item goes to the AP queue. You'll see this gate first in module 3 and enforce it everywhere after.

Auto-resolution from history. The system learns how past exceptions got resolved (auto-GRN, pending GRN, price mismatch) and applies the same fix when the pattern repeats. Built in modules 9 and 10.

Requester and resolver recommendation. When a non-PO invoice names no requester, or the named approver keeps forwarding or not responding, the system recommends the right person from history. Built in module 10.

Prioritization. Items needing a human (low-confidence data entry, AP corrections, approvals, resolutions) get ranked by critical vendor, invoice value, and due-date proximity. Built in module 11.

## Pace

One module is roughly one to three working sessions. We don't move on until the current slice runs. You can always ask me to slow down on a concept or speed past one you already know.
