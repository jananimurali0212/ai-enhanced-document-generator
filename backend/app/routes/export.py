"""
Export API Endpoints for PDF and DOCX.
Generates downloadable, high-fidelity PDF and Word documents
with strict ownership verification and temporary-file cleanup.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.auth import get_current_user, AuthenticatedUser
from app.schemas.export import ExportRequest
from app.services.document_service import document_service
from app.services.export_service import export_service
from app.utils.file_utils import sanitize_filename, cleanup_file

router = APIRouter(prefix="/api/export", tags=["Document Export"])

@router.post(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export document as downloadable PDF"
)
def export_pdf(
    payload: ExportRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Exports a document as a publication-ready PDF.
    If 'document_id' is supplied, verifies user ownership before rendering.
    """
    if payload.document_id:
        # Retrieve owned document
        doc = document_service.get_document_by_id(
            document_id=payload.document_id,
            user_id=current_user.id,
            token=current_user.token
        )
        title = doc.title
        content = doc.content
        doc_type = doc.document_type
    else:
        title = payload.title or "Generated Document"
        content = payload.content
        doc_type = payload.document_type or "General Document"

    # Render PDF to temporary file
    try:
        temp_pdf_path = export_service.generate_pdf(
            title=title,
            content=content,
            document_type=doc_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF rendering failed: {str(e)}"
        )

    safe_name = sanitize_filename(title, default_name="document", extension="pdf")

    return FileResponse(
        path=temp_pdf_path,
        media_type="application/pdf",
        filename=safe_name,
        background=BackgroundTask(cleanup_file, temp_pdf_path),
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"'
        }
    )

@router.post(
    "/docx",
    status_code=status.HTTP_200_OK,
    summary="Export document as editable DOCX"
)
def export_docx(
    payload: ExportRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Exports a document as an editable Microsoft Word document (.docx).
    If 'document_id' is supplied, verifies user ownership before rendering.
    """
    if payload.document_id:
        doc = document_service.get_document_by_id(
            document_id=payload.document_id,
            user_id=current_user.id,
            token=current_user.token
        )
        title = doc.title
        content = doc.content
        doc_type = doc.document_type
    else:
        title = payload.title or "Generated Document"
        content = payload.content
        doc_type = payload.document_type or "General Document"

    # Render DOCX to temporary file
    try:
        temp_docx_path = export_service.generate_docx(
            title=title,
            content=content,
            document_type=doc_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOCX rendering failed: {str(e)}"
        )

    safe_name = sanitize_filename(title, default_name="document", extension="docx")

    return FileResponse(
        path=temp_docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=safe_name,
        background=BackgroundTask(cleanup_file, temp_docx_path),
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"'
        }
    )
