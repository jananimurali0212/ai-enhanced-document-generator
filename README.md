# 📄 AI-Enhanced Document Generator

> **Transform prompts and reference material into structured, editable, professionally formatted documents.**  
> Powered by **React + Tailwind CSS** on the frontend, **Python FastAPI** on the backend, **Google Gemini API** for intelligence, **Supabase PostgreSQL** for persistence with Row Level Security (RLS), and **ReportLab & python-docx** for binary exports.

[![Day 3 Status](https://img.shields.io/badge/Day%203%20Scope-Persistence%20%26%20Export%20Completed-success?style=for-the-badge)](DAY3_IMPLEMENTATION_REPORT.md)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Tailwind%20CSS-blue?style=for-the-badge)](frontend/)
[![Backend](https://img.shields.io/badge/Backend-Python%20FastAPI-emerald?style=for-the-badge)](backend/)
[![AI Provider](https://img.shields.io/badge/AI%20Provider-Google%20Gemini%20API-orange?style=for-the-badge)](https://ai.google.dev/)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL%20(RLS)-3ECF8E?style=for-the-badge)](https://supabase.com/)

---

## 📑 Table of Contents
- [Project Overview](#-project-overview)
- [System Architecture](#-system-architecture)
- [Four-Day Implementation Plan](#-four-day-implementation-plan)
- [Day 3 Scope & Delivered Features](#-day-3-scope--delivered-features)
- [Day 2 Scope & Delivered AI Integration](#-day-2-scope--delivered-ai-integration)
- [Day 1 Scope & Delivered Components](#-day-1-scope--delivered-components)
- [Repository Structure](#-repository-structure)
- [Quick Start Guide](#-quick-start-guide)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [API Design Specification](#-api-design-specification)
- [Full System Blueprint](#-full-system-blueprint)

---

## 🎯 Project Overview

The **AI-Enhanced Document Generator** is an enterprise-grade web application that assists users in creating and refining documents using generative AI. A user selects a document type, enters instructions, optionally uploads reference material, and receives a structured draft that can be edited, augmented with AI actions, saved to the cloud, and exported as selectable **PDF** or editable **DOCX**.

### Core Capabilities:
- **Category-Aware Blueprints:** Pre-configured structures for Project documentation, Technical reports, Business proposals, Resumes, Cover letters, and Meeting summaries.
- **Reference Grounding:** Ingestion and validation of uploaded references (`.pdf`, `.docx`, `.txt`, `.md`, `.csv`).
- **Interactive Markdown Workspace:** Live dual-mode editing (Rendered Preview & Raw Editor) with real-time word count and reading time telemetry.
- **AI Modification Actions:** Tone transformation, shortening, expansion, and automated action matrices.
- **Supabase Cloud Persistence:** Automatic document saving, history browsing, and database-level Row Level Security (RLS) ensuring strict user privacy (`auth.uid() = user_id`).
- **Standardized Multi-Format Export:**
  - **PDF:** Rendered with ReportLab using vector text, dynamic `"Page X of Y"` footers, styled tables, and running headers.
  - **DOCX:** Native Microsoft Word documents styled with XML-compliant heading hierarchies, bullet lists, and zebra-striped tables.

---

## 🏛️ System Architecture

The application is structured into decoupled frontend, backend, AI orchestration, persistence, and compilation tiers:

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
                                    HTTPS / Bearer Auth
                                             v
+-----------------------------------------------------------------------------------------+
|                                  BACKEND (FastAPI)                                      |
|  - API Endpoints   - Request Validation   - JWT Auth   - AI & Export Orchestration      |
+-----------------------------------------------------------------------------------------+
        |                                    |                                    |
        v                                    v                                    v
+--------------------+              +--------------------+              +--------------------+
|     Gemini API     |              |  Supabase (Postgres)|              |   Export Engines   |
| - Grounded Drafting|              | - Row Level Security|              | - ReportLab (PDF)  |
| - Rewriting/Tone   |              | - User Isolation   |              | - python-docx(Word)|
| - Summarization    |              | - Documents Table  |              | - Temp cleanup     |
+--------------------+              +--------------------+              +--------------------+
```

---

## 🗓️ Four-Day Implementation Plan

| Phase | Milestone | Deliverables | Status |
| :--- | :--- | :--- | :---: |
| **Day 1** | **Foundation & UI Shell** | Initialize React & FastAPI projects; build clean dashboard, document-type selector, prompt form, drag-and-drop reference upload, and document editor shell with telemetry and mock fallback. | **COMPLETED** ✅ |
| **Day 2** | **AI Integration** | Configure Google Gemini API on the backend; implement prompt builder, dynamic drafting, rewriting, expanding, and summarization across all categories with full error handling. | **COMPLETED** ✅ |
| **Day 3** | **Persistence & Export** | Configure Supabase PostgreSQL with RLS; implement JWT authentication, user-scoped Document CRUD APIs, selectable ReportLab PDF export, python-docx Word export, and History Modal. | **COMPLETED** ✅ |
| **Day 4** | **Quality & Release** | Document scoring & comparison; end-to-end load & failure testing; responsive audit; security lockdown and deployment. | *Scheduled* ⏳ |

---

## 💾 Day 3 Scope & Delivered Features

1. **Supabase Database & Row Level Security (`migrations/create_documents_table.sql`)**
   - Documents table schema (`id`, `user_id`, `title`, `document_type`, `content`, `status`, `created_at`, `updated_at`).
   - Automated `updated_at` timestamp triggers and compound indexes (`idx_documents_user_updated`).
   - RLS policies enforcing `auth.uid() = user_id` for SELECT, INSERT, UPDATE, and DELETE.

2. **Authentication & Ownership Validation (`backend/app/core/auth.py`)**
   - Reusable FastAPI authentication dependencies verifying Supabase Bearer JWTs.
   - Cryptographic signature, expiration, and audience validation.
   - Derives verified `user_id` without trusting client-supplied user parameters.

3. **Document Service & Management APIs (`backend/app/routes/documents.py`)**
   - `GET /api/documents`: Paginated, filtered (type/status), sorted document listing.
   - `POST /api/documents`: Save newly generated drafts into Supabase.
   - `GET /api/documents/{id}`: Retrieve document with ownership verification (returns 404 for wrong user).
   - `PUT /api/documents/{id}`: Update document title, content, status, or metadata.
   - `DELETE /api/documents/{id}`: Permanently delete saved documents.

4. **Selectable ReportLab PDF Generation (`backend/app/services/export_service.py`)**
   - Vector PDF rendering with `SimpleDocTemplate` and Flowable objects.
   - Custom two-pass `NumberedCanvas` computing dynamic `"Page X of Y"` footers.
   - Styled Markdown tables, blockquotes, and running header rules.

5. **Microsoft Word DOCX Generation (`backend/app/services/export_service.py`)**
   - Native Office Open XML generation using `python-docx`.
   - Word Heading styles (H1-H3), bullet/numbered lists, and formatted code spans.
   - XML 1.0 control character sanitization preventing corruption warnings.

6. **Secure Binary Export Endpoints (`backend/app/routes/export.py`)**
   - `POST /api/export/pdf`: Stream binary PDF with `Content-Disposition`.
   - `POST /api/export/docx`: Stream binary Word document with MIME headers.
   - Path traversal prevention via `sanitize_filename()`.
   - Guaranteed zero-leak temporary file deletion via FastAPI `BackgroundTasks`.

7. **Frontend Cloud Integration (`frontend/src/components/DocumentHistoryModal.jsx`)**
   - Interactive History modal with search, type filters, and delete actions.
   - One-click "Save to Cloud" / "Update in Cloud" in the editor.
   - Direct PDF and DOCX download action triggers.

---

## 🤖 Day 2 Scope & Delivered AI Integration

1. **Google Gemini Client Configuration (`backend/app/core/config.py`)**
   - Secure API key isolation strictly in backend environment variables (`GEMINI_API_KEY`).
   - Model support for `gemini-2.5-flash` with graceful local mock fallback.

2. **Task-Specific Prompt Builder (`backend/app/services/prompt_builder.py`)**
   - Synthesizes document type, purpose, target audience, tone, length, and source references.
   - Anti-hallucination constraints flagging unverified claims as `[Assumption]`.

3. **FastAPI AI Routes (`backend/app/api/routes.py`)**
   - `POST /api/generate`: Structured draft generation.
   - `POST /api/edit/rewrite`: Tone and style transformations.
   - `POST /api/edit/summarize`: Executive summaries and bullet distillations.
   - `POST /api/edit/expand`: Deep technical expansion and checklists.

---

## 📦 Day 1 Scope & Delivered Components

1. **Dashboard & Template Selector (`frontend/src/components/Dashboard.jsx`)**
2. **Prompt Form (`frontend/src/components/PromptForm.jsx`)**
3. **Reference File Upload Interface (`frontend/src/components/FileUpload.jsx`)**
4. **Document Editor Shell (`frontend/src/components/DocumentEditor.jsx`)**

---

## 📁 Repository Structure

```
ai-doc-generator/
├── migrations/
│   └── create_documents_table.sql       # Supabase schema migration with RLS
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI app with CORS and registered routers
│   │   ├── api/
│   │   │   └── routes.py                # Health check, templates, AI generate/edit routes
│   │   ├── core/
│   │   │   ├── auth.py                  # JWT Bearer token authentication dependency
│   │   │   ├── config.py                # Settings with Supabase and Gemini configs
│   │   │   └── exceptions.py            # AI and authentication error handlers
│   │   ├── routes/
│   │   │   ├── documents.py             # Document CRUD endpoints (/api/documents)
│   │   │   └── export.py                # Binary export endpoints (/api/export/pdf, /docx)
│   │   ├── schemas/
│   │   │   ├── document.py              # Document request/response Pydantic models
│   │   │   └── export.py                # Export request Pydantic models
│   │   ├── services/
│   │   │   ├── ai_service.py            # Gemini GenAI communication service
│   │   │   ├── prompt_builder.py        # Task-specific prompt compiler
│   │   │   ├── supabase_service.py      # Supabase client factory
│   │   │   ├── document_service.py      # User-scoped Document CRUD service
│   │   │   └── export_service.py        # ReportLab PDF & python-docx Word compiler
│   │   └── utils/
│   │       └── file_utils.py            # Path sanitization and temp cleanup
│   ├── tests/
│   │   ├── test_auth.py                 # Authentication unit tests
│   │   ├── test_documents.py            # Document CRUD & RLS isolation tests
│   │   └── test_exports.py              # Export format & magic bytes tests
│   ├── test_day3.py                     # Master Day 3 verification test suite
│   ├── test_day2.py                     # Master Day 2 verification test suite
│   ├── test_api.py                      # Master Day 1 verification test suite
│   ├── requirements.txt                 # Backend dependencies
│   └── .env.example                     # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx               # Stepper navigation, Day 3 indicator, History button
│   │   │   ├── Dashboard.jsx            # Template selector, search, category filters
│   │   │   ├── PromptForm.jsx           # Topic, purpose, audience, tone, length inputs
│   │   │   ├── FileUpload.jsx           # Drag-and-drop reference files interface
│   │   │   ├── DocumentEditor.jsx       # Markdown editor, preview, Save & Export triggers
│   │   │   ├── DocumentHistoryModal.jsx # Saved document browser & management modal
│   │   │   └── Icons.jsx                # Reusable SVG icon primitives
│   │   ├── services/
│   │   │   └── api.js                   # Client API calls for documents and exports
│   │   ├── App.jsx                      # Multi-step state machine with modal management
│   │   └── main.jsx                     # React mount point
│   ├── package.json
│   └── vite.config.js
├── samples/
│   ├── sample_export.pdf                # Generated ReportLab vector PDF sample
│   └── sample_export.docx               # Generated python-docx Word sample
├── DAY3_IMPLEMENTATION_REPORT.md        # Comprehensive Day 3 delivery report
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js:** v18+ (tested on v24.x)
- **Python:** 3.10+ (tested on 3.12.x)

### 1. Backend Setup & Run
```powershell
cd backend
pip install -r requirements.txt
python run.py
```
- API Server: `http://localhost:8000`
- Swagger OpenAPI Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### 2. Frontend Setup & Run
```powershell
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🧪 Testing & Quality Assurance

Run the comprehensive test suites:

```powershell
# 1. Day 3 Persistence & Export Master Suite (All 6 modules)
python backend/test_day3.py

# 2. Day 2 AI Integration Master Suite
python backend/test_day2.py

# 3. Day 1 API & Template Master Suite
python backend/test_api.py

# 4. Frontend Production Build Check
npm --prefix frontend run build
```

---

## 📖 Documentation
- [Day 3 Implementation Report](DAY3_IMPLEMENTATION_REPORT.md)
- [System Design & Implementation Plan](docs/SYSTEM_DESIGN_AND_IMPLEMENTATION_PLAN.md)
