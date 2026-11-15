/**
 * API Service for Day 3 Persistence & Export
 * Handles document CRUD via Supabase-backed FastAPI endpoints
 * and binary exports (PDF / DOCX) with secure headers.
 */

const getAuthHeaders = (extraHeaders = {}) => {
  // Use user token from localStorage if logged in, or the demo dev token
  const token = localStorage.getItem('supabase_token') || 'demo-token-default-user';
  return {
    'Authorization': `Bearer ${token}`,
    ...extraHeaders
  };
};

/**
 * Extract filename from Content-Disposition header if available
 */
const getFilenameFromDisposition = (disposition, defaultFilename) => {
  if (!disposition) return defaultFilename;
  const match = disposition.match(/filename=["']?([^"';]+)["']?/i);
  if (match && match[1]) {
    return match[1].trim();
  }
  return defaultFilename;
};

/**
 * Trigger browser file download from a Blob
 */
export const triggerDownload = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 200);
};

// ----------------------------------------------------------------------
// Document Management Endpoints
// ----------------------------------------------------------------------

export const apiListDocuments = async ({ page = 1, limit = 20, document_type = null, status = null } = {}) => {
  const params = new URLSearchParams();
  if (page) params.append('page', page);
  if (limit) params.append('limit', limit);
  if (document_type) params.append('document_type', document_type);
  if (status) params.append('status', status);

  const res = await fetch(`/api/documents?${params.toString()}`, {
    method: 'GET',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch documents (${res.status})`);
  }

  return await res.json();
};

export const apiGetDocument = async (id) => {
  const res = await fetch(`/api/documents/${id}`, {
    method: 'GET',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Document not found or inaccessible (${res.status})`);
  }

  return await res.json();
};

export const apiCreateDocument = async ({ title, document_type, content, status = 'draft' }) => {
  const res = await fetch('/api/documents', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      title,
      document_type,
      content,
      status
    })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to save document (${res.status})`);
  }

  return await res.json();
};

export const apiUpdateDocument = async (id, { title, document_type, content, status }) => {
  const body = {};
  if (title !== undefined) body.title = title;
  if (document_type !== undefined) body.document_type = document_type;
  if (content !== undefined) body.content = content;
  if (status !== undefined) body.status = status;

  const res = await fetch(`/api/documents/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update document (${res.status})`);
  }

  return await res.json();
};

export const apiDeleteDocument = async (id) => {
  const res = await fetch(`/api/documents/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' })
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to delete document (${res.status})`);
  }

  return await res.json();
};

// ----------------------------------------------------------------------
// Export Endpoints (PDF & DOCX)
// ----------------------------------------------------------------------

export const apiExportPdf = async ({ documentId = null, title = 'Document', content = '' }) => {
  const body = {};
  if (documentId) {
    body.document_id = documentId;
  } else {
    body.title = title;
    body.content = content;
  }

  const res = await fetch('/api/export/pdf', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `PDF export failed (${res.status})`);
  }

  const disposition = res.headers.get('Content-Disposition');
  const safeTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'document';
  const filename = getFilenameFromDisposition(disposition, `${safeTitle}.pdf`);

  const blob = await res.blob();
  triggerDownload(blob, filename);
  return { filename, size: blob.size };
};

export const apiExportDocx = async ({ documentId = null, title = 'Document', content = '' }) => {
  const body = {};
  if (documentId) {
    body.document_id = documentId;
  } else {
    body.title = title;
    body.content = content;
  }

  const res = await fetch('/api/export/docx', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `DOCX export failed (${res.status})`);
  }

  const disposition = res.headers.get('Content-Disposition');
  const safeTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '') || 'document';
  const filename = getFilenameFromDisposition(disposition, `${safeTitle}.docx`);

  const blob = await res.blob();
  triggerDownload(blob, filename);
  return { filename, size: blob.size };
};

// ----------------------------------------------------------------------
// Day 4: Quality Assessment, Completeness & Comparison Endpoints
// ----------------------------------------------------------------------

export const apiAnalyzeQuality = async ({ documentId = null, content = null, documentType = "General Document", context = null }) => {
  const body = {};
  if (documentId) body.document_id = documentId;
  if (content) body.content = content;
  if (documentType) body.document_type = documentType;
  if (context) body.context = context;

  const res = await fetch('/api/quality/analyze', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Quality analysis failed (${res.status})`);
  }

  return await res.json();
};

export const apiAnalyzeCompleteness = async ({ documentId = null, content = null, documentType = "General Document" }) => {
  const body = {};
  if (documentId) body.document_id = documentId;
  if (content) body.content = content;
  if (documentType) body.document_type = documentType;

  const res = await fetch('/api/quality/completeness', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Completeness analysis failed (${res.status})`);
  }

  return await res.json();
};

export const apiImproveContent = async ({ documentId = null, content = null, operation = "improve_writing", instruction = null, context = null }) => {
  const body = { operation };
  if (documentId) body.document_id = documentId;
  if (content) body.content = content;
  if (instruction) body.instruction = instruction;
  if (context) body.context = context;

  const res = await fetch('/api/quality/improve', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Document improvement failed (${res.status})`);
  }

  return await res.json();
};

export const apiCompareDocuments = async ({ documentId1 = null, documentId2 = null, originalText = null, revisedText = null, title = null }) => {
  const body = {};
  if (documentId1) body.document_id_1 = documentId1;
  if (documentId2) body.document_id_2 = documentId2;
  if (originalText !== null) body.original_text = originalText;
  if (revisedText !== null) body.revised_text = revisedText;
  if (title) body.title = title;

  const res = await fetch('/api/documents/compare', {
    method: 'POST',
    headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Document comparison failed (${res.status})`);
  }

  return await res.json();
};
