# Backend - AI-Enhanced Document Generator

FastAPI-powered backend handling Google Gemini generative AI document generation workflows, interactive editing (rewrite, summarize, expand), reference file ingestion, and template catalogs.

## Features (Day 2: AI Integration)

- **Secure Google Gemini Client (`app/services/ai_service.py`):** Configured strictly with server-side environment variables (`GEMINI_API_KEY`). API keys are never exposed to the frontend.
- **Task-Specific Prompt Builder (`app/services/prompt_builder.py`):** Constructs rich, grounded prompts adhering to document type, audience, tone, target length, category-specific blueprints, and strict anti-hallucination rules.
- **AI Endpoints (`app/api/routes.py`):**
  - `POST /api/generate` – Full structured document drafting with reference text/file grounding.
  - `POST /api/edit/rewrite` – In-place section rewriting based on custom user instructions and target tone.
  - `POST /api/edit/summarize` – Content synthesis into key takeaways, executive summaries, or bullet points.
  - `POST /api/edit/expand` – Technical elaboration with concrete sub-sections, implementation checklists, and edge-case analysis.
- **Robust Error Handling & Resilience (`app/core/exceptions.py`):**
  - Clear, user-facing error responses with actionable retry guidance for:
    - AI rate limits (`429` / `AI_RATE_LIMIT_EXCEEDED`)
    - Network / generation timeouts (`504` / `AI_TIMEOUT`)
    - Invalid or missing API credentials (`503` / `AI_CONFIGURATION_ERROR`)
    - Empty or malformed model responses (`502` / `AI_GENERATION_FAILED`)
  - Resilient local fallback engine when API keys are absent during early development or offline mode.

---

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure your Gemini API key in `.env`:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   GEMINI_TEMPERATURE=0.7
   GEMINI_MAX_OUTPUT_TOKENS=4096
   AI_REQUEST_TIMEOUT=60
   ```
   *Obtain a key from [Google AI Studio](https://aistudio.google.com/).*

---

## Quickstart

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API server:**
   ```bash
   python run.py
   # Or directly with uvicorn:
   uvicorn app.main:app --reload --port 8000
   ```

3. **Interactive Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

4. **Run Test Suites:**
   ```bash
   # Run comprehensive Day 2 test suite:
   python backend/test_day2.py

   # Run Day 1 regression suite:
   python backend/test_api.py
   ```
