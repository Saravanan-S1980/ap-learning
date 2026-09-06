# Architecture

This is the target shape of the system. We don't build it all at once. We grow into it slice by slice, but it helps to see where we're headed.

## The pipeline

An invoice flows left to right through these stages. Each stage either passes the invoice forward automatically or hands it to a human when confidence is low.

1. Ingestion. Email and shared folders bring in PDFs and images. We log every file, check for duplicates, and quarantine anything unreadable.
2. Extraction. Claude reads the document and returns structured data with a confidence score per field.
3. Validation and enrichment. We apply business rules, look up the vendor master, and route low-confidence fields to the AP queue.
4. Matching. For PO invoices, we match against the PO and goods receipt, using vector search to align line items semantically.
5. Coding. For non-PO invoices, we suggest GL account, tax code, and cost center from history and rules.
6. Exception handling. Anything that can't go straight through gets routed to the right resolver, with a suggested fix.
7. Posting. A payment-ready invoice goes to the ERP.

## The layers

Data layer. PostgreSQL holds master data, invoices, and audit logs. The pgvector extension stores embeddings next to that data, so semantic search and business queries share one database.

Intelligence layer. Claude handles extraction, classification, and coding suggestions. Embeddings power matching and retrieval. A self-learning loop feeds corrections and past resolutions back in.

Orchestration layer. Early on this is plain Python that calls each stage in order. Later it becomes a crew of agents (retrieval, validation, response, monitoring, supervisor) that coordinate and escalate.

Service layer. FastAPI exposes the pipeline and the queue over HTTP. The React UI and any integration talk to it here.

Presentation layer. The React validation screen is where AP staff correct low-confidence data, resolve exceptions, and approve. Work is ranked by priority.

## Why these choices

Postgres with pgvector instead of a separate vector database keeps one source of truth and one thing to operate. We can split the vector store out later if scale demands it.

Claude for extraction instead of a traditional OCR plus rules engine, because the same model reads the document, understands its structure, and returns clean data, with confidence we can gate on.

FastAPI because it's the standard for Python AI services, it's fast, and it generates API docs for free.

We add the agent framework last, not first. You'll understand multi-agent orchestration far better once you've built the single-step pieces it coordinates.
