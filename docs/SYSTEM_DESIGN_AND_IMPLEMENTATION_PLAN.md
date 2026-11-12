# AI-ENHANCED DOCUMENT GENERATOR
**Project Documentation • System Design • Architecture • Implementation Plan**

| Parameter | Specification |
| :--- | :--- |
| **Project type** | AI-powered web application |
| **AI provider** | Google Gemini API |
| **Frontend** | React + Tailwind CSS |
| **Backend** | Python FastAPI |
| **Data platform** | Supabase (Auth, database, storage) |
| **Document output** | PDF and DOCX |

**Purpose:** Transform a user's prompt and optional reference material into a structured, editable, professionally formatted document. The system also supports rewriting, summarization, document history, and export.

*Prepared as an implementation blueprint. Specific endpoints, database fields, and deployment settings can be refined during development.*

---

## 1. Project Overview

The AI-Enhanced Document Generator is a web application that assists users in creating and refining documents using generative AI. A user selects a document type, enters instructions, optionally uploads reference material, and receives a structured draft that can be edited and exported.

### 1.1 Objectives
- **Reduce turnaround time:** Drastically reduce the time required to create structured enterprise documents.
- **Tone & Type Adherence:** Generate content that strictly follows a selected document category and tone.
- **Reference Grounding:** Use uploaded reference material as context where appropriate.
- **Interactive Editing:** Provide editing tools for rewriting, expanding, and summarizing content.
- **Standardized Export:** Export documents in commonly used formats such as PDF and DOCX.
- **Secure Persistence:** Save user documents securely for later access and version control.

### 1.2 Target Users
Students, professionals, job seekers, small businesses, engineering teams, and enterprise users who regularly prepare reports, proposals, resumes, letters, and meeting summaries.

### 1.3 Supported Document Categories
- Project documentation
- Technical reports
- Research reports
- Business proposals
- Resumes
- Cover letters
- Meeting summaries
- Academic assignments

---

## 2. Functional Requirements

| ID | Feature | Expected Behaviour |
| :--- | :--- | :--- |
| **FR-01** | **Prompt-based generation** | Accept topic, purpose, audience, length, and tone; generate a structured draft. |
| **FR-02** | **Document templates** | Offer document-specific structures and section guidance. |
| **FR-03** | **Reference upload** | Accept supported files, validate them, and extract usable text. |
| **FR-04** | **AI editing** | Rewrite, expand, shorten, change tone, and summarize selected content. |
| **FR-05** | **Rich document editing** | Allow users to review and modify generated text before export. |
| **FR-06** | **Export** | Create downloadable PDF and DOCX files. |
| **FR-07** | **Document history** | Save, reopen, rename, and delete a user's documents. |
| **FR-08** | **Authentication** | Restrict saved documents to their owner. |

---

## 3. Non-Functional Requirements

- **Security:** Protect API keys on the server; enforce authentication and per-user document access.
- **Reliability:** Validate inputs and handle AI, database, and export failures gracefully.
- **Usability:** Provide a clear workflow, loading indicators, and editable output.
- **Maintainability:** Separate UI, API routes, AI services, file processing, and persistence.
- **Performance:** Use sensible upload limits, request timeouts, and loading feedback; avoid promising a fixed response time until measured.
- **Privacy:** Explain how uploaded files and generated content are processed and stored.

---

## 4. High-Level Architecture

The system uses a React client, a FastAPI backend, Gemini for AI generation, Supabase for authentication and persistence, and dedicated export services for PDF and DOCX creation. The backend acts as the trusted boundary: it validates requests, protects secrets, coordinates AI calls, and controls database access.

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

### 4.1 Main Components
- **React frontend:** Dashboard, template picker, prompt form, file upload, document editor, history, and export controls.
- **FastAPI backend:** Request validation, authentication checks, orchestration, and API responses.
- **Gemini API:** Intent interpretation, document planning, drafting, rewriting, and summarization.
- **Supabase:** Authentication, document metadata, and optional file storage.
- **Export services:** Convert approved document content into PDF or DOCX.

