import React, { useState, useEffect } from 'react';
import {
  FolderIcon,
  XIcon,
  TrashIcon,
  DownloadIcon,
  ClockIcon,
  FileTextIcon,
  SearchIcon,
  LoaderIcon,
  RefreshCwIcon
} from './Icons';
import {
  apiListDocuments,
  apiDeleteDocument,
  apiExportPdf,
  apiExportDocx
} from '../services/api';

export const DocumentHistoryModal = ({
  isOpen,
  onClose,
  onSelectDocument
}) => {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [deletingId, setDeletingId] = useState(null);
  const [exportingState, setExportingState] = useState({}); // { [docId]: 'pdf' | 'docx' }

  const loadDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await apiListDocuments({ limit: 50 });
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err.message || 'Failed to load documents from database.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadDocuments();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleDelete = async (docId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }

    setDeletingId(docId);
    try {
      await apiDeleteDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
    } catch (err) {
      alert(`Could not delete document: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const handleExport = async (doc, format, e) => {
    e.stopPropagation();
    setExportingState((prev) => ({ ...prev, [doc.id]: format }));
    try {
      if (format === 'pdf') {
        await apiExportPdf({ documentId: doc.id, title: doc.title });
      } else {
        await apiExportDocx({ documentId: doc.id, title: doc.title });
      }
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setExportingState((prev) => {
        const next = { ...prev };
        delete next[doc.id];
        return next;
      });
    }
  };

  const documentTypes = ['all', ...Array.from(new Set(documents.map((d) => d.document_type).filter(Boolean)))];

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (doc.document_type || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || doc.document_type === selectedType;
    return matchesSearch && matchesType;
  });

  const formatDate = (isoString) => {
    if (!isoString) return 'Recent';
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-scaleIn"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-brand-100 text-brand-700 flex items-center justify-center">
              <FolderIcon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                Document History
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
                  {documents.length} saved
                </span>
              </h3>
              <p className="text-xs text-slate-500">
                Supabase persistent storage • Click any document to open in editor
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadDocuments}
              disabled={isLoading}
              title="Refresh document list"
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-200/60 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCwIcon className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <XIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="px-6 py-3 border-b border-slate-100 bg-white flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[220px]">
            <SearchIcon className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by title or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
          </div>

          {documentTypes.length > 2 && (
            <div className="flex items-center gap-1.5 overflow-x-auto max-w-full pb-1 sm:pb-0">
              {documentTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className={`text-xs px-2.5 py-1 rounded-lg capitalize font-medium transition-all ${
                    selectedType === type
                      ? 'bg-brand-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {type}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Modal Body / Document List */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50">
          {isLoading && documents.length === 0 ? (
            <div className="py-16 flex flex-col items-center justify-center text-slate-400 gap-3">
              <LoaderIcon className="w-8 h-8 text-brand-600" />
              <p className="text-sm font-medium text-slate-600">Loading documents from Supabase...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-center">
              <p className="text-sm text-red-700 font-semibold mb-2">{error}</p>
              <button
                onClick={loadDocuments}
                className="px-3 py-1.5 text-xs bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
              >
                Retry
              </button>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div className="py-16 text-center text-slate-400 flex flex-col items-center gap-3">
              <FileTextIcon className="w-12 h-12 text-slate-300 stroke-[1.5]" />
              <div>
                <p className="text-sm font-semibold text-slate-700">No documents found</p>
                <p className="text-xs text-slate-400 mt-1 max-w-sm">
                  {searchTerm
                    ? 'No saved documents match your search criteria.'
                    : 'You haven’t saved any documents yet. Open the Document Editor and click "Save to Cloud" to persist your drafts.'}
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3">
              {filteredDocs.map((doc) => {
                const isDeleting = deletingId === doc.id;
                const activeExport = exportingState[doc.id];

                return (
                  <div
                    key={doc.id}
                    onClick={() => {
                      onSelectDocument(doc);
                      onClose();
                    }}
                    className="group bg-white p-4 rounded-xl border border-slate-200 hover:border-brand-400 hover:shadow-md transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-brand-50 text-brand-700 border border-brand-200">
                          {doc.document_type || 'General'}
                        </span>
                        <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${
                          doc.status === 'final'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                          {doc.status || 'draft'}
                        </span>
                      </div>
                      <h4 className="text-base font-bold text-slate-900 group-hover:text-brand-600 transition-colors truncate">
                        {doc.title}
                      </h4>
                      <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                        <span className="flex items-center gap-1">
                          <ClockIcon className="w-3.5 h-3.5" />
                          Updated {formatDate(doc.updated_at || doc.created_at)}
                        </span>
                        {doc.content && typeof doc.content === 'string' && (
                          <span>• {doc.content.split(/\s+/).length} words</span>
                        )}
                      </div>
                    </div>

                    {/* Action buttons */}
                    <div className="flex items-center gap-2 shrink-0">
                      {/* PDF Export */}
                      <button
                        type="button"
                        onClick={(e) => handleExport(doc, 'pdf', e)}
                        disabled={!!activeExport}
                        title="Download selectable ReportLab PDF"
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors disabled:opacity-50"
                      >
                        {activeExport === 'pdf' ? (
                          <LoaderIcon className="w-3.5 h-3.5 text-brand-600" />
                        ) : (
                          <DownloadIcon className="w-3.5 h-3.5" />
                        )}
                        <span>PDF</span>
                      </button>

                      {/* DOCX Export */}
                      <button
                        type="button"
                        onClick={(e) => handleExport(doc, 'docx', e)}
                        disabled={!!activeExport}
                        title="Download editable python-docx Word document"
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 transition-colors disabled:opacity-50"
                      >
                        {activeExport === 'docx' ? (
                          <LoaderIcon className="w-3.5 h-3.5 text-indigo-600" />
                        ) : (
                          <DownloadIcon className="w-3.5 h-3.5" />
                        )}
                        <span>DOCX</span>
                      </button>

                      {/* Delete */}
                      <button
                        type="button"
                        onClick={(e) => handleDelete(doc.id, e)}
                        disabled={isDeleting}
                        title="Delete document"
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                      >
                        {isDeleting ? (
                          <LoaderIcon className="w-4 h-4 text-red-600" />
                        ) : (
                          <TrashIcon className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Row Level Security (RLS) active • Only your documents are accessible</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-slate-200 text-slate-700 hover:bg-slate-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
