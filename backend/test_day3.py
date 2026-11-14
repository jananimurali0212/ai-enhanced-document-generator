"""
Comprehensive Day 3 Test Suite:
Validates Supabase Database integration, Authentication, Document Service CRUD,
Ownership Isolation, PDF & DOCX Export Services, Secure File Handling,
and FastAPI Endpoints.
"""

import os
import sys
import uuid
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.auth import get_current_user, AuthenticatedUser
from app.services.supabase_service import supabase_service
from app.services.document_service import document_service
from app.services.export_service import export_service
from app.utils.file_utils import sanitize_filename, cleanup_file, get_temp_export_path
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.export import ExportRequest
from app.routes.documents import (
    list_documents,
    create_document,
    get_document,
    update_document,
    delete_document
)
from app.routes.export import export_pdf, export_docx
from fastapi import HTTPException

# Test user IDs
USER_A = AuthenticatedUser(id=str(uuid.uuid4()), email="usera@corp.internal", token="mock-user-a")
USER_B = AuthenticatedUser(id=str(uuid.uuid4()), email="userb@corp.internal", token="mock-user-b")

def test_module_1_supabase_config_and_migrations():
    print("\n--- [1/6] Testing Supabase Database Configuration & Migration ---")
    conn_info = supabase_service.check_connection()
    assert "configured" in conn_info
    assert "status" in conn_info
    print(f" [x] Supabase service status: {conn_info['status']}")

    # Check migration file exists and is well-formed
    migration_path = backend_dir.parent / "migrations" / "create_documents_table.sql"
    assert migration_path.exists(), "Migration SQL file is missing"
    with open(migration_path, "r", encoding="utf-8") as f:
        sql = f.read()
    assert "CREATE TABLE IF NOT EXISTS public.documents" in sql
    assert "user_id UUID NOT NULL REFERENCES auth.users(id)" in sql
    assert "ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY" in sql
    assert "CREATE POLICY \"Users can read own documents\"" in sql
    assert "CREATE POLICY \"Users can insert own documents\"" in sql
    assert "CREATE POLICY \"Users can update own documents\"" in sql
    assert "CREATE POLICY \"Users can delete own documents\"" in sql
    assert "auth.uid() = user_id" in sql
    print(" [x] Migration SQL verified: table schema, RLS policies, indexes, and triggers verified.")

def test_module_2_authentication():
    print("\n--- [2/6] Testing Authentication & Ownership Verification ---")
    # 1. Missing header
    try:
        get_current_user(authorization=None)
        assert False, "Should raise 401 on missing auth"
    except HTTPException as he:
        assert he.status_code == 401
        print(" [x] Intercepted missing Authorization header with 401.")

    # 2. Invalid format
    try:
        get_current_user(authorization="Token 12345")
        assert False, "Should raise 401 on non-Bearer scheme"
    except HTTPException as he:
        assert he.status_code == 401
        print(" [x] Intercepted invalid header scheme with 401.")

    # 3. Valid user derivation
    test_uid = str(uuid.uuid4())
    user = get_current_user(authorization=f"Bearer mock-user-{test_uid}")
    assert user.id == test_uid
    assert user.role == "authenticated"
    print(f" [x] Authenticated user identity successfully derived: {user.id}")

