import React, { useState, useMemo, useEffect } from 'react';
import {
  CopyIcon,
  DownloadIcon,
  CheckIcon,
  EyeIcon,
  Edit3Icon,
  SparklesIcon,
  ArrowLeftIcon,
  RefreshCwIcon,
  SaveIcon,
  LoaderIcon,
  AwardIcon,
  GitCompareIcon,
  ZapIcon
} from './Icons';
import {
  apiCreateDocument,
  apiUpdateDocument,
  apiExportPdf,
  apiExportDocx,
  apiImproveContent,
  apiCompareDocuments
} from '../services/api';
import { QualityDashboardModal } from './QualityDashboardModal';
import { DiffComparisonModal } from './DiffComparisonModal';

export const DocumentEditor = ({
  documentData,
  onEditAnother,
  onRegenerate,
  onSaveSuccess
}) => {
  const [content, setContent] = useState(documentData?.content || "");
  const [savedDocId, setSavedDocId] = useState(
    documentData?.id && !documentData.id.toString().startsWith('mock-') ? documentData.id : null
  );
  const [activeTab, setActiveTab] = useState("preview"); // 'edit' or 'preview'
  const [copied, setCopied] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [isAiProcessing, setIsAiProcessing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isExportingPdf, setIsExportingPdf] = useState(false);
  const [isExportingDocx, setIsExportingDocx] = useState(false);

  // Day 4 Modals & States
  const [isQualityModalOpen, setIsQualityModalOpen] = useState(false);
  const [isDiffModalOpen, setIsDiffModalOpen] = useState(false);
  const [activeDiffData, setActiveDiffData] = useState(null);

  // Sync state if new documentData is passed from outside
  useEffect(() => {
    if (documentData) {
      setContent(documentData.content || "");
      if (documentData.id && !documentData.id.toString().startsWith('mock-')) {
        setSavedDocId(documentData.id);
      } else {
        setSavedDocId(null);
      }
    }
  }, [documentData]);

  // Compute stats
  const stats = useMemo(() => {
    const text = content.trim();
    const words = text ? text.split(/\s+/).length : 0;
    const chars = text.length;
    const readingTime = Math.max(1, Math.ceil(words / 225));
    return { words, chars, readingTime };
  }, [content]);

  // Insert markdown helper at cursor / end
  const handleInsertMarkdown = (prefix, suffix = '') => {
    setContent((prev) => `${prev}\n${prefix}Selected Text${suffix}\n`);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };

  // Save / Update to Supabase
  const handleSave = async () => {
    setIsSaving(true);
    setStatusMessage({ type: 'info', text: 'Saving document to Supabase...' });

    try {
      if (savedDocId) {
        // Update existing document
        const updated = await apiUpdateDocument(savedDocId, {
          title: documentData?.title || 'Untitled Document',
          content: content,
          document_type: documentData?.category || documentData?.document_type || 'General',
          status: 'draft'
        });
        setStatusMessage({ type: 'success', text: `Document updated successfully in Supabase` });
        if (onSaveSuccess) onSaveSuccess(updated);
      } else {
        // Create new document
        const created = await apiCreateDocument({
          title: documentData?.title || 'Generated Document',
          content: content,
          document_type: documentData?.category || documentData?.document_type || 'General',
          status: 'draft'
        });
        setSavedDocId(created.id);
        setStatusMessage({ type: 'success', text: `Saved to database with ID: ${created.id.substring(0, 8)}...` });
        if (onSaveSuccess) onSaveSuccess(created);
      }
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Save failed: ${err.message}` });
    } finally {
      setIsSaving(false);
      setTimeout(() => {
        setStatusMessage(null);
      }, 4000);
    }
  };

  // Export to ReportLab PDF
  const handleExportPdf = async () => {
    setIsExportingPdf(true);
    setStatusMessage({ type: 'info', text: 'Generating professional PDF via ReportLab...' });
    try {
      await apiExportPdf({
        documentId: savedDocId,
        title: documentData?.title || 'Document',
        content: content
      });
      setStatusMessage({ type: 'success', text: 'PDF downloaded successfully!' });
    } catch (err) {
      setStatusMessage({ type: 'error', text: `PDF export failed: ${err.message}` });
    } finally {
      setIsExportingPdf(false);
      setTimeout(() => setStatusMessage(null), 3500);
    }
  };

  // Export to python-docx Word document
  const handleExportDocx = async () => {
    setIsExportingDocx(true);
    setStatusMessage({ type: 'info', text: 'Generating editable Word document via python-docx...' });
    try {
      await apiExportDocx({
        documentId: savedDocId,
        title: documentData?.title || 'Document',
        content: content
      });
      setStatusMessage({ type: 'success', text: 'DOCX downloaded successfully!' });
    } catch (err) {
      setStatusMessage({ type: 'error', text: `DOCX export failed: ${err.message}` });
    } finally {
      setIsExportingDocx(false);
      setTimeout(() => setStatusMessage(null), 3500);
    }
  };

  // Quick fallback text/markdown download
  const handleQuickDownload = (format = 'md') => {
    const blob = new Blob([content], { type: format === 'md' ? 'text/markdown' : 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement('a');
    const safeTitle = (documentData?.title || 'generated-document')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
    link.href = url;
    link.download = `${safeTitle}.${format}`;
    window.document.body.appendChild(link);
    link.click();
    window.document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // Day 4: Trigger AI Improvement with Diff Review
  const handleTriggerImprove = async (operation) => {
    setIsAiProcessing(true);
    const opTitle = operation.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
    setStatusMessage({ type: 'info', text: `Applying AI Improvement: ${opTitle}...` });

    try {
      const impRes = await apiImproveContent({
        documentId: savedDocId,
        content: content,
        operation: operation,
        context: documentData?.title || ""
      });

      // Calculate diff between current content and revised
      const diffRes = await apiCompareDocuments({
        originalText: content,
        revisedText: impRes.revised_text,
        title: `AI Improvement: ${opTitle}`
      });

      setActiveDiffData({
        ...diffRes,
        original_text: content,
        revised_text: impRes.revised_text
      });
      setIsDiffModalOpen(true);
      setStatusMessage({ type: 'success', text: `Generated revision: review diff and accept or discard.` });
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Improvement failed: ${err.message}` });
    } finally {
      setIsAiProcessing(false);
      setTimeout(() => setStatusMessage(null), 4000);
    }
  };

  // Compare Current Editor vs Saved Document
  const handleCompareWithSaved = async () => {
    if (!savedDocId) {
      alert("Please save this document to Supabase first before comparing with previous saved version.");
      return;
    }

    setIsAiProcessing(true);
    setStatusMessage({ type: 'info', text: 'Comparing current editor text with saved version...' });

    try {
      const diffRes = await apiCompareDocuments({
        documentId1: savedDocId,
        revisedText: content,
        title: `Current Editor vs Saved Version`
      });

      setActiveDiffData({
        ...diffRes,
        original_text: documentData?.content || "",
        revised_text: content
      });
      setIsDiffModalOpen(true);
      setStatusMessage({ type: 'success', text: `Comparison loaded.` });
    } catch (err) {
      setStatusMessage({ type: 'error', text: `Comparison error: ${err.message}` });
    } finally {
      setIsAiProcessing(false);
      setTimeout(() => setStatusMessage(null), 3000);
    }
  };

  // Simple Markdown renderer for Preview Tab
  const renderSimpleMarkdown = (raw) => {
    const lines = raw.split('\n');
    return lines.map((line, idx) => {
      if (line.startsWith('# ')) {
        return <h1 key={idx} className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-6 mb-3 border-b pb-2">{line.replace('# ', '')}</h1>;
      }
      if (line.startsWith('## ')) {
        return <h2 key={idx} className="text-xl sm:text-2xl font-bold text-slate-800 mt-5 mb-2.5">{line.replace('## ', '')}</h2>;
      }
      if (line.startsWith('### ')) {
        return <h3 key={idx} className="text-lg font-bold text-slate-800 mt-4 mb-2">{line.replace('### ', '')}</h3>;
      }
      if (line.startsWith('> ')) {
        return (
          <blockquote key={idx} className="border-l-4 border-brand-500 pl-4 py-1.5 my-3 bg-brand-50/50 text-slate-700 italic text-sm rounded-r-lg">
            {line.replace('> ', '')}
          </blockquote>
        );
      }
      if (line.startsWith('```')) {
        return <div key={idx} className="my-1 text-xs text-slate-400 font-mono"></div>;
      }
      if (line.startsWith('|')) {
        return (
          <div key={idx} className="overflow-x-auto font-mono text-xs my-1 text-slate-700">
            {line}
          </div>
        );
      }
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <li key={idx} className="ml-5 list-disc text-sm text-slate-700 my-1">
            {line.substring(2)}
          </li>
        );
      }
      if (line.startsWith('1. ') || line.startsWith('2. ') || line.startsWith('3. ')) {
        return (
          <li key={idx} className="ml-5 list-decimal text-sm text-slate-700 my-1">
            {line.substring(3)}
          </li>
        );
      }
      if (line.trim() === '---') {
        return <hr key={idx} className="my-6 border-slate-200" />;
      }
      if (line.trim() === '') {
        return <div key={idx} className="h-2"></div>;
      }
      return (
        <p key={idx} className="text-sm text-slate-700 leading-relaxed my-2">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="space-y-6 animate-fadeIn max-w-6xl mx-auto">
      {/* Top Banner & Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <button
            onClick={onEditAnother}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors mb-2"
          >
            <ArrowLeftIcon className="w-3.5 h-3.5" />
            Back to Inputs & Prompts
          </button>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">
              {documentData?.title || "Document Draft"}
            </h2>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200">
              {documentData?.category || documentData?.document_type || "Standard Template"}
            </span>
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
              Tone: {documentData?.tone || "Professional"}
            </span>
            {savedDocId && (
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                Persisted in Supabase
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400 mt-1">
            {savedDocId ? `Saved ID: ${savedDocId}` : `Generated draft ready for cloud saving, quality audit & export`}
          </p>
        </div>

        {/* Global Document Actions */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Day 4: Quality & Completeness Modal Trigger */}
          <button
            onClick={() => setIsQualityModalOpen(true)}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 shadow-2xs transition-all"
            title="Inspect quality score, category breakdown, and completeness matrix"
          >
            <AwardIcon className="w-3.5 h-3.5 text-indigo-600" />
            <span>Quality Score</span>
          </button>

          {/* Day 4: Compare with Saved */}
          {savedDocId && (
            <button
              onClick={handleCompareWithSaved}
              disabled={isAiProcessing}
              className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 shadow-2xs transition-all disabled:opacity-50"
              title="Compare current draft against last saved revision"
            >
              <GitCompareIcon className="w-3.5 h-3.5" />
              <span>Compare</span>
            </button>
          )}

          {/* Save / Update to Supabase */}
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white shadow-xs transition-all disabled:opacity-50"
            title="Save document and content to Supabase database"
          >
            {isSaving ? (
              <LoaderIcon className="w-3.5 h-3.5 text-white" />
            ) : (
              <SaveIcon className="w-3.5 h-3.5" />
            )}
            <span>{savedDocId ? 'Update in Cloud' : 'Save to Cloud'}</span>
          </button>

          {/* ReportLab PDF Export */}
          <button
            onClick={handleExportPdf}
            disabled={isExportingPdf}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-brand-600 hover:bg-brand-700 text-white shadow-xs transition-all disabled:opacity-50"
            title="Generate professional PDF via ReportLab"
          >
            {isExportingPdf ? (
              <LoaderIcon className="w-3.5 h-3.5 text-white" />
            ) : (
              <DownloadIcon className="w-3.5 h-3.5" />
            )}
            <span>PDF</span>
          </button>

          {/* python-docx DOCX Export */}
          <button
            onClick={handleExportDocx}
            disabled={isExportingDocx}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs transition-all disabled:opacity-50"
            title="Generate editable Word document via python-docx"
          >
            {isExportingDocx ? (
              <LoaderIcon className="w-3.5 h-3.5 text-white" />
            ) : (
              <DownloadIcon className="w-3.5 h-3.5" />
            )}
            <span>DOCX</span>
          </button>

          {/* Copy Markdown */}
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 shadow-xs transition-all"
          >
            {copied ? (
              <>
                <CheckIcon className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700 font-bold">Copied!</span>
              </>
            ) : (
              <>
                <CopyIcon className="w-3.5 h-3.5" />
                Copy
              </>
            )}
          </button>

          {/* Quick .md / .txt fallback */}
          <div className="relative inline-flex rounded-xl shadow-xs">
            <button
              onClick={() => handleQuickDownload('md')}
              className="px-2.5 py-2 rounded-l-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 transition-all"
              title="Quick download as raw markdown"
            >
              .md
            </button>
            <button
              onClick={() => handleQuickDownload('txt')}
              className="px-2.5 py-2 rounded-r-xl text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-l-0 border-slate-300 transition-all"
              title="Quick download as plain text"
            >
              .txt
            </button>
          </div>

          {/* Regenerate */}
          <button
            onClick={onRegenerate}
            className="p-2 rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-100 border border-slate-200 transition-all"
            title="Re-run generation with current parameters"
          >
            <RefreshCwIcon className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Status / Notification Pill */}
      {statusMessage && (
        <div className={`p-3 rounded-xl text-xs flex items-center justify-between animate-fadeIn border ${
          statusMessage.type === 'error'
            ? 'bg-red-50 border-red-200 text-red-800'
            : statusMessage.type === 'success'
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
            : 'bg-brand-50 border-brand-200 text-brand-800'
        }`}>
          <span className="flex items-center gap-2 font-medium">
            {statusMessage.type === 'info' && <SparklesIcon className="w-4 h-4 text-brand-600 animate-spin" />}
            {statusMessage.type === 'success' && <CheckIcon className="w-4 h-4 text-emerald-600" />}
            {statusMessage.text}
          </span>
        </div>
      )}

      {/* Editor Main Card */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex flex-col min-h-[620px]">
        {/* Editor Toolbar */}
        <div className="bg-slate-50/80 border-b border-slate-200 p-3 flex flex-wrap items-center justify-between gap-3">
          {/* View Toggle Tabs */}
          <div className="flex items-center bg-slate-200/80 p-0.5 rounded-xl">
            <button
              type="button"
              onClick={() => setActiveTab('preview')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'preview'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <EyeIcon className="w-3.5 h-3.5" />
              Rendered Preview
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('edit')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'edit'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Edit3Icon className="w-3.5 h-3.5" />
              Raw Markdown Editor
            </button>
          </div>

          {/* Quick Markdown Inserts (shown on edit) */}
          {activeTab === 'edit' && (
            <div className="hidden sm:flex items-center gap-1 border-l border-slate-300 pl-3">
              <button
                type="button"
                onClick={() => handleInsertMarkdown('## ')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-mono font-bold text-slate-700"
                title="Heading 2"
              >
                H2
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('### ')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-mono font-bold text-slate-700"
                title="Heading 3"
              >
                H3
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('**', '**')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-bold text-slate-700"
                title="Bold"
              >
                B
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('*', '*')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs italic text-slate-700"
                title="Italic"
              >
                I
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('> ')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-mono text-slate-700"
                title="Quote"
              >
                &ldquo;&rdquo;
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('- ')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-mono text-slate-700"
                title="Bullet List"
              >
                • List
              </button>
              <button
                type="button"
                onClick={() => handleInsertMarkdown('```\n', '\n```')}
                className="px-2 py-1 rounded hover:bg-slate-200 text-xs font-mono text-slate-700"
                title="Code Block"
              >
                &lt;/&gt;
              </button>
            </div>
          )}

          {/* Day 4 AI Improvement Toolbar */}
          <div className="flex flex-wrap items-center gap-1.5 ml-auto">
            <span className="text-[11px] font-semibold text-slate-400 hidden xl:inline">
              AI Refinements:
            </span>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("improve_grammar")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors disabled:opacity-50"
              title="Fix spelling, grammar and syntax errors"
            >
              Fix Grammar
            </button>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("improve_professionalism")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 transition-colors disabled:opacity-50"
              title="Elevate tone to executive and authoritative standard"
            >
              Make Professional
            </button>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("simplify_language")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 transition-colors disabled:opacity-50"
              title="Simplify convoluted sentences into clear prose"
            >
              Simplify
            </button>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("expand_explanations")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-brand-50 text-brand-700 hover:bg-brand-100 border border-brand-200 transition-colors disabled:opacity-50"
              title="Expand with concrete technical details and examples"
            >
              + Expand
            </button>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("shorten_content")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-300 transition-colors disabled:opacity-50"
              title="Condense and remove fluff"
            >
              Shorten
            </button>
            <button
              type="button"
              disabled={isAiProcessing}
              onClick={() => handleTriggerImprove("improve_structure")}
              className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 transition-colors disabled:opacity-50"
              title="Organize with headings and numbered milestones"
            >
              Structure
            </button>
          </div>
        </div>

        {/* Editor Body */}
        <div className="flex-1 p-6 overflow-y-auto">
          {activeTab === 'preview' ? (
            <div className="prose max-w-none px-2 sm:px-6 py-2">
              {renderSimpleMarkdown(content)}
            </div>
          ) : (
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full h-full min-h-[500px] p-4 font-mono text-xs sm:text-sm text-slate-800 bg-transparent border-0 outline-none resize-none leading-relaxed"
              placeholder="Write or edit generated document markdown here..."
            />
          )}
        </div>

        {/* Editor Footer / Telemetry Bar */}
        <div className="bg-slate-50 border-t border-slate-200 px-6 py-3 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-3">
          <div className="flex items-center gap-4">
            <span>
              Words: <strong className="text-slate-800">{stats.words}</strong>
            </span>
            <span>
              Characters: <strong className="text-slate-800">{stats.chars}</strong>
            </span>
            <span>
              Reading Time: <strong className="text-slate-800">~{stats.readingTime} min</strong>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-indigo-500"></span>
            <span className="text-[11px] text-slate-600 font-medium">
              Day 4 Active: Quality Scoring • Completeness Matrix • Diff Comparison Review
            </span>
          </div>
        </div>
      </div>

      {/* Quality & Completeness Modal */}
      <QualityDashboardModal
        isOpen={isQualityModalOpen}
        onClose={() => setIsQualityModalOpen(false)}
        content={content}
        documentType={documentData?.category || documentData?.document_type || "General Document"}
        documentId={savedDocId}
        onTriggerImprove={handleTriggerImprove}
      />

      {/* Diff Comparison & Review Modal */}
      <DiffComparisonModal
        isOpen={isDiffModalOpen}
        onClose={() => setIsDiffModalOpen(false)}
        diffData={activeDiffData}
        onApplyChanges={(revised) => {
          setContent(revised);
          setStatusMessage({ type: 'success', text: 'Applied AI revision to editor.' });
        }}
      />
    </div>
  );
};
