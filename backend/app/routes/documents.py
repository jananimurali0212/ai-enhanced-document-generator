"""
Document Management Endpoints.
Provides user-authenticated CRUD operations for persistent documents
with Row Level Security and pagination.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.core.auth import get_current_user, AuthenticatedUser
from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentInDB,
    DocumentListResponse
)
from app.services.document_service import document_service

router = APIRouter(prefix="/api/documents", tags=["Document Persistence"])

@router.get(
    "",
    response_model=DocumentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all documents owned by the authenticated user"
)
def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document category"),
    status: Optional[str] = Query(None, description="Filter by status (draft, completed, archived)"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Retrieves all documents belonging to the authenticated user.
    Results are sorted chronologically by last updated timestamp.
    """
    clean_type = document_type if isinstance(document_type, str) else None
    clean_status = status if isinstance(status, str) else None
    clean_page = page if isinstance(page, int) else 1
    clean_limit = limit if isinstance(limit, int) else 20

    return document_service.get_user_documents(
        user_id=current_user.id,
        page=clean_page,
        limit=clean_limit,
        document_type=clean_type,
        status_filter=clean_status,
        token=current_user.token
    )

@router.post(
    "",
    response_model=DocumentInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new document for the authenticated user"
)
def create_document(
    payload: DocumentCreate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Saves a newly generated or authored document.
    Ownership is strictly derived from the verified user token.
    """
    return document_service.create_document(
        user_id=current_user.id,
        doc_data=payload,
        token=current_user.token
    )

@router.get(
    "/{id}",
    response_model=DocumentInDB,
    status_code=status.HTTP_200_OK,
    summary="Retrieve one owned document by ID"
)
def get_document(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Retrieves a single document by its UUID.
    Returns 404 if the document does not exist or belongs to another user.
    """
    return document_service.get_document_by_id(
        document_id=id,
        user_id=current_user.id,
        token=current_user.token
    )

@router.put(
    "/{id}",
    response_model=DocumentInDB,
    status_code=status.HTTP_200_OK,
    summary="Update an existing owned document"
)
def update_document(
    id: str,
    payload: DocumentUpdate,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Updates the specified document. Verifies ownership before applying changes.
    Preserves fields that are omitted in the request.
    """
    return document_service.update_document(
        document_id=id,
        user_id=current_user.id,
        update_data=payload,
        token=current_user.token
    )

@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an owned document"
)
def delete_document(
    id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Deletes an existing document. Verifies ownership before deletion.
    """
    return document_service.delete_document(
        document_id=id,
        user_id=current_user.id,
        token=current_user.token
    )