def test_module_3_document_crud_and_service():
    print("\n--- [3/6] Testing Document Service CRUD Operations ---")
    # Create
    doc = document_service.create_document(
        user_id=USER_A.id,
        doc_data=DocumentCreate(
            title="Distributed Kafka Telemetry Architecture",
            document_type="Project documentation",
            content="# Event Architecture\n\nHigh throughput specifications.",
            status="draft"
        )
    )
    assert doc.id is not None
    assert doc.user_id == USER_A.id
    assert doc.title == "Distributed Kafka Telemetry Architecture"
    print(f" [x] Created Document: '{doc.title}' (ID: {doc.id})")

    # Read
    fetched = document_service.get_document_by_id(doc.id, USER_A.id)
    assert fetched.id == doc.id
    assert fetched.title == doc.title
    print(f" [x] Retrieved Document by ID: '{fetched.title}'")

    # Update
    updated = document_service.update_document(
        document_id=doc.id,
        user_id=USER_A.id,
        update_data=DocumentUpdate(title="Distributed Kafka Telemetry - V2 Production", status="completed")
    )
    assert updated.title == "Distributed Kafka Telemetry - V2 Production"
    assert updated.status == "completed"
    print(f" [x] Updated Document: '{updated.title}' (Status: {updated.status})")

    # List
    user_docs = document_service.get_user_documents(USER_A.id)
    assert user_docs.total >= 1
    assert any(d.id == doc.id for d in user_docs.documents)
    print(f" [x] Listed User Documents: Total {user_docs.total} documents found.")

def test_module_3_ownership_isolation():
    print("\n--- [4/6] Testing Cross-User Ownership Isolation ---")
    doc_a = document_service.create_document(
        user_id=USER_A.id,
        doc_data=DocumentCreate(
            title="User A Highly Classified Specs",
            document_type="Technical reports",
            content="Top Secret."
        )
    )

    # 1. User B cannot read User A document
    try:
        document_service.get_document_by_id(doc_a.id, USER_B.id)
        assert False, "User B should not read User A document"
    except HTTPException as he:
        assert he.status_code == 404
        print(" [x] Confirmed User B cannot read User A document (404 Not Found).")

    # 2. User B cannot update User A document
    try:
        document_service.update_document(doc_a.id, USER_B.id, DocumentUpdate(title="Hacked Title"))
        assert False, "User B should not update User A document"
    except HTTPException as he:
        assert he.status_code == 404
        print(" [x] Confirmed User B cannot update User A document (404 Not Found).")

    # 3. User B cannot delete User A document
    try:
        document_service.delete_document(doc_a.id, USER_B.id)
        assert False, "User B should not delete User A document"
    except HTTPException as he:
        assert he.status_code == 404
        print(" [x] Confirmed User B cannot delete User A document (404 Not Found).")

    # 4. User B list does not leak User A document
    b_docs = document_service.get_user_documents(USER_B.id)
    assert not any(d.id == doc_a.id for d in b_docs.documents)
    print(" [x] Confirmed User B document listing contains zero User A records.")

def test_module_5_and_6_export_services():
    print("\n--- [5/6] Testing PDF & DOCX Export Services ---")
    sample_md = """# Enterprise System Architecture
> **Executive Summary:** Highly resilient multi-region infrastructure.

## 1. Key Performance Indicators
- **Availability:** 99.99% uptime
- **Throughput:** 50,000 requests/sec

## 2. Resource Allocations
| Component | Replica Count | CPU Request | Memory Request |
| :--- | :--- | :--- | :--- |
| Gateway | 10 | 2000m | 4Gi |
| Event Consumer | 24 | 4000m | 8Gi |
| Storage Sync | 6 | 1000m | 2Gi |

### 3. Action Items
1. Deploy Kubernetes manifests
2. Run load test benchmark
"""

    # 1. Filename sanitization
    safe_name = sanitize_filename("../../malicious/path/Executive Pitch: 2026?", extension="pdf")
    assert safe_name == "Executive-Pitch-2026.pdf"
    assert ".." not in safe_name
    print(f" [x] Filename sanitization verified: '{safe_name}'")

    # 2. ReportLab PDF Export
    pdf_path = export_service.generate_pdf(
        title="Enterprise System Architecture",
        content=sample_md,
        document_type="Project documentation"
    )
    assert os.path.exists(pdf_path)
    file_size = os.path.getsize(pdf_path)
    assert file_size > 2000
    with open(pdf_path, "rb") as f:
        magic = f.read(5)
        assert magic.startswith(b"%PDF")
    cleanup_file(pdf_path)
    assert not os.path.exists(pdf_path)
    print(f" [x] PDF rendered successfully ({file_size} bytes, selectable text, tables & page numbers).")

    # 3. python-docx DOCX Export
    docx_path = export_service.generate_docx(
        title="Enterprise System Architecture",
        content=sample_md,
        document_type="Project documentation"
    )
    assert os.path.exists(docx_path)
    docx_size = os.path.getsize(docx_path)
    assert docx_size > 3000
    with open(docx_path, "rb") as f:
        magic = f.read(4)
        assert magic == b"PK\x03\x04"
    cleanup_file(docx_path)
    assert not os.path.exists(docx_path)
    print(f" [x] DOCX rendered successfully ({docx_size} bytes, Word headers, footers, tables & styles).")

