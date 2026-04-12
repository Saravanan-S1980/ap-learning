# Health Protocol Builder

## What This Is
A mobile-first health app that lets users photograph or upload blood test reports, extracts biomarkers using AI, and generates personalized evidence-based protocols (diet, supplements, lifestyle, retest schedule).

**Primary platform: Mobile (Android + iOS via Capacitor)**
**Secondary platform: Desktop browser**

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Mobile App (Capacitor)                   │
│         React + Tailwind CSS (mobile-first)          │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ ┌────────────┐ │
│  │ Upload  │→│ Review  │→│ Goals  │→│  Protocol  │ │
│  │ Screen  │ │ Markers │ │ Screen │ │   View     │ │
│  └─────────┘ └─────────┘ └────────┘ └────────────┘ │
│         Native: Camera, Push, Share, Files           │
└──────────────────────┬───────────────────────────────┘
                       │ HTTPS REST API
┌──────────────────────▼───────────────────────────────┐
│                 FastAPI Backend                        │
│  PDF Extraction → Marker Parsing → Analysis Chain     │
│         (PyMuPDF + Claude API + Reference DB)         │
│                                                       │
│  Database: SQLite (MVP) → PostgreSQL (prod)           │
└───────────────────────────────────────────────────────┘
```

## Mobile-First Design Principles

1. **Touch targets: minimum 44px height** for all buttons and interactive elements
2. **Single-column layout** — no side-by-side panels on mobile
3. **Bottom navigation** — thumb-reachable primary actions
4. **Swipe between screens** — Upload → Review → Goals → Protocol
5. **Camera-first upload** — camera button is primary, file picker is secondary
6. **Progressive disclosure** — show summary first, expand for details
7. **Offline shell** — app loads instantly, shows "analyzing..." states
8. **No horizontal scrolling ever**
9. **Font sizes: minimum 16px** body text (prevents iOS zoom on input focus)
10. **Loading states for everything** — skeleton screens, not spinners

## Project Structure

```
health-protocol-builder/
├── CLAUDE.md
├── pyproject.toml
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── markers.py       # ExtractedMarker, ExtractionResult
│   │   │   ├── protocol.py      # Protocol output models
│   │   │   └── database.py      # SQLAlchemy models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py        # POST /api/upload
│   │   │   ├── markers.py       # GET/PUT /api/markers/{id}
│   │   │   ├── analyze.py       # POST /api/analyze
│   │   │   └── protocol.py      # GET /api/protocol/{id}
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pdf_extractor.py
│   │   │   ├── marker_parser.py
│   │   │   ├── marker_normalizer.py
│   │   │   ├── marker_flagger.py
│   │   │   ├── goal_crossref.py
│   │   │   └── protocol_generator.py
│   │   ├── data/
│   │   │   ├── marker_reference.py
│   │   │   └── goals.py
│   │   └── utils/
│   │       ├── claude_client.py
│   │       └── prompts.py
│   └── tests/
│       ├── test_pdf_extractor.py
│       ├── test_marker_parser.py
│       └── fixtures/
├── frontend/
│   ├── package.json
│   ├── capacitor.config.ts      # Capacitor configuration
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   │   ├── manifest.json
│   │   └── icons/               # App icons (all sizes)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── pages/
│   │   │   ├── UploadPage.jsx
│   │   │   ├── ReviewPage.jsx
│   │   │   ├── GoalsPage.jsx
│   │   │   └── ProtocolPage.jsx
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── MobileShell.jsx    # Bottom nav, safe areas
│   │   │   │   ├── BottomNav.jsx
│   │   │   │   └── StatusBar.jsx
│   │   │   ├── upload/
│   │   │   │   ├── CameraCapture.jsx  # Native camera integration
│   │   │   │   ├── FileDropzone.jsx
│   │   │   │   └── UploadProgress.jsx
│   │   │   ├── markers/
│   │   │   │   ├── MarkerCard.jsx     # Single marker display
│   │   │   │   ├── MarkerList.jsx     # Scrollable marker list
│   │   │   │   └── MarkerEditor.jsx   # Edit modal (bottom sheet)
│   │   │   ├── goals/
│   │   │   │   └── GoalChip.jsx       # Selectable goal pill
│   │   │   ├── protocol/
│   │   │   │   ├── ProtocolSection.jsx # Collapsible section
│   │   │   │   ├── SupplementCard.jsx
│   │   │   │   ├── DietPlan.jsx
│   │   │   │   └── RetestTimeline.jsx
│   │   │   └── shared/
│   │   │       ├── Button.jsx
│   │   │       ├── Card.jsx
│   │   │       ├── BottomSheet.jsx    # Mobile modal pattern
│   │   │       ├── SkeletonLoader.jsx
│   │   │       └── Disclaimer.jsx
│   │   ├── hooks/
│   │   │   ├── useCamera.js           # Capacitor camera hook
│   │   │   ├── useApi.js
│   │   │   └── useProgress.js         # Polling-based progress
│   │   ├── services/
│   │   │   └── api.js
│   │   └── styles/
│   │       └── globals.css
│   ├── android/                       # Generated by Capacitor
│   └── ios/                           # Generated by Capacitor
└── docs/
    └── spec.md
