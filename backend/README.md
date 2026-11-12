# Backend - AI-Enhanced Document Generator

FastAPI-powered backend handling document generation workflows, reference file ingestion, and template catalogs.

## Quickstart

1. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server:**
   ```bash
   python run.py
   # Or directly with uvicorn:
   uvicorn app.main:app --reload --port 8000
   ```

4. **Interactive Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
