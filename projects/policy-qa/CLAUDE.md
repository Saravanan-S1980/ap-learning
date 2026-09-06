# CLAUDE.md

This is the project context for Claude Code. Read this first, every session.

## CRITICAL WORKFLOW RULES (read these before anything else)

These rules override anything else you might infer from the rest of this document or from the user's prompts.

**1. No code without explicit approval.**

Do not create files. Do not write code. Do not run commands that modify the filesystem until I (the user) have explicitly approved a written plan in this exact format:

> APPROVED: [one-sentence description of what to build]

If I haven't typed that, you're still in planning mode. Asking clarifying questions is encouraged. Writing code is not.

**2. When in doubt, discuss, don't build.**

If a prompt could be read as either "discuss" or "build," default to discuss. Ask: "Do you want me to discuss the approach first, or build it directly?"

**3. One step at a time.**

Even after approval, build the smallest possible piece, then stop and show me. Wait for review before continuing to the next piece.

**4. Plan format.**

When proposing a plan, use this structure:

- What I propose to build (one sentence)
- What I'll NOT build in this step (one sentence)
- Files I'll create or modify (bulleted list)
- How you'll verify it works (one sentence)

Then wait for me to type APPROVED.

## Product

**Name:** Policy Pal (working title, can change)

**What it does:** Lets a user upload their health insurance policy PDF and ask plain-language questions about it. Returns answers grounded in the actual policy with section citations.

**Why:** Indians buy health insurance and never read the policy. When they need to claim (parent in hospital, surgery scheduled, accident), they panic-read 40 pages of legalese trying to find one answer. This product gives them that answer in seconds.

**Primary user:** Working Indian, age 28-45, has at least one health insurance policy (own, family floater, or employer-provided). English-literate. Smartphone-first.

**Secondary user:** Their parents, for whom they bought insurance and who occasionally have questions.

## MVP scope (locked)

**In scope:**
- Health insurance policies only (no term life, no car, no travel)
- English language only
- Web app (mobile-responsive), no native app
- One policy per user account at MVP
- 30-day pass: ₹49 for unlimited questions on one policy
- Subscription: ₹99/month for unlimited policies

**Out of scope until we have paying users:**
- Multiple insurance types
- Regional language support
- Native mobile app (Capacitor wrapping comes later)
- Multi-policy comparison
- Claim assistance features
- Family/shared policy access

If a feature isn't in the "in scope" list, push back when I ask for it. Remind me of the MVP discipline.

## Locked architecture decisions

Do not re-litigate these. They were decided after research and trade-off discussion.

**Backend:** Python + FastAPI. Matches my existing Health Protocol Builder stack.

**Frontend:** React + Vite + Tailwind. Mobile-first design.

**Database:** SQLite for MVP. Migrate to Postgres only when concurrent writes become a problem.

**PDF processing:** pdfplumber for text extraction. Most health policies are text-based PDFs, not scans. Add OCR fallback only if real users hit it.

**Chunking:** ~800 token chunks with 100 token overlap. Preserve section headers as metadata. Tune empirically with real policies.

**Embeddings:** Voyage AI (voyage-3 or latest). Anthropic's recommended embedding partner. Better retrieval quality than OpenAI for the cost.

**Vector storage:** sqlite-vec extension for MVP. One file, no separate service. Move to dedicated vector DB only when scale demands it.

**Answer generation:** Claude Sonnet 4.6 (model string `claude-sonnet-4-6`).

**Why Sonnet not Haiku for answers:** Writing quality matters. People are trusting answers about their health coverage. Worth the extra cost per call.

**Why not Opus 4.7:** Cost. Sonnet is sufficient for grounded Q&A given a tight prompt and good retrieval.

**Auth:** Google sign-in via Firebase Auth. Cheapest path to working auth.

**Payments:** Razorpay (India primary). Stripe added when we go global.

**Hosting:** Backend on Railway, frontend on Vercel. Both have generous free tiers for MVP.

## Coding principles

**Write code that the PM (me) can read.** I've been coding less than I've been managing for years. Default to clear over clever. Comment the non-obvious parts.