```

## Tech Stack

### Backend
- fastapi, uvicorn[standard]
- python-multipart
- pymupdf (PDF extraction)
- anthropic (Claude API)
- pydantic, pydantic-settings
- sqlalchemy, aiosqlite

### Frontend
- react, react-dom, react-router-dom
- tailwindcss, @tailwindcss/forms
- @capacitor/core, @capacitor/cli
- @capacitor/camera (native camera)
- @capacitor/share (share protocol with doctor)
- @capacitor/push-notifications (retest reminders)
- @capacitor/filesystem (save PDF exports)
- @capacitor/haptics (touch feedback)
- lucide-react (icons)
- vite, @vitejs/plugin-react

### Capacitor Config (capacitor.config.ts)
```typescript
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.healthprotocol.app',
  appName: 'Health Protocol',
  webDir: 'dist',
  server: {
    // For dev: point to Vite dev server
    // url: 'http://192.168.x.x:5173',
    // cleartext: true
  },
  plugins: {
    Camera: {
      presentationStyle: 'fullScreen'
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    }
  }
};

export default config;
```

## Coding Standards

- Python: Type hints everywhere. Pydantic models for all data shapes.
- Async/await for all FastAPI endpoints and Claude API calls.
- Frontend: Functional components with hooks only.
- Tailwind only — mobile breakpoints first (no `sm:` prefix = mobile default).
- All touch targets minimum h-11 (44px).
- All form inputs minimum text-base (16px) to prevent iOS zoom.
- Claude prompts in `backend/app/utils/prompts.py` — never inline.
- Every Claude API call: try/except with 3x exponential backoff retry.
- Environment variables via .env, loaded by pydantic-settings.

## Mobile Screen Designs

### Screen 1: Upload (Home)
```
┌─────────────────────────┐
│ Health Protocol Builder  │ ← App header (safe area aware)
├─────────────────────────┤
│                         │
│   ┌─────────────────┐   │
│   │                 │   │
│   │   📸            │   │ ← Large camera button (primary CTA)
│   │   Take Photo    │   │    Full-width, 120px tall
│   │   of Report     │   │
│   │                 │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │ 📁 Upload PDF   │   │ ← Secondary action, smaller
│   └─────────────────┘   │
│                         │
│   ┌─ Recent Reports ──┐ │
│   │ 📋 Mar 15 - SRL   │ │ ← Previous reports list
│   │ 📋 Jan 8 - Thyro  │ │
│   └────────────────────┘ │
│                         │
├─────────────────────────┤
│  📸    📊    ⚙️        │ ← Bottom nav (Upload, History, Settings)
└─────────────────────────┘
```

### Screen 2: Review Markers
```
┌─────────────────────────┐
│ ← Back    Review Report │
├─────────────────────────┤
│ Lab: Thyrocare           │
│ Date: March 15, 2026    │
├─────────────────────────┤
│ ⚠️ 4 markers need       │ ← Alert banner (if any out of range)
│    attention             │
├─────────────────────────┤
│ ┌─ Lipid Panel ───────┐ │ ← Category headers
│ │ Triglycerides   210  │ │
│ │ ████████████░░  ⚠️  │ │ ← Visual range bar + flag
│ │ Ref: <150            │ │
│ │                      │ │
│ │ HDL            38    │ │
│ │ ██░░░░░░░░░░   ⚠️  │ │
│ │ Ref: 40-60           │ │
│ └──────────────────────┘ │
│ ┌─ Vitamins ──────────┐ │
│ │ Vitamin D      18    │ │
│ │ █░░░░░░░░░░░   🔴  │ │
│ │ Ref: 30-100          │ │
│ └──────────────────────┘ │
│                         │
│ ┌─────────────────────┐ │
│ │  Continue to Goals → │ │ ← Sticky bottom CTA
│ └─────────────────────┘ │
├─────────────────────────┤
│  📸    📊    ⚙️        │
└─────────────────────────┘
```

### Screen 3: Goals
```
┌─────────────────────────┐
│ ← Back    Your Goals    │
├─────────────────────────┤
│                         │
│ What do you want to     │
│ improve? (pick up to 3) │
│                         │
│ ┌──────────┐ ┌────────┐│
│ │❤️ Heart  │ │⚡Energy ││ ← Tappable chips, large touch
│ │  Health  │ │        ││    targets, selected = filled
│ └──────────┘ └────────┘│
│ ┌──────────┐ ┌────────┐│
│ │🏃 Fat    │ │🧬 Hor- ││
│ │  Loss    │ │  mones ││
│ └──────────┘ └────────┘│
│ ┌──────────┐ ┌────────┐│
│ │🧠 Brain  │ │💪 Ath- ││
│ │  Power   │ │  letic ││
│ └──────────┘ └────────┘│
│ ┌──────────┐ ┌────────┐│
│ │🛡️ Immune│ │🧘 Stress││
│ └──────────┘ └────────┘│
│ ┌──────────┐           │
│ │🕐 Longe- │           │
│ │  vity    │           │
│ └──────────┘           │
│                         │
│ ┌─────────────────────┐ │
│ │ Generate Protocol → │ │ ← Sticky bottom CTA
│ └─────────────────────┘ │
├─────────────────────────┤
│  📸    📊    ⚙️        │
└─────────────────────────┘
```

### Screen 4: Protocol (Scrollable)
```
┌─────────────────────────┐
│ ← Back    Your Protocol │  ┌─────────┐
│                         │  │ 📤 Share│ ← Share with doctor
├─────────────────────────┤  └─────────┘
│ ⚕️ Disclaimer: This is │
│ informational only...   │ ← Collapsible, always visible
├─────────────────────────┤
│ ▼ 🥗 Diet Changes      │ ← Collapsible sections
│ ┌──────────────────────┐│
│ │ START NOW            ││
│ │ • 200g salmon 3x/wk  ││
│ │ • 2 tbsp ground flax ││
│ │                      ││
│ │ PHASE IN (2-4 weeks) ││
│ │ • Replace rice with  ││
│ │   millet 3x/week     ││
│ └──────────────────────┘│
│                         │
│ ▼ 💊 Supplements       │
│ ┌──────────────────────┐│
│ │ Omega-3 (EPA/DHA)    ││
│ │ 2000mg · Morning     ││
│ │ With food · 12 weeks ││
│ │ Targets: Triglycerides││
│ ├──────────────────────┤│
│ │ Vitamin D3           ││
│ │ 5000 IU · Morning    ││
│ │ With fat · 12 weeks  ││
│ │ Targets: Vitamin D   ││
│ └──────────────────────┘│
│                         │
│ ▶ 🏃 Lifestyle         │ ← Collapsed by default
│ ▶ 📅 Retest Schedule   │
│                         │
│ ┌─────────────────────┐ │
│ │ 📥 Save as PDF      │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│  📸    📊    ⚙️        │
└─────────────────────────┘
```

## Key Pydantic Models

### ExtractedMarker
```python
class ExtractedMarker(BaseModel):
    name: str
    reported_name: str
    value: float | None
    qualitative_value: str | None
    unit: str
    reference_low: float | None
    reference_high: float | None
    flag: Literal["normal", "low", "high", "critical_low", "critical_high"]
    category: Literal["CBC", "Lipid", "Thyroid", "Liver", "Kidney",
                       "Vitamin", "Mineral", "Hormone", "Metabolic",
                       "Inflammatory", "Other"]
    test_date: str | None