---

## 5. Low-Level Architecture

```
+---------------------+           +---------------------+           +---------------------+
|      React UI       | --REST--> |   FastAPI Routes    | --Calls-> |    Service Layer    |
| - Prompt / Upload   |           | /generate  /rewrite |           | - Request validation|
| - TemplateSelector  |           | /summarize /export  |           | - Prompt builder    |
| - Editor / History  |           | /documents          |           | - AI Client / Export|
+---------------------+           +---------------------+           +---------------------+
                                             |                                 |
                                             v                                 v
                                  +---------------------+           +---------------------+
                                  |   File Processing   |           |     Data Layer      |
                                  | - Type & size check |           | - Supabase Auth     |
                                  | - Text extraction   |           | - Documents table   |
                                  | - Safe AI payload   |           | - Row Level Security|
                                  +---------------------+           +---------------------+
```

### 5.1 Suggested Backend Modules
- `app/main.py` – Create FastAPI application and register routers.
- `app/routes/generate.py` – Generation endpoint.
- `app/routes/documents.py` – Create, list, retrieve, update, and delete documents.
- `app/routes/edit.py` – Rewrite, expand, shorten, and summarize actions.
- `app/routes/export.py` – PDF and DOCX export endpoints.
- `app/services/ai_service.py` – Gemini client and response handling.
- `app/services/prompt_builder.py` – Document-type and task-specific prompt construction.
- `app/services/file_service.py` – File validation and text extraction.
- `app/services/export_service.py` – PDF/DOCX rendering.
- `app/services/document_service.py` – Persistence and ownership checks.

### 5.2 Suggested Frontend Components
- `DashboardPage`
- `DocumentTypeSelector`
- `PromptForm`
- `ReferenceFileUpload`
- `GenerationSettings`
- `DocumentEditor`
- `AIActionToolbar`
- `DocumentHistory`
- `ExportMenu`
- `AuthPages`

---

## 6. Core Processing Workflows

### 6.1 Generate a New Document
1. User authenticates and selects a document type.
2. User enters topic, purpose, audience, tone, and desired length.
3. Optional reference files are uploaded and validated.
4. Backend extracts relevant text and constructs a structured prompt.
5. Gemini generates the draft.
6. Backend validates and normalizes the response.
7. Frontend displays the editable document.
8. On save, the backend stores the document under the authenticated user.

### 6.2 Edit or Summarize Content
The frontend sends the selected text, requested operation, and relevant context. The backend checks ownership where a saved document is involved, builds a focused prompt, calls Gemini, and returns the revised text. The user reviews and accepts or rejects the suggestion.

### 6.3 Export
The frontend requests an export format. The backend validates document ownership and content, applies a template, generates a PDF or DOCX file, and returns it as a downloadable response. Exported files use safe filenames and temporary-file cleanup.

---

