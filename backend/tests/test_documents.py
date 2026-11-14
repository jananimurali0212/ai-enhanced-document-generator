"""
Unit & Integration Tests for Document CRUD & Ownership Isolation (Modules 1, 3, 4).
Verifies:
- Document creation
- User-scoped retrieval & filtering
- Document updating
- Document deletion
- Cross-user ownership enforcement (User A vs User B)
"""

import sys
import uuid
from pathlib import Path
import pytest
from fastapi import HTTPException

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.document_service import document_service

USER_A_ID = str(uuid.uuid4())
USER_B_ID = str(uuid.uuid4())

def test_document_creation():
    doc_create = DocumentCreate(
        title="Microservices Event Sourcing Architecture",
        document_type="Project documentation",
        content="# Architecture\n\nDetailed system specifications.",
        status="draft"
    )
    doc = document_service.create_document(user_id=USER_A_ID, doc_data=doc_create)
    assert doc.id is not None
    assert doc.user_id == USER_A_ID
    assert doc.title == "Microservices Event Sourcing Architecture"
    assert doc.document_type == "Project documentation"
    assert doc.status == "draft"
    assert doc.created_at is not None
    assert doc.updated_at is not None

def test_document_retrieval_and_filtering():
    # Create 2 documents for User A with different types
    doc1 = document_service.create_document(
        user_id=USER_A_ID,
        doc_data=DocumentCreate(
            title="Q4 Infrastructure Benchmark",
            document_type="Technical reports",
            content="Benchmark results.",
            status="completed"
        )
    )
    doc2 = document_service.create_document(
        user_id=USER_A_ID,
        doc_data=DocumentCreate(
            title="Executive Strategy Brief",
            document_type="Business proposals",
            content="Proposal details.",
            status="draft"
        )
    )

    # List all for User A
    list_all = document_service.get_user_documents(user_id=USER_A_ID)
    assert list_all.total >= 2
    assert any(d.id == doc1.id for d in list_all.documents)
    assert any(d.id == doc2.id for d in list_all.documents)

    # Filter by document_type
    filtered = document_service.get_user_documents(user_id=USER_A_ID, document_type="Technical reports")
    assert all(d.document_type == "Technical reports" for d in filtered.documents)

    # Filter by status
    filtered_status = document_service.get_user_documents(user_id=USER_A_ID, status_filter="completed")
    assert all(d.status == "completed" for d in filtered_status.documents)

def test_document_update():
    doc = document_service.create_document(
        user_id=USER_A_ID,
        doc_data=DocumentCreate(
            title="Original Draft Title",
            document_type="Project documentation",
            content="Original content.",
            status="draft"
        )
    )

    update_payload = DocumentUpdate(
        title="Revised Approved Title",
        status="completed"
    )
    updated = document_service.update_document(
        document_id=doc.id,
        user_id=USER_A_ID,
        update_data=update_payload
    )

    assert updated.id == doc.id
    assert updated.title == "Revised Approved Title"
    assert updated.status == "completed"
    assert updated.document_type == "Project documentation"  # Preserved

def test_document_deletion():
    doc = document_service.create_document(
        user_id=USER_A_ID,
        doc_data=DocumentCreate(
            title="Doc to be deleted",
            document_type="Cover letters",
            content="Temporary content."
        )
    )

    # Delete
    del_res = document_service.delete_document(document_id=doc.id, user_id=USER_A_ID)
    assert del_res["success"] is True

    # Retrieve should 404
    with pytest.raises(HTTPException) as exc_info:
        document_service.get_document_by_id(document_id=doc.id, user_id=USER_A_ID)
    assert exc_info.value.status_code == 404

def test_ownership_isolation_user_b_cannot_access_user_a():
    # User A creates a document
    doc_a = document_service.create_document(
        user_id=USER_A_ID,
        doc_data=DocumentCreate(
            title="User A Confidential Spec",
            document_type="Project documentation",
            content="Confidential proprietary information."
        )
    )

    # 1. User B cannot retrieve User A's document (returns 404)
    with pytest.raises(HTTPException) as exc_info:
        document_service.get_document_by_id(document_id=doc_a.id, user_id=USER_B_ID)
    assert exc_info.value.status_code == 404

    # 2. User B cannot update User A's document (returns 404)
    with pytest.raises(HTTPException) as exc_info:
        document_service.update_document(
            document_id=doc_a.id,
            user_id=USER_B_ID,
            update_data=DocumentUpdate(title="Malicious Overwrite")
        )
    assert exc_info.value.status_code == 404

    # 3. User B cannot delete User A's document (returns 404)
    with pytest.raises(HTTPException) as exc_info:
        document_service.delete_document(document_id=doc_a.id, user_id=USER_B_ID)
    assert exc_info.value.status_code == 404

    # 4. User B listing documents never includes User A's documents
    user_b_list = document_service.get_user_documents(user_id=USER_B_ID)
    assert not any(d.id == doc_a.id for d in user_b_list.documents)
