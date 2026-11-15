import React, { useState, useEffect } from 'react';
import {
  AwardIcon,
  ShieldCheckIcon,
  CheckCircleIcon,
  AlertCircleIcon,
  XIcon,
  RefreshCwIcon,
  LoaderIcon,
  ZapIcon
} from './Icons';
import { apiAnalyzeQuality, apiAnalyzeCompleteness } from '../services/api';

export const QualityDashboardModal = ({
  isOpen,
  onClose,
  content,
  documentType = "General Document",
  documentId = null,
  onTriggerImprove
}) => {
  const [activeTab, setActiveTab] = useState('quality'); // 'quality' or 'completeness'
  const [qualityData, setQualityData] = useState(null);
  const [completenessData, setCompletenessData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [qRes, cRes] = await Promise.all([
        apiAnalyzeQuality({ documentId, content, documentType }),
        apiAnalyzeCompleteness({ documentId, content, documentType })
      ]);
      setQualityData(qRes);
      setCompletenessData(cRes);
    } catch (err) {
      setError(err.message || 'Failed to analyze document quality.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen, content, documentId, documentType]);

  if (!isOpen) return null;

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 70) return 'text-indigo-600 bg-indigo-50 border-indigo-200';
    if (score >= 55) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-rose-600 bg-rose-50 border-rose-200';
  };

  const getProgressColor = (score) => {
    if (score >= 85) return 'bg-emerald-500';
    if (score >= 70) return 'bg-indigo-500';
    if (score >= 55) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-fadeIn">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[88vh] flex flex-col overflow-hidden animate-scaleIn"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 flex items-center justify-center">
              <AwardIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-slate-900">
                  Document Quality & Completeness
                </h3>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                  {documentType}
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Multi-dimensional AI quality evaluation & structural completeness audit
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={fetchData}
              disabled={isLoading}
              title="Re-analyze document"
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

        {/* Tab Selector */}
        <div className="px-6 border-b border-slate-200 bg-white flex items-center gap-4">
          <button
            onClick={() => setActiveTab('quality')}
            className={`py-3 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'quality'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <AwardIcon className="w-4 h-4" />
            Quality Scoring ({qualityData ? `${qualityData.overall_score}/100` : '...'})
          </button>
          <button
            onClick={() => setActiveTab('completeness')}
            className={`py-3 text-xs font-bold border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'completeness'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <ShieldCheckIcon className="w-4 h-4" />
            Completeness ({completenessData ? `${completenessData.completeness_percentage}%` : '...'})
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 bg-slate-50/40">
          {isLoading && !qualityData ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
              <LoaderIcon className="w-8 h-8 text-indigo-600" />
              <p className="text-sm font-medium text-slate-600">Evaluating document quality & section completeness...</p>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-center">
              <p className="text-sm text-red-700 font-semibold mb-2">{error}</p>
              <button
                onClick={fetchData}
                className="px-3 py-1.5 text-xs bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
              >
                Retry
              </button>
            </div>
          ) : activeTab === 'quality' && qualityData ? (
            <div className="space-y-6">
              {/* Overall Score Banner */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-5">
                  <div className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center border-2 font-black text-3xl shadow-sm ${getScoreColor(qualityData.overall_score)}`}>
                    {qualityData.overall_score}
                    <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">/ 100</span>
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">
                      Overall Document Grade
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {qualityData.overall_score >= 85
                        ? 'High-standard document ready for executive publication.'
                        : qualityData.overall_score >= 70
                        ? 'Solid document draft; applying targeted refinements will elevate its impact.'
                        : 'Draft requires structural expansion and stylistic polishing.'}
                    </p>
                    <span className="inline-block mt-2 text-[11px] font-mono text-slate-400">
                      Evaluated via: {qualityData.evaluation_engine} • Words: {qualityData.metrics?.word_count || 'N/A'}
                    </span>
                  </div>
                </div>

                {onTriggerImprove && (
                  <button
                    onClick={() => {
                      onClose();
                      onTriggerImprove('improve_professionalism');
                    }}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white shadow-xs transition-all shrink-0"
                  >
                    <ZapIcon className="w-3.5 h-3.5" />
                    Auto-Improve Writing
                  </button>
                )}
              </div>

              {/* Category Breakdown Bars */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
                  Category Score Breakdown
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {Object.entries(qualityData.category_scores).map(([category, score]) => (
                    <div key={category} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold capitalize text-slate-700">{category}</span>
                        <span className="font-bold text-slate-900">{score}%</span>
                      </div>
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getProgressColor(score)}`}
                          style={{ width: `${score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Strengths & Weaknesses */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1.5 mb-3">
                    <CheckCircleIcon className="w-4 h-4 text-emerald-600" />
                    Verified Strengths
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-700">
                    {qualityData.strengths.map((s, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-500 font-bold">•</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-amber-700 flex items-center gap-1.5 mb-3">
                    <AlertCircleIcon className="w-4 h-4 text-amber-600" />
                    Areas for Refinement
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-700">
                    {qualityData.weaknesses.map((w, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-amber-500 font-bold">•</span>
                        <span>{w}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Actionable Recommendations */}
              <div className="bg-indigo-50/60 p-5 rounded-2xl border border-indigo-200">
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-900 mb-2">
                  Actionable Recommendations
                </h4>
                <ul className="space-y-1.5 text-xs text-indigo-950">
                  {qualityData.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="font-bold text-indigo-600">{idx + 1}.</span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : activeTab === 'completeness' && completenessData ? (
            <div className="space-y-6">
              {/* Completeness Banner */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between gap-6">
                <div>
                  <h4 className="text-base font-bold text-slate-900">
                    Structural Completeness: {completenessData.completeness_percentage}%
                  </h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Evaluated against industry blueprint for <strong>{completenessData.detected_category}</strong>
                  </p>
                  <div className="flex items-center gap-3 mt-3 text-xs">
                    <span className="px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                      ✓ {completenessData.completed_count} Completed
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-amber-50 text-amber-700 font-semibold border border-amber-200">
                      ⚠ {completenessData.incomplete_count} Incomplete
                    </span>
                    <span className="px-2.5 py-1 rounded-md bg-rose-50 text-rose-700 font-semibold border border-rose-200">
                      ✕ {completenessData.missing_count} Missing
                    </span>
                  </div>
                </div>
                <div className={`w-20 h-20 rounded-2xl flex flex-col items-center justify-center border-2 font-black text-3xl shadow-sm ${getScoreColor(completenessData.completeness_percentage)}`}>
                  {completenessData.completeness_percentage}%
                </div>
              </div>

              {/* Sections Breakdown List */}
              <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
                  Expected Blueprint Sections
                </h4>
                <div className="space-y-3">
                  {/* Completed */}
                  {completenessData.completed_sections.map((sec, idx) => (
                    <div key={`comp-${idx}`} className="p-3 bg-emerald-50/50 border border-emerald-200 rounded-xl flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2.5">
                        <CheckCircleIcon className="w-4 h-4 text-emerald-600 shrink-0" />
                        <div>
                          <span className="font-bold text-slate-900">{sec.name}</span>
                          <span className="text-slate-400 text-[11px] block sm:inline sm:ml-2">
                            Matched: &ldquo;{sec.matched_heading}&rdquo; ({sec.word_count} words)
                          </span>
                        </div>
                      </div>
                      <span className="font-bold text-emerald-700 uppercase tracking-wider text-[10px]">Complete</span>
                    </div>
                  ))}

                  {/* Incomplete */}
                  {completenessData.incomplete_sections.map((sec, idx) => (
                    <div key={`incomp-${idx}`} className="p-3 bg-amber-50/50 border border-amber-200 rounded-xl flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2.5">
                        <AlertCircleIcon className="w-4 h-4 text-amber-600 shrink-0" />
                        <div>
                          <span className="font-bold text-slate-900">{sec.name}</span>
                          <span className="text-amber-700 text-[11px] block">{sec.suggestion}</span>
                        </div>
                      </div>
                      <span className="font-bold text-amber-700 uppercase tracking-wider text-[10px]">Incomplete</span>
                    </div>
                  ))}

                  {/* Missing */}
                  {completenessData.missing_sections.map((sec, idx) => (
                    <div key={`miss-${idx}`} className="p-3 bg-rose-50/50 border border-rose-200 rounded-xl flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2.5">
                        <XIcon className="w-4 h-4 text-rose-600 shrink-0" />
                        <div>
                          <span className="font-bold text-slate-900">{sec.name}</span>
                          <span className="text-rose-700 text-[11px] block">{sec.suggestion}</span>
                        </div>
                      </div>
                      <span className="font-bold text-rose-700 uppercase tracking-wider text-[10px]">Missing</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              {completenessData.recommendations.length > 0 && (
                <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
                    Structural Recommendations
                  </h4>
                  <ul className="space-y-1.5 text-xs text-slate-700">
                    {completenessData.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="font-bold text-indigo-600">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Objective Evaluation Rubric • Dynamic Blueprint Calibration</span>
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