## 7. Proposed API Design

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/api/generate` | Generate a document from user requirements. |
| `POST` | `/api/edit/rewrite` | Rewrite selected text or a section. |
| `POST` | `/api/edit/summarize` | Summarize supplied content. |
| `POST` | `/api/edit/expand` | Expand a section with relevant detail. |
| `GET` | `/api/documents` | List the authenticated user's documents. |
| `POST` | `/api/documents` | Save a new document. |
| `GET` | `/api/documents/{id}` | Retrieve one owned document. |
| `PUT` | `/api/documents/{id}` | Update an owned document. |
| `DELETE`| `/api/documents/{id}` | Delete an owned document. |
| `POST` | `/api/export/pdf` | Generate and return a PDF. |
| `POST` | `/api/export/docx` | Generate and return a DOCX. |

---

## 8. Proposed Data Model

### `documents` table:
- `id` – UUID primary key
- `user_id` – authenticated owner ID (foreign key to `auth.users.id`)
- `title` – document title
- `document_type` – selected template / category
- `content` – editable document content (JSON or structured markdown text)
- `created_at` – creation timestamp
- `updated_at` – last modification timestamp
- `status` – draft or completed

### Optional `document_files` table or Storage metadata:
- `id`, `document_id`, `user_id`, `storage_path`, `original_filename`, `mime_type`, `uploaded_at`.

> **Row Level Security (RLS):** Apply RLS so a user can only read or modify rows where `user_id` matches their authenticated identity (`auth.uid()`). Never trust a `user_id` supplied only by the browser; derive identity from a verified session/token.

---

## 9. AI Prompt and Output Strategy

- Use a shared prompt-building layer with document-specific instructions.
- Include the document type, objective, intended audience, tone, target length, required sections, source text, and explicit constraints.
- Instruct the model to distinguish source facts from assumptions and avoid inventing citations, statistics, or credentials.
- **Recommended output structure:** Title, executive summary or introduction, ordered sections, conclusion, and references only when genuine sources are supplied or verified.
- Prefer structured JSON from the model for predictable rendering; validate the schema before displaying or exporting.

---

## 10. Security, Privacy, and Error Handling

- **Key Isolation:** Store the Gemini API key in backend environment variables (`.env`); never expose it in frontend client code.
- **Input Sanitization:** Validate upload size, extension, and MIME type; reject unsupported or potentially unsafe files.
- **Prompt Injection Defense:** Treat uploaded content as untrusted input and do not follow instructions embedded in files that conflict with system rules.
- **Strict Authorization:** Enforce authentication and ownership checks on every saved-document operation.
- **Storage Policies:** Configure Supabase RLS and private storage policies.
- **User-Facing Telemetry:** Handle rate limits, network timeouts, malformed AI output, and export failures with clear user-facing messages.
- **Privacy:** Avoid logging sensitive document contents or API keys.

---

## 11. Four-Day Implementation Plan

- **Day 1 – Foundation (Completed):** Initialize React and FastAPI projects; build dashboard, document-type selection, prompt form, upload interface, and editor shell. Use mock content until the UI flow is stable.
- **Day 2 – AI Integration:** Configure Gemini on the backend; implement prompt construction, generation, rewrite, expand, and summarize; test multiple document categories and failure cases.
- **Day 3 – Persistence and Export:** Configure Supabase Auth and database; implement save/history; generate PDF and DOCX; verify formatting and ownership controls.
- **Day 4 – Quality and Release:** Add document scoring and comparison where feasible; test uploads, long content, API errors, authentication, and exports; fix defects and deploy.

---

## 12. Testing Plan

| Test | Input / Condition | Expected Result |
| :--- | :--- | :--- |
| **Generation** | Valid prompt and selected template | Structured document is returned. |
| **Empty prompt** | No topic or instructions | Validation message; no AI request. |
| **Reference upload**| Supported file within size limit | Text is extracted and used as context. |
| **Unsupported upload** | Unsupported file type | File is rejected with a clear message. |
| **Rewrite** | Select a paragraph and request formal tone | Revised paragraph is returned. |
| **PDF export** | Save or export a completed draft | Readable PDF downloads. |
| **DOCX export** | Export a document with headings and lists | Editable DOCX preserves structure. |
| **Access control** | User requests another user's document | Request is denied. |
| **AI failure** | Timeout or rate limit | Graceful error and retry guidance. |

---

## 13. Future Enhancements

- OCR and extraction for scanned documents.
- Citation assistance with source verification and user review.
- Multilingual generation and translation.
- Team workspaces, sharing, and collaboration.
- Custom branding, headers, footers, and template builder.
- Version comparison and restore.
- Quality rubric configurable by document category.

---

## 14. Expected Outcome

The completed application will provide an end-to-end workflow for creating, editing, saving, and exporting AI-assisted documents. Its modular architecture supports future expansion while keeping AI orchestration, file processing, persistence, and document rendering independently testable.