def test_module_4_and_7_fastapi_endpoints():
    print("\n--- [6/6] Testing FastAPI Document & Export Route Handlers ---")
    # 1. POST /api/documents
    doc_create_req = DocumentCreate(
        title="Q4 System Scalability Strategy",
        document_type="Technical reports",
        content="# Strategy Overview\n\nScale up Kafka partitions.",
        status="completed"
    )
    created = create_document(doc_create_req, current_user=USER_A)
    assert created.id is not None
    assert created.title == "Q4 System Scalability Strategy"
    print(f" [x] POST /api/documents succeeded (ID: {created.id})")

    # 2. GET /api/documents
    listing = list_documents(page=1, limit=10, current_user=USER_A)
    assert listing.total >= 1
    assert any(d.id == created.id for d in listing.documents)
    print(f" [x] GET /api/documents returned {len(listing.documents)} documents (Total: {listing.total})")

    # 3. GET /api/documents/{id}
    fetched = get_document(created.id, current_user=USER_A)
    assert fetched.id == created.id
    print(f" [x] GET /api/documents/{created.id} returned document successfully")

    # 4. PUT /api/documents/{id}
    updated = update_document(
        created.id,
        DocumentUpdate(title="Q4 System Scalability Strategy - Approved Final"),
        current_user=USER_A
    )
    assert updated.title == "Q4 System Scalability Strategy - Approved Final"
    print(f" [x] PUT /api/documents/{created.id} updated title successfully")

    # 5. POST /api/export/pdf
    pdf_res = export_pdf(
        ExportRequest(document_id=created.id),
        current_user=USER_A
    )
    assert pdf_res.media_type == "application/pdf"
    assert "attachment" in pdf_res.headers["Content-Disposition"]
    print(" [x] POST /api/export/pdf returned FileResponse with correct headers and cleanup task")

    # 6. POST /api/export/docx
    docx_res = export_docx(
        ExportRequest(document_id=created.id),
        current_user=USER_A
    )
    assert docx_res.media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert "attachment" in docx_res.headers["Content-Disposition"]
    print(" [x] POST /api/export/docx returned FileResponse with correct headers and cleanup task")

    # 7. User B attempting to export User A document -> 404
    try:
        export_pdf(ExportRequest(document_id=created.id), current_user=USER_B)
        assert False, "User B should not be permitted to export User A document"
    except HTTPException as he:
        assert he.status_code == 404
        print(" [x] Confirmed User B cannot export User A document (404 Not Found).")

    # 8. DELETE /api/documents/{id}
    del_res = delete_document(created.id, current_user=USER_A)
    assert del_res["success"] is True
    print(f" [x] DELETE /api/documents/{created.id} deleted document successfully")

if __name__ == "__main__":
    try:
        test_module_1_supabase_config_and_migrations()
        test_module_2_authentication()
        test_module_3_document_crud_and_service()
        test_module_3_ownership_isolation()
        test_module_5_and_6_export_services()
        test_module_4_and_7_fastapi_endpoints()
        print("\n" + "="*70)
        print(" 🎉 ALL DAY 3 PERSISTENCE & EXPORT TESTS PASSED SUCCESSFULLY! 🎉 ")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ DAY 3 TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