**Small functions, named clearly.** A function called `chunk_policy_text` should chunk policy text and do nothing else.

**Type hints everywhere.** I use them in Health Protocol Builder, keep using them.

**Pydantic for all API contracts.** No raw dicts crossing endpoint boundaries.

**Errors are user-facing.** Every endpoint returns a clear error message in JSON, not a stack trace. The frontend should be able to display it directly.

**One feature per PR mentally.** Don't sprawl. If I ask for chunking, build chunking. Don't also rewrite the embedding code.

## Style rules for any text you write or suggest I write

These apply to UI copy, error messages, README files, commit messages, everything user-facing.

- Short paragraphs. 1-2 sentences default, 3 max.
- Active voice. Direct address with "you."
- No em dashes. Use commas or periods.
- Contractions always: "it's" not "it is", "you'll" not "you will".

**Banned words:** delve, leverage, unlock, paradigm, seamless, robust, holistic, transformative, optimize, elevate, foster, align, showcase, highlight, underscore, crucial, pivotal, meticulous, vibrant, unparalleled, cutting-edge, innovative, synergy, groundbreaking, empower, streamline, game-changer, testament, garner, enhance, scalable, accelerate, dynamic, reimagine, unprecedented, intuitive, captivate.

**Banned phrases:** "In today's X", "It's important to note", "In order to", "Let's dive in/explore/unpack", "Moving forward", "That said", "Furthermore/Additionally/Moreover", "Let that sink in", "Straightforward."

**Banned constructions:** Em dashes. Negative parallelisms ("Not X. Y." or "It's not about X, it's about Y"). "Serves as / stands as / represents a / marks a" - use "is." Rule-of-three adjective lists. Meta commentary ("In this section I will...").

## The 8-week build plan

Each week is roughly 7 hours of my time. Plan against that budget.

**Week 1 (current): PDF ingestion**
Get 3 real health policy PDFs. Build the extraction + chunking pipeline. Output: a script that turns a policy PDF into clean, structured chunks with metadata.

**Week 2: Embedding and retrieval**
Set up Voyage embeddings. Store in sqlite-vec. Build retrieval function. Test: ask 10 questions against 1 policy, verify retrieval surfaces the right chunks 8+ times.

**Week 3: Answer generation**
Wire retrieval to Claude Sonnet. Write the answer prompt with strict grounding rules. Eval against 30 questions across 3 policies.

**Week 4: FastAPI backend**
Wrap everything in endpoints: /upload-policy, /ask, /policies. SQLite for persistence. No auth yet.

**Week 5: Frontend MVP**
React app. Policy upload screen, chat-style Q&A interface. Mobile-first. No payment yet.

**Week 6: Auth and payments**
Firebase Auth for Google sign-in. Razorpay for payments. Free first 3 questions, then payment gate.

**Week 7: Polish**
Error handling, edge cases, loading states, the unglamorous stuff.

**Week 8: Deploy and reach out to users**
Railway + Vercel deployment. Reach back to the 20 people I should have talked to during validation.

## How to work with me

**Propose before you build.** For any non-trivial piece, give me 2-3 design options with trade-offs before writing code. I'll pick.

**Explain trade-offs in PM terms.** "This approach is faster to ship but harder to debug" beats "this uses async iterators which provide better backpressure semantics."

**Stop me from scope creep.** If I ask for something that's out of MVP scope, remind me before building it.

**Show me what changed.** After any change, summarize what files were modified and why. Don't make me hunt.

**Test as we go.** Don't write code without verifying it runs. If I ask for chunking, write the function AND a test script that runs it on a real PDF.

## What I'm bringing to this

- Python familiarity from Health Protocol Builder (FastAPI + Claude API)
- 24 years of PM experience (I can think about users and trade-offs)
- 5-10 hours per week of evening time
- An Anthropic API key for the production app
- A Claude Pro subscription for using you (Claude Code)

## What I'm NOT bringing

- Deep RAG experience. Teach me as we go.
- Frontend depth. I can read React, but explain non-obvious patterns.
- DevOps. Keep deployment simple.
