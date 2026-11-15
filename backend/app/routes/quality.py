"""
FastAPI Routes for Day 4 Quality Assessment, Completeness Analysis,
Intelligent Improvement, and Document Comparison.
"""

import logging
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, AuthenticatedUser
from app.services.document_service import document_service
from app.services.quality_service import quality_service
from app.services.completeness_service import completeness_service
from app.services.comparison_service import comparison_service
from app.services.ai_service import ai_service
from app.schemas.quality import (
    QualityAnalyzeRequest,
    QualityAnalyzeResponse,
    CompletenessRequest,
    CompletenessResponse,
    ImproveRequest,
    ImproveResponse,
    CompareRequest,
    CompareResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Document Quality & Analytics"])

def _extract_text_content(content: Any) -> str:
    """Extracts raw markdown or text string from varied content shapes."""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        if "markdown" in content:
            return str(content["markdown"])
        if "text" in content:
            return str(content["text"])
        if "content" in content:
            return _extract_text_content(content["content"])
    return str(content)

def _resolve_document_content(
    document_id: Optional[str],
    raw_content: Optional[str],
    user_id: str,
    default_doc_type: str = "General Document"
) -> tuple[str, str, str]:
    """Helper to resolve content and metadata from saved document or raw payload."""
    if document_id:
        doc = document_service.get_document_by_id(document_id, user_id)
        content_text = _extract_text_content(doc.content)
        return content_text, doc.document_type, doc.title
    elif raw_content and raw_content.strip():
        return raw_content.strip(), default_doc_type, "Draft Document"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'document_id' of a saved document or 'content' must be provided."
        )

# ----------------------------------------------------------------------
# 1. Quality Analysis Endpoint
# ----------------------------------------------------------------------
@router.post("/quality/analyze", response_model=QualityAnalyzeResponse)
def analyze_quality(
    req: QualityAnalyzeRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Evaluates document quality across grammar, clarity, relevance,
    professionalism, structure, and completeness.
    """
    content, doc_type, _ = _resolve_document_content(
        req.document_id,
        req.content,
        current_user.id,
        req.document_type or "General Document"
    )

    try:
        result = quality_service.analyze_quality(
            content=content,
            document_type=doc_type,
            context=req.context
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Quality analysis error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Quality evaluation error: {str(e)}")

# ----------------------------------------------------------------------
# 2. Completeness Analysis Endpoint
# ----------------------------------------------------------------------
@router.post("/quality/completeness", response_model=CompletenessResponse)
def analyze_completeness(
    req: CompletenessRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Compares document structure against expected blueprints for its type.
    Identifies completed, incomplete, and missing sections with percentage score.
    """
    content, doc_type, _ = _resolve_document_content(
        req.document_id,
        req.content,
        current_user.id,
        req.document_type or "General Document"
    )

    try:
        result = completeness_service.analyze_completeness(
            content=content,
            document_type=doc_type
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Completeness analysis error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Completeness evaluation error: {str(e)}")

# ----------------------------------------------------------------------
# 3. Intelligent Document Improvement Endpoint
# ----------------------------------------------------------------------
@router.post("/quality/improve", response_model=ImproveResponse)
def improve_document(
    req: ImproveRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Applies targeted editorial improvements to document content.
    Returns revised text separately without automatically overwriting the original.
    """
    content, _, _ = _resolve_document_content(
        req.document_id,
        req.content,
        current_user.id
    )

    try:
        result = ai_service.improve_content(
            content=content,
            operation=req.operation,
            instruction=req.instruction,
            context=req.context
        )
        return result
    except Exception as e:
        logger.error(f"Improvement error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Improvement error: {str(e)}")

# ----------------------------------------------------------------------
# 4. Document Comparison Endpoint
# ----------------------------------------------------------------------
@router.post("/documents/compare", response_model=CompareResponse)
def compare_documents(
    req: CompareRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Compares two document versions using an algorithmic diff engine,
    calculates exact similarity percentage, and provides an AI summary of changes.
    """
    # Resolve original
    if req.document_id_1:
        doc1 = document_service.get_document_by_id(req.document_id_1, current_user.id)
        orig_text = _extract_text_content(doc1.content)
    elif req.original_text is not None:
        orig_text = req.original_text
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'document_id_1' or 'original_text' must be provided."
        )

    # Resolve revised
    if req.document_id_2:
        doc2 = document_service.get_document_by_id(req.document_id_2, current_user.id)
        rev_text = _extract_text_content(doc2.content)
    elif req.revised_text is not None:
        rev_text = req.revised_text
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either 'document_id_2' or 'revised_text' must be provided."
        )

    try:
        result = comparison_service.compare_documents(
            original=orig_text,
            revised=rev_text,
            title=req.title or "Document Comparison"
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"Comparison error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Comparison error: {str(e)}")
