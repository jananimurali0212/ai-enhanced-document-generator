import React, { useState } from 'react';
import {
  GitCompareIcon,
  XIcon,
  CheckIcon,
  ZapIcon
} from './Icons';

export const DiffComparisonModal = ({
  isOpen,
  onClose,
  diffData,
  onApplyChanges
}) => {
  const [viewMode, setViewMode] = useState('unified'); // 'unified' or 'side-by-side'

  if (!isOpen || !diffData) return null;

  const {
    title = "Document Comparison & Review",
    summary = "Review the proposed changes before accepting them into your document draft.",
    similarity_percentage = 100,
    added = [],
    removed = [],
    modified = [],
    diff_blocks = [],
    original_text = "",
    revised_text = ""
  } = diffData;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden animate-scaleIn"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
              <GitCompareIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-slate-900">{title}</h3>
                <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {similarity_percentage}% Similar
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Review proposed additions and edits before replacing editor content
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center bg-slate-200/80 p-0.5 rounded-lg text-xs mr-2">
              <button
                type="button"
                onClick={() => setViewMode('unified')}
                className={`px-3 py-1 font-semibold rounded-md transition-all ${
                  viewMode === 'unified'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Unified Diff
              </button>
              <button
                type="button"
                onClick={() => setViewMode('side-by-side')}
                className={`px-3 py-1 font-semibold rounded-md transition-all ${
                  viewMode === 'side-by-side'
                    ? 'bg-white text-slate-900 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Side-by-Side
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <XIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Change Telemetry & AI Summary Banner */}
        <div className="px-6 py-4 bg-indigo-50/40 border-b border-indigo-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex-1">
            <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-900 block mb-1">
              AI Editorial Summary
            </span>
            <p className="text-xs text-indigo-950 font-medium leading-relaxed">
              {summary}
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs shrink-0 font-mono">
            <span className="px-2.5 py-1 rounded-md bg-emerald-100 text-emerald-800 font-bold border border-emerald-300">
              +{added.length} added
            </span>
            <span className="px-2.5 py-1 rounded-md bg-rose-100 text-rose-800 font-bold border border-rose-300">
              -{removed.length} removed
            </span>
            {modified.length > 0 && (
              <span className="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 font-bold border border-amber-300">
                ~{modified.length} modified
              </span>
            )}
          </div>
        </div>

        {/* Diff Viewport */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-900 font-mono text-xs leading-relaxed">
          {viewMode === 'unified' ? (
            <div className="space-y-0.5">
              {diff_blocks && diff_blocks.length > 0 ? (
                diff_blocks.map((block, idx) => {
                  const isAdded = block.type === 'added';
                  const isRemoved = block.type === 'removed';
                  return (
                    <div
                      key={idx}
                      className={`px-3 py-1 rounded flex items-start gap-3 ${
                        isAdded
                          ? 'bg-emerald-950/70 text-emerald-300 border-l-2 border-emerald-500'
                          : isRemoved
                          ? 'bg-rose-950/70 text-rose-300 line-through border-l-2 border-rose-500'
                          : 'text-slate-300'
                      }`}
                    >
                      <span className="select-none text-slate-500 w-4 font-bold">
                        {isAdded ? '+' : isRemoved ? '-' : ' '}
                      </span>
                      <span className="whitespace-pre-wrap break-all flex-1">{block.text || ' '}</span>
                    </div>
                  );
                })
              ) : (
                <div className="text-slate-400 py-10 text-center">
                  No structural diff detected between versions.
                </div>
              )}
            </div>
          ) : (
            /* Side-by-Side */
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-bold text-rose-400 uppercase tracking-wider block mb-2">
                  Original Document
                </span>
                <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono">
                  {original_text || "(Empty)"}
                </pre>
              </div>

              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider block mb-2">
                  Revised Document
                </span>
                <pre className="text-xs text-slate-300 whitespace-pre-wrap font-mono">
                  {revised_text || "(Empty)"}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Footer with Actions */}
        <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-200 transition-colors"
          >
            Discard Changes
          </button>

          <button
            onClick={() => {
              if (onApplyChanges && revised_text) {
                onApplyChanges(revised_text);
              }
              onClose();
            }}
            className="inline-flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white shadow-md shadow-emerald-600/20 transition-all"
          >
            <CheckIcon className="w-4 h-4" />
            Accept & Apply Revision
          </button>
        </div>
      </div>
    </div>
  );
};
