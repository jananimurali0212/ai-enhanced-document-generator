from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from datetime import datetime
from app.models.schemas import (
    Template,
    GenerateDocumentRequest,
    DocumentResponse,
    UploadResponse
)
from app.services.mock_generator import TEMPLATES_DATA, generate_mock_document

router = APIRouter(prefix="/api", tags=["Document Generator"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Document Generator API",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/templates", response_model=List[Template])
def get_templates():
    """Retrieve supported document templates and categories."""
    return TEMPLATES_DATA

@router.post("/generate", response_model=DocumentResponse)
def generate_document(payload: GenerateDocumentRequest):
    """
    Mock endpoint generating rich markdown documents based on 
    topic, purpose, audience, tone, length, and reference files.
    """
    try:
        return generate_mock_document(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=UploadResponse)
async def upload_reference_file(file: UploadFile = File(...)):
    """Mock file upload interface that registers reference materials."""
    contents = await file.read()
    return UploadResponse(
        filename=file.filename or "unknown_file",
        size_bytes=len(contents),
        content_type=file.content_type or "application/octet-stream",
        status="parsed",
        uploaded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
