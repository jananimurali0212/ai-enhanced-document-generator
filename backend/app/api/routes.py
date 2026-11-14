from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import AIServiceException
from app.models.schemas import (
    Template,
    GenerateDocumentRequest,
    RewriteRequest,
    SummarizeRequest,
    ExpandRequest,
    DocumentResponse,
    EditResponse,
    UploadResponse
)
from app.services.mock_generator import TEMPLATES_DATA
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api", tags=["Document Generator"])

# ------------------------------------------------------------------------------
# System & Discovery Endpoints
# ------------------------------------------------------------------------------
@router.get("/health")
def health_check():
    """Returns backend and AI service health status."""
    return {
        "status": "healthy",
        "service": "AI-Enhanced Document Generator API",
        "version": settings.VERSION,
        "ai_provider": "Google Gemini API",
        "model": settings.GEMINI_MODEL,
        "is_gemini_configured": settings.is_gemini_configured,
        "is_supabase_configured": settings.is_supabase_configured,
        "mode": "live_gemini" if settings.is_gemini_configured else "mock_fallback",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/templates", response_model=List[Template])
def get_templates():
    """Retrieve supported document templates and categories."""
    return TEMPLATES_DATA

# ------------------------------------------------------------------------------
# Document Generation Endpoint
# ------------------------------------------------------------------------------
@router.post(
    "/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a structured document draft using Gemini AI"
)
def generate_document(payload: GenerateDocumentRequest):
    """
    Accepts user requirements (topic, purpose, audience, tone, length)
    and optional reference text/files to generate a comprehensive, structured draft.
    """
    try:
        return ai_service.generate_document(payload)
    except AIServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "error_type": e.error_type,
                "retry_guidance": e.retry_guidance
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Unexpected error during generation: {str(e)}",
                "error_type": "INTERNAL_SERVER_ERROR",
                "retry_guidance": "Please review your parameters and resubmit."
            }
        )

# ------------------------------------------------------------------------------
# AI Edit Endpoints: Rewrite, Summarize, Expand
# ------------------------------------------------------------------------------
@router.post(
    "/edit/rewrite",
    response_model=EditResponse,
    status_code=status.HTTP_200_OK,
    summary="Rewrite selected text or section based on user instructions"
)
def rewrite_text(payload: RewriteRequest):
    """Rewrites selected text or section according to specified instructions and tone."""
    try:
        return ai_service.rewrite_text(payload)
    except AIServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "error_type": e.error_type,
                "retry_guidance": e.retry_guidance
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Unexpected error during rewrite: {str(e)}",
                "error_type": "INTERNAL_SERVER_ERROR",
                "retry_guidance": "Please try again with a smaller text segment."
            }
        )

@router.post(
    "/edit/summarize",
    response_model=EditResponse,
    status_code=status.HTTP_200_OK,
    summary="Summarize supplied content into key takeaways"
)
def summarize_text(payload: SummarizeRequest):
    """Summarizes supplied content into bullet points, executive brief, or concise takeaways."""
    try:
        return ai_service.summarize_text(payload)
    except AIServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "error_type": e.error_type,
                "retry_guidance": e.retry_guidance
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Unexpected error during summarization: {str(e)}",
                "error_type": "INTERNAL_SERVER_ERROR",
                "retry_guidance": "Please retry with valid content."
            }
        )

@router.post(
    "/edit/expand",
    response_model=EditResponse,
    status_code=status.HTTP_200_OK,
    summary="Expand a section with relevant technical and operational detail"
)
def expand_text(payload: ExpandRequest):
    """Expands a document section with relevant detail, concrete examples, and depth."""
    try:
        return ai_service.expand_text(payload)
    except AIServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail={
                "message": e.message,
                "error_type": e.error_type,
                "retry_guidance": e.retry_guidance
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": f"Unexpected error during expansion: {str(e)}",
                "error_type": "INTERNAL_SERVER_ERROR",
                "retry_guidance": "Please try expanding a more specific paragraph."
            }
        )

# ------------------------------------------------------------------------------
# File Upload Endpoint
# ------------------------------------------------------------------------------
@router.post("/upload", response_model=UploadResponse)
async def upload_reference_file(file: UploadFile = File(...)):
    """Registers reference materials for document grounding."""
    contents = await file.read()
    return UploadResponse(
        filename=file.filename or "unknown_file",
        size_bytes=len(contents),
        content_type=file.content_type or "application/octet-stream",
        status="parsed",
        uploaded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