```

### ExtractionResult
```python
class ExtractionResult(BaseModel):
    lab_name: str | None
    patient_name: str | None
    report_date: str | None
    markers: list[ExtractedMarker]
    extraction_confidence: float
    warnings: list[str]
```

## Claude API Usage

- `anthropic` Python SDK (not raw HTTP)
- Extraction model: `claude-haiku-4-5-20251001` (cheap, fast)
- Protocol generation model: `claude-sonnet-4-20250514` (quality)
- Always `max_tokens` appropriate: 1024 extraction, 4096 protocol
- Prompts say "Return ONLY valid JSON. No markdown. No preamble."
- 3x exponential backoff retry on all API calls

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/upload | Upload PDF or image, extract markers |
| GET | /api/extraction/{id} | Get extraction results |
| PUT | /api/markers/{id} | User edits markers |
| POST | /api/analyze | Run 4-step analysis chain |
| GET | /api/protocol/{id} | Get generated protocol |
| GET | /api/protocols | List past protocols |
| GET | /health | Health check |

## Analysis Chain (4 Claude API Calls)

1. **Normalize**: Standardize names, units, deduplicate
2. **Flag**: Compare against lab + optimal ranges, clinical significance
3. **Cross-reference**: Map flagged markers to user's selected goals
4. **Generate**: Full protocol (diet, supplements, lifestyle, retest)

## Important Constraints

- NEVER store patient names beyond current session
- ALWAYS show medical disclaimer on protocol output
- Delete uploaded PDFs after extraction
- All prompts include: "Informational only. Not medical advice."
- Primary lab formats: Thyrocare, SRL, Metropolis, Dr Lal, Apollo
- Minimum font 16px on all inputs (prevents iOS auto-zoom)
- All interactive elements minimum 44px touch target

## Environment Variables (.env)
```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite+aiosqlite:///./data/health_protocol.db
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=10
CORS_ORIGINS=http://localhost:5173,capacitor://localhost
```

## Current Status
Phase 1: Project setup — NOT STARTED
