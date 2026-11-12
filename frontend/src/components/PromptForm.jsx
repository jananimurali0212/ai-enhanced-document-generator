import React from 'react';
import { TONE_OPTIONS, LENGTH_OPTIONS } from '../data/templates';
import { FileUpload } from './FileUpload';
import { SparklesIcon, ArrowLeftIcon, ArrowRightIcon, RefreshCwIcon } from './Icons';

export const PromptForm = ({
  formData,
  setFormData,
  selectedTemplate,
  files,
  setFiles,
  onGenerate,
  onBack,
  isGenerating
}) => {
  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleApplySampleData = () => {
    if (selectedTemplate) {
      setFormData((prev) => ({
        ...prev,
        topic: selectedTemplate.sampleTopic || prev.topic,
        purpose: selectedTemplate.samplePurpose || prev.purpose,
        intendedAudience: selectedTemplate.sampleAudience || prev.intendedAudience,
        tone: selectedTemplate.defaultTone || prev.tone,
        desiredLength: selectedTemplate.defaultLength || prev.desiredLength,
      }));
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      {/* Top Header / Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <button
            onClick={onBack}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors mb-2"
          >
            <ArrowLeftIcon className="w-3.5 h-3.5" />
            Back to Templates
          </button>
          <h2 className="text-2xl font-bold text-slate-900">
            {selectedTemplate ? selectedTemplate.name : "Custom Document Configuration"}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Configure prompt parameters, grounding references, tone, and structural constraints.
          </p>
        </div>

        {selectedTemplate && (
          <button
            type="button"
            onClick={handleApplySampleData}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium bg-brand-50 text-brand-700 hover:bg-brand-100 border border-brand-200 transition-colors self-start sm:self-center"
          >
            <SparklesIcon className="w-3.5 h-3.5 text-brand-600" />
            Load Blueprint Defaults
          </button>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onGenerate();
        }}
        className="space-y-6"
      >
        {/* Core Input Fields */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider text-slate-700">
            1. Core Prompt Parameters
          </h3>

          {/* Topic Field */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label htmlFor="topic" className="block text-xs font-semibold text-slate-700">
                Document Topic / Subject <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] text-slate-400">
                {formData.topic.length}/150
              </span>
            </div>
            <input
              id="topic"
              type="text"
              required
              maxLength={150}
              value={formData.topic}
              onChange={(e) => handleChange('topic', e.target.value)}
              placeholder="e.g., Real-time Event Streaming Platform Architecture & Integration"
              className="block w-full px-4 py-2.5 text-sm rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all placeholder:text-slate-400 font-medium"
            />
          </div>

          {/* Purpose Field */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label htmlFor="purpose" className="block text-xs font-semibold text-slate-700">
                Primary Purpose & Key Goals <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] text-slate-400">What should this document achieve?</span>
            </div>
            <textarea
              id="purpose"
              required
              rows={3}
              value={formData.purpose}
              onChange={(e) => handleChange('purpose', e.target.value)}
              placeholder="e.g., Define microservices boundaries, data synchronization models, and disaster recovery SLA guarantees."
              className="block w-full px-4 py-2.5 text-sm rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all placeholder:text-slate-400"
            />
          </div>

          {/* Intended Audience */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label htmlFor="audience" className="block text-xs font-semibold text-slate-700">
                Intended Audience <span className="text-rose-500">*</span>
              </label>
              <span className="text-[11px] text-slate-400">Who is reviewing or reading?</span>
            </div>
            <input
              id="audience"
              type="text"
              required
              value={formData.intendedAudience}
              onChange={(e) => handleChange('intendedAudience', e.target.value)}
              placeholder="e.g., Principal Cloud Architects, VP of Engineering, SRE Incident Responders"
              className="block w-full px-4 py-2.5 text-sm rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Tone and Desired Length */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs space-y-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
            2. Stylistic & Structural Controls
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tone Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Document Tone
              </label>
              <div className="grid grid-cols-2 gap-2">
                {TONE_OPTIONS.map((t) => {
                  const isSelected = formData.tone === t.value;
                  return (
                    <button
                      key={t.value}
                      type="button"
                      onClick={() => handleChange('tone', t.value)}
                      className={`text-left p-3 rounded-xl border transition-all text-xs ${
                        isSelected
                          ? 'border-brand-500 bg-brand-50/70 text-brand-900 ring-1 ring-brand-500 font-semibold'
                          : 'border-slate-200 hover:border-slate-300 bg-white text-slate-700'
                      }`}
                    >
                      <div className="font-semibold">{t.label}</div>
                      <div className="text-[10px] text-slate-500 mt-0.5 line-clamp-1">{t.desc}</div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Desired Length Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-2">
                Target Length & Depth
              </label>
              <div className="space-y-2">
                {LENGTH_OPTIONS.map((l) => {
                  const isSelected = formData.desiredLength === l.value;
                  return (
                    <button
                      key={l.value}
                      type="button"
                      onClick={() => handleChange('desiredLength', l.value)}
                      className={`w-full flex items-center justify-between p-3 rounded-xl border transition-all text-xs ${
                        isSelected
                          ? 'border-brand-500 bg-brand-50/70 text-brand-900 ring-1 ring-brand-500 font-semibold'
                          : 'border-slate-200 hover:border-slate-300 bg-white text-slate-700'
                      }`}
                    >
                      <div className="text-left">
                        <span className="font-semibold block">{l.label}</span>
                        <span className="text-[10px] text-slate-500">{l.wordRange}</span>
                      </div>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                        isSelected ? 'bg-brand-200 text-brand-800' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {l.badge}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Additional Guidance / Rules */}
          <div>
            <label htmlFor="instructions" className="block text-xs font-semibold text-slate-700 mb-1.5">
              Specific Instructions or Constraints (Optional)
            </label>
            <textarea
              id="instructions"
              rows={2}
              value={formData.additionalInstructions}
              onChange={(e) => handleChange('additionalInstructions', e.target.value)}
              placeholder="e.g., Include an ASCII architecture diagram, mention SOC-2 compliance, avoid jargon in the summary section."
              className="block w-full px-4 py-2 text-xs rounded-xl border border-slate-300 bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Reference File Upload Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs">
          <FileUpload files={files} setFiles={setFiles} />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4">
          <button
            type="button"
            onClick={onBack}
            className="w-full sm:w-auto px-5 py-2.5 rounded-xl border border-slate-300 bg-white text-slate-700 font-semibold text-sm hover:bg-slate-50 transition-all text-center"
          >
            Cancel & Return
          </button>

          <button
            type="submit"
            disabled={isGenerating || !formData.topic || !formData.purpose || !formData.intendedAudience}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 font-bold text-white text-sm shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01]"
          >
            {isGenerating ? (
              <>
                <RefreshCwIcon className="w-4 h-4 animate-spin" />
                Synthesizing Document Shell...
              </>
            ) : (
              <>
                <SparklesIcon className="w-4 h-4" />
                Generate Document Shell
                <ArrowRightIcon className="w-4 h-4 ml-1" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
