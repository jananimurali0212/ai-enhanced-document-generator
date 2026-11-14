"""
Document Persistence & Management Service.
Handles document CRUD operations, user-scoped querying, ownership verification,
and resilient database interaction with Supabase RLS.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, status

from app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentInDB,
    DocumentListResponse
)
from app.services.supabase_service import supabase_service

logger = logging.getLogger(__name__)

# In-memory local fallback store used when Supabase is not configured or in offline tests.
# Keys are document UUIDs, values are dicts matching table schema.
_LOCAL_DOCUMENTS_STORE: Dict[str, Dict[str, Any]] = {}

def _validate_uuid(val: str, field_name: str = "document_id") -> str:
    """Validates that a string is a valid UUID."""
    try:
        val_str = str(val).strip()
        return str(uuid.UUID(val_str))
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Must be a valid UUID."
        )

def _normalize_content(content: Any) -> Any:
    """Normalizes document content for JSONB storage without losing structure."""
    if isinstance(content, dict) or isinstance(content, list):
        return content
    # Text or Markdown string
    return {"markdown": str(content)}

class DocumentService:

    def create_document(
        self,
        user_id: str,
        doc_data: DocumentCreate,
        token: str = ""
    ) -> DocumentInDB:
        """
        Creates a new document scoped strictly to the authenticated user_id.
        """
        valid_user_id = _validate_uuid(user_id, "user_id")
        now_iso = datetime.now(timezone.utc).isoformat()
        doc_id = str(uuid.uuid4())
        normalized_content = _normalize_content(doc_data.content)

        # 1. Supabase postgrest insert with user client
        if supabase_service.is_available and token:
            user_client = supabase_service.get_user_client(token)
            if user_client:
                try:
                    payload = {
                        "id": doc_id,
                        "user_id": valid_user_id,
                        "title": doc_data.title.strip(),
                        "document_type": doc_data.document_type.strip(),
                        "content": normalized_content,
                        "status": doc_data.status or "draft",
                        "created_at": now_iso,
                        "updated_at": now_iso
                    }
                    res = user_client.table("documents").insert(payload).execute()
                    if res.data and len(res.data) > 0:
                        row = res.data[0]
                        return DocumentInDB(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row["title"],
                            document_type=row["document_type"],
                            content=row["content"],
                            created_at=str(row["created_at"]),
                            updated_at=str(row["updated_at"]),
                            status=row.get("status", "draft")
                        )
                except Exception as e:
                    logger.error(f"Supabase document insert failed: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to persist document to database: {str(e)}"
                    )

        # 2. Local fallback storage (when Supabase credentials are not provided)
        record = {
            "id": doc_id,
            "user_id": valid_user_id,
            "title": doc_data.title.strip(),
            "document_type": doc_data.document_type.strip(),
            "content": normalized_content,
            "status": doc_data.status or "draft",
            "created_at": now_iso,
            "updated_at": now_iso
        }
        _LOCAL_DOCUMENTS_STORE[doc_id] = record

        return DocumentInDB(
            id=record["id"],
            user_id=record["user_id"],
            title=record["title"],
            document_type=record["document_type"],
            content=record["content"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
            status=record["status"]
        )

    def get_user_documents(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        document_type: Optional[str] = None,
        status_filter: Optional[str] = None,
        token: str = ""
    ) -> DocumentListResponse:
        """
        Retrieves all documents owned by user_id, sorted by updated_at descending.
        """
        valid_user_id = _validate_uuid(user_id, "user_id")
        page = max(1, page)
        limit = max(1, min(100, limit))
        offset = (page - 1) * limit

        # 1. Supabase user-scoped query
        if supabase_service.is_available and token:
            user_client = supabase_service.get_user_client(token)
            if user_client:
                try:
                    query = user_client.table("documents").select("*", count="exact")
                    query = query.eq("user_id", valid_user_id)
                    if document_type:
                        query = query.eq("document_type", document_type)
                    if status_filter:
                        query = query.eq("status", status_filter)
                    query = query.order("updated_at", desc=True)
                    query = query.range(offset, offset + limit - 1)
                    res = query.execute()

                    docs = [
                        DocumentInDB(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row["title"],
                            document_type=row["document_type"],
                            content=row["content"],
                            created_at=str(row["created_at"]),
                            updated_at=str(row["updated_at"]),
                            status=row.get("status", "draft")
                        )
                        for row in (res.data or [])
                    ]
                    total = res.count if res.count is not None else len(docs)
                    return DocumentListResponse(documents=docs, total=total, page=page, limit=limit)
                except Exception as e:
                    logger.error(f"Supabase get_user_documents error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database query error: {str(e)}"
                    )

        # 2. Local fallback storage query
        user_docs = [
            d for d in _LOCAL_DOCUMENTS_STORE.values()
            if d["user_id"] == valid_user_id
        ]
        if document_type and isinstance(document_type, str):
            user_docs = [d for d in user_docs if d["document_type"].lower() == document_type.lower()]
        if status_filter and isinstance(status_filter, str):
            user_docs = [d for d in user_docs if d["status"].lower() == status_filter.lower()]

        # Sort updated_at desc
        user_docs.sort(key=lambda x: x["updated_at"], reverse=True)
        total = len(user_docs)
        paged = user_docs[offset: offset + limit]

        docs = [
            DocumentInDB(
                id=d["id"],
                user_id=d["user_id"],
                title=d["title"],
                document_type=d["document_type"],
                content=d["content"],
                created_at=d["created_at"],
                updated_at=d["updated_at"],
                status=d["status"]
            )
            for d in paged
        ]
        return DocumentListResponse(documents=docs, total=total, page=page, limit=limit)

    def get_document_by_id(
        self,
        document_id: str,
        user_id: str,
        token: str = ""
    ) -> DocumentInDB:
        """
        Retrieves a document by ID. Enforces ownership check; returns 404 if not found or not owned.
        """
        valid_doc_id = _validate_uuid(document_id, "document_id")
        valid_user_id = _validate_uuid(user_id, "user_id")

        # 1. Supabase query
        if supabase_service.is_available and token:
            user_client = supabase_service.get_user_client(token)
            if user_client:
                try:
                    res = user_client.table("documents").select("*").eq("id", valid_doc_id).eq("user_id", valid_user_id).execute()
                    if res.data and len(res.data) > 0:
                        row = res.data[0]
                        return DocumentInDB(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row["title"],
                            document_type=row["document_type"],
                            content=row["content"],
                            created_at=str(row["created_at"]),
                            updated_at=str(row["updated_at"]),
                            status=row.get("status", "draft")
                        )
                    # Return 404 without revealing if document exists under another user
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Document not found."
                    )
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(f"Supabase get_document_by_id error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database query error: {str(e)}"
                    )

        # 2. Local fallback check
        doc = _LOCAL_DOCUMENTS_STORE.get(valid_doc_id)
        if not doc or doc["user_id"] != valid_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found."
            )

        return DocumentInDB(
            id=doc["id"],
            user_id=doc["user_id"],
            title=doc["title"],
            document_type=doc["document_type"],
            content=doc["content"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            status=doc["status"]
        )

    def update_document(
        self,
        document_id: str,
        user_id: str,
        update_data: DocumentUpdate,
        token: str = ""
    ) -> DocumentInDB:
        """
        Updates an existing document owned by user_id. Preserves unmodified fields.
        """
        # Verify ownership first
        self.verify_document_ownership(document_id, user_id, token)

        valid_doc_id = _validate_uuid(document_id, "document_id")
        valid_user_id = _validate_uuid(user_id, "user_id")
        now_iso = datetime.now(timezone.utc).isoformat()

        # Build update fields
        updates: Dict[str, Any] = {"updated_at": now_iso}
        if update_data.title is not None:
            updates["title"] = update_data.title.strip()
        if update_data.document_type is not None:
            updates["document_type"] = update_data.document_type.strip()
        if update_data.content is not None:
            updates["content"] = _normalize_content(update_data.content)
        if update_data.status is not None:
            updates["status"] = update_data.status

        # 1. Supabase update
        if supabase_service.is_available and token:
            user_client = supabase_service.get_user_client(token)
            if user_client:
                try:
                    res = user_client.table("documents").update(updates).eq("id", valid_doc_id).eq("user_id", valid_user_id).execute()
                    if res.data and len(res.data) > 0:
                        row = res.data[0]
                        return DocumentInDB(
                            id=row["id"],
                            user_id=row["user_id"],
                            title=row["title"],
                            document_type=row["document_type"],
                            content=row["content"],
                            created_at=str(row["created_at"]),
                            updated_at=str(row["updated_at"]),
                            status=row.get("status", "draft")
                        )
                except Exception as e:
                    logger.error(f"Supabase update error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database update error: {str(e)}"
                    )

        # 2. Local fallback update
        doc = _LOCAL_DOCUMENTS_STORE.get(valid_doc_id)
        if not doc or doc["user_id"] != valid_user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

        doc.update(updates)
        return DocumentInDB(
            id=doc["id"],
            user_id=doc["user_id"],
            title=doc["title"],
            document_type=doc["document_type"],
            content=doc["content"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            status=doc["status"]
        )

    def delete_document(
        self,
        document_id: str,
        user_id: str,
        token: str = ""
    ) -> dict:
        """
        Deletes a document owned by user_id. Returns success confirmation.
        """
        # Verify ownership first
        self.verify_document_ownership(document_id, user_id, token)

        valid_doc_id = _validate_uuid(document_id, "document_id")
        valid_user_id = _validate_uuid(user_id, "user_id")

        # 1. Supabase delete
        if supabase_service.is_available and token:
            user_client = supabase_service.get_user_client(token)
            if user_client:
                try:
                    res = user_client.table("documents").delete().eq("id", valid_doc_id).eq("user_id", valid_user_id).execute()
                    return {"message": "Document successfully deleted.", "id": valid_doc_id, "success": True}
                except Exception as e:
                    logger.error(f"Supabase delete error: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Database delete error: {str(e)}"
                    )

        # 2. Local fallback delete
        if valid_doc_id in _LOCAL_DOCUMENTS_STORE:
            del _LOCAL_DOCUMENTS_STORE[valid_doc_id]

        return {"message": "Document successfully deleted.", "id": valid_doc_id, "success": True}

    def verify_document_ownership(
        self,
        document_id: str,
        user_id: str,
        token: str = ""
    ) -> bool:
        """
        Verifies that document_id exists and is strictly owned by user_id.
        Raises 404 if document does not exist or belongs to another user.
        """
        self.get_document_by_id(document_id, user_id, token)
        return True

# Global singleton service
document_service = DocumentService()
