# 📄 AI-Enhanced Document Generator

> **Transform prompts and reference material into structured, editable, professionally formatted documents.**  
> Powered by **React + Tailwind CSS** on the frontend, **Python FastAPI** on the backend, **Google Gemini API** for intelligence, and **Supabase** for persistence.

[![Day 2 Status](https://img.shields.io/badge/Day%202%20Scope-AI%20Integration%20Completed-success?style=for-the-badge)](docs/SYSTEM_DESIGN_AND_IMPLEMENTATION_PLAN.md)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Tailwind%20CSS-blue?style=for-the-badge)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-Python%20FastAPI-emerald?style=for-the-badge)](backend/)
[![AI Provider](https://img.shields.io/badge/AI%20Provider-Google%20Gemini%20API-orange?style=for-the-badge)](https://ai.google.dev/)

---

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Four-Day Implementation Plan](#-four-day-implementation-plan)
- [Day 1 Scope & Delivered Components](#-day-1-scope--delivered-components)
- [Repository Structure](#-repository-structure)
- [Quick Start Guide](#-quick-start-guide)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [API Design Specification](#-api-design-specification)
- [Full System Blueprint](#-full-system-blueprint)

---

https://github.com/jananimurali0212/ai-enhanced-document-generator## 🎯 Project Overview

The **AI-Enhanced Document Generator** is an enterprise-grade web application that assists users in creating and refining documents using generative AI. A user selects a document type, enters instructions, optionally uploads reference material, and receives a structured draft that can be edited, augmented with AI actions, and exported as **PDF** or **DOCX**.

### Core Capabilities:
- **Category-Aware Blueprints:** Pre-configured structures for Project documentation, Technical reports, Business proposals, Resumes, Cover letters, and Meeting summaries.
- **Reference Grounding:** Ingestion and validation of uploaded references (`.pdf`, `.docx`, `.txt`, `.md`, `.csv`).
- **Interactive Markdown Workspace:** Live dual-mode editing (Rendered Preview & Raw Editor) with real-time word count and reading time telemetry.
- **AI Modification Actions:** Tone transformation, shortening, expansion, and automated action matrices.
- **Enterprise Persistence & Export:** Supabase Auth with Row Level Security (RLS) and standardized document export.

---

## 🏛️ System Architecture

The application is structured into decoupled frontend, backend, AI orchestration, and persistence tiers:

```
+-----------------------------------------------------------------------------------------+
|                                    USER (Browser / Desktop)                             |
|                           [Prompt Form + Optional Reference Files]                      |
+-----------------------------------------------------------------------------------------+
                                             |
                                        User Actions
                                             v
+-----------------------------------------------------------------------------------------+
|                                    FRONTEND (React)                                     |
|  - Dashboard & Templates   - Prompt Form   - File Upload   - Document Editor & History  |
+-----------------------------------------------------------------------------------------+
                                             |
                                      HTTPS / JSON API
                                             v
+-----------------------------------------------------------------------------------------+
|                                  BACKEND (FastAPI)                                      |
|  - API Endpoints   - Request Validation   - Authentication   - AI Orchestration         |
+-----------------------------------------------------------------------------------------+
        |                                    |                                    |
        v                                    v                                    v
+--------------------+              +--------------------+              +--------------------+
|     Gemini API     |              |      Supabase      |              |   Export Services  |
| - Intent & Planning|              | - Auth & Profiles  |              | - PDF generation   |
| - Drafting/Rewrite |              | - Documents Table  |              | - DOCX generation  |
| - Summarization    |              | - Storage Buckets  |              | - Download streams |
+--------------------+              +--------------------+              +--------------------+
```

---

## 🗓️ Four-Day Implementation Plan

| Phase | Milestone | Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Day 1** | **Foundation & UI Shell** | Initialize React & FastAPI projects; build clean dashboard, document-type selector, prompt form, drag-and-drop reference upload, and document editor shell with telemetry and mock fallback. | **COMPLETED** ✅ |
| **Day 2** | **AI Integration** | Configure Google Gemini API on the backend; implement prompt builder, dynamic drafting, rewriting, expanding, and summarization across all categories with full error handling. | **COMPLETED** ✅ |
| **Day 3** | **Persistence & Export** | Configure Supabase Auth and PostgreSQL database; implement document history, user profiles, PDF generation, and DOCX generation. | *Scheduled* ⏳ |
| **Day 4** | **Quality & Release** | Document scoring & comparison; end-to-end load & failure testing; responsive audit; security lockdown and deployment. | *Scheduled* ⏳ |

---

## 🤖 Day 2 Scope & Delivered AI Integration

1. **Google Gemini Client Configuration (`backend/app/core/config.py`)**
   - Secure API key isolation strictly in backend environment variables (`GEMINI_API_KEY`).
   - `.env.example` template with configurable parameters (`GEMINI_MODEL`, `TEMPERATURE`, `MAX_OUTPUT_TOKENS`, `TIMEOUT_SECONDS`).
   - Support for `gemini-2.5-flash` with graceful local mock fallback when key is not yet set.

2. **Task-Specific Prompt Builder (`backend/app/services/prompt_builder.py`)**
   - **Grounded Generation Prompts:** Synthesizes document type, purpose, target audience, tone, target length, required structural blueprints, and source references.
   - **Anti-Hallucination Constraints:** Mandates clear distinction between source facts and assumptions (flagged as `[Assumption]`), prohibits fabricated citations/statistics.
   - **Interactive Editing Prompts:** Dedicated builders for rewriting (`build_rewrite_prompt`), summarization (`build_summarize_prompt`), and technical expansion (`build_expand_prompt`).

3. **Gemini AI Service Layer (`backend/app/services/ai_service.py`)**
   - Direct integration with Google GenAI SDK (`google.genai`).
   - Response validation, title extraction, word count computation, and structured markdown parsing.
   - Implementation of `generate_document`, `rewrite_text`, `summarize_text`, and `expand_text`.

4. **FastAPI AI Routes (`backend/app/api/routes.py`)**
   - `POST /api/generate` – Full structured draft generation from prompt parameters and reference material.
   - `POST /api/edit/rewrite` – Section-level rewrite according to custom instructions and tone.
   - `POST /api/edit/summarize` – Content distillation into executive takeaways or bullet points.
   - `POST /api/edit/expand` – Section elaboration with technical depth and implementation checklists.

5. **Resilient Error Handling (`backend/app/core/exceptions.py`)**
   - User-facing error classification and retry guidance:
     - `429 Too Many Requests` (`AI_RATE_LIMIT_EXCEEDED`) – Rate limit / quota cooldown guidance.
     - `504 Gateway Timeout` (`AI_TIMEOUT`) – Request timeout guidance with length reduction suggestions.
     - `503 Service Unavailable` (`AI_CONFIGURATION_ERROR`) – Clear API key setup instructions.
     - `502 Bad Gateway` (`AI_GENERATION_FAILED`) – Malformed or empty output recovery guidance.
   - Comprehensive Pydantic input validation on all routes.

---

## 📦 Day 1 Scope & Delivered Components

1. **Dashboard & Template Selector (`frontend/src/components/Dashboard.jsx`)**
   - 6 supported enterprise document blueprints.
   - Dynamic search bar and category pill filtering.
   - One-click launch for blank custom documents.

2. **Prompt Form (`frontend/src/components/PromptForm.jsx`)**
   - Input controls for Topic, Purpose, Intended Audience.
   - Tone selector: *Professional, Technical, Persuasive, Executive, Casual, Academic*.
   - Desired Length cards: *Concise (~300–500w)*, *Standard (~800–1,200w)*, *In-depth (~1,500–2,500w)*.
   - *"Load Blueprint Defaults"* button for instant pre-population.

3. **Reference File Upload Interface (`frontend/src/components/FileUpload.jsx`)**
   - Drag-and-drop zone with file picker fallback.
   - Extension & MIME type validation (`.pdf`, `.docx`, `.txt`, `.md`, `.csv`, `.json`).
   - File chip list with human-readable file sizes and removal controls.

4. **Document Editor Shell (`frontend/src/components/DocumentEditor.jsx`)**
   - Dual view: **Rendered Markdown Preview** and **Raw Markdown Editor**.
   - Markdown formatting toolbar (`H2`, `H3`, `Bold`, `Italic`, `Quotes`, `Bullet Lists`, `Code blocks`).
   - Live telemetry bar: Word count, character count, estimated reading time.
   - Mock AI assistance tools (*Elevate Tone*, *Shorten & Summarize*, *+ Action Matrix*).
   - Export suite: Copy Markdown, Download `.md`, Download `.txt`.

5. **FastAPI Backend (`backend/app/main.py`)**
   - Health check endpoint (`/api/health`).
   - Template catalog endpoint (`/api/templates`).
   - Generation endpoint with mock fallback (`/api/generate`).
   - Multipart file upload ingestion (`/api/upload`).

---

## 📁 Repository Structure

```
ai-doc-generator/
├── docs/
│   └── SYSTEM_DESIGN_AND_IMPLEMENTATION_PLAN.md # Full 7-page blueprint & specification
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app with CORS, health check, router
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py            # API routes (/api/templates, /api/generate, /api/upload)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py           # Pydantic schemas (Tone, Length, Categories, Payloads)
│   │   └── services/
│   │       ├── __init__.py
│   │       └── mock_generator.py    # Structured document generator per category
│   ├── requirements.txt             # FastAPI, Uvicorn, Pydantic dependencies
│   ├── test_api.py                  # Unit verification suite
│   ├── run.py                       # Development server launcher
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Stepper navigation, Day 1 indicator, logo
│   │   │   ├── Dashboard.jsx        # Template selector, search, category filters
│   │   │   ├── PromptForm.jsx       # Topic, purpose, audience, tone, length inputs
│   │   │   ├── FileUpload.jsx       # Drag-and-drop reference files interface
│   │   │   ├── DocumentEditor.jsx   # Dual-mode Markdown editor, preview, telemetry
│   │   │   └── Icons.jsx            # Reusable SVG icon primitives
│   │   ├── data/
│   │   │   └── templates.js         # The 6 core document category specifications
│   │   ├── App.jsx                  # Multi-step state machine with mock & backend fallback
│   │   ├── index.css                # Tailwind CSS styling directives
│   │   └── main.jsx                 # React DOM mount point
│   ├── index.html                   # Shell with Inter & JetBrains Mono fonts
│   ├── package.json                 # React 18, Tailwind CSS, Vite
│   ├── vite.config.js               # Vite config with reverse proxy to FastAPI
│   └── tailwind.config.js           # Brand palette & typography
├── e2e_verification.py              # Automated 5-suite End-to-End test runner
├── .gitignore                       # Standardized exclusion rules
└── README.md                        # Master repository documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js:** v18+ (tested on v24.x)
- **Python:** 3.10+ (tested on 3.12.x)

### 1. Run the Backend API
```powershell
cd backend
pip install -r requirements.txt
python run.py
```
- API Server: `http://localhost:8000`
- Swagger OpenAPI Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Run the React Frontend
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

> **Note on Standalone Evaluation:**  
> The React frontend is equipped with an integrated client-side mock fallback. If the backend is offline, the UI automatically falls back to simulated generation, allowing full UX testing without dependencies.

---

## 🧪 Testing & Quality Assurance

Run the comprehensive 5-suite end-to-end verification script:
```powershell
python e2e_verification.py
```

### Verification Checklist:
- [x] Backend Health & Connectivity (`/api/health`)
- [x] Frontend Root Mounting & Asset Compilation (`http://localhost:5173`)
- [x] Vite Reverse Proxy Integrity (`/api/*` forwarding)
- [x] All 6 Document Categories Validated
- [x] Prompt Form Parameter Binding & Grounding Ingestion
- [x] Multipart Reference File Upload Parsing
- [x] Real-time Telemetry (Word Count, Characters, Reading Time)
- [x] Mock AI Transformations & Markdown Export

---

## 🔌 API Design Specification

| Method | Endpoint | Request Payload / Params | Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | None | `{ status: "healthy", service: "...", timestamp: "..." }` |
| `GET` | `/api/templates` | None | Array of 6 category templates with defaults |
| `POST` | `/api/generate` | `GenerateDocumentRequest` | `DocumentResponse` with generated content & stats |
| `POST` | `/api/upload` | `multipart/form-data` (`file`) | `UploadResponse` with file size and parse status |

---

## 📖 Full System Blueprint

For the in-depth system architecture, Supabase schema designs, RLS security policies, prompt engineering guidelines, and error handling protocols, refer to:  
👉 [**System Design & Implementation Plan**](docs/SYSTEM_DESIGN_AND_IMPLEMENTATION_PLAN.md)
