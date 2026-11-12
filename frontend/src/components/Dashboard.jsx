import React, { useState, useMemo } from 'react';
import { DOCUMENT_CATEGORIES, TEMPLATES } from '../data/templates';
import { TemplateIconMap, SearchIcon, SparklesIcon, ArrowRightIcon, FileTextIcon } from './Icons';

export const Dashboard = ({ onSelectTemplate, onSelectCustom }) => {
  const [selectedCategory, setSelectedCategory] = useState("All Templates");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredTemplates = useMemo(() => {
    return TEMPLATES.filter((tpl) => {
      const matchesCategory =
        selectedCategory === "All Templates" || tpl.category === selectedCategory;
      const matchesSearch =
        tpl.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tpl.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        tpl.category.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCategory && matchesSearch;
    });
  }, [selectedCategory, searchQuery]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-brand-950 to-indigo-950 text-white p-8 sm:p-10 shadow-xl border border-slate-800">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 rounded-full bg-brand-500/10 blur-3xl pointer-events-none"></div>
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-brand-500/20 text-brand-300 border border-brand-400/30 mb-4">
            <SparklesIcon className="w-3.5 h-3.5" />
            Day 1 Architecture & UI Shell
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-3 leading-tight">
            Generate Grounded, High-Impact Documents in Seconds
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
            Choose a standardized document category template below or start with a custom prompt. 
            Ground your outputs with reference collateral, customize tone and length, and refine in the built-in document editor.
          </p>
          <div className="flex flex-wrap gap-4 items-center">
            <button
              onClick={onSelectCustom}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 font-semibold text-white text-sm shadow-lg shadow-brand-500/30 transition-all hover:scale-[1.02]"
            >
              <FileTextIcon className="w-4 h-4" />
              Start Blank Custom Document
            </button>
            <span className="text-xs text-slate-400">
              Supports 6 enterprise document types + dynamic file uploads
            </span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Supported Document Categories</h2>
            <p className="text-xs sm:text-sm text-slate-500">
              Select a specialized blueprint to auto-populate prompt parameters and guidelines.
            </p>
          </div>
          {/* Search Box */}
          <div className="relative w-full sm:w-72">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <SearchIcon className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter templates..."
              className="block w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-slate-300 bg-white shadow-xs focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
          {DOCUMENT_CATEGORIES.map((cat) => {
            const isSelected = selectedCategory === cat;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs sm:text-sm font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? "bg-slate-900 text-white shadow-sm"
                    : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
                }`}
              >
                {cat}
              </button>
            );
          })}
        </div>
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((tpl) => {
          const IconComponent = TemplateIconMap[tpl.icon] || FileTextIcon;
          return (
            <div
              key={tpl.id}
              onClick={() => onSelectTemplate(tpl)}
              className="group relative flex flex-col justify-between bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-xl hover:border-brand-300 transition-all cursor-pointer hover:-translate-y-1"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-tr ${tpl.color} flex items-center justify-center text-white shadow-md group-hover:scale-110 transition-transform`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <span className="text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200">
                    {tpl.badge}
                  </span>
                </div>
                
                <span className="text-xs font-medium text-brand-600 block mb-1">
                  {tpl.category}
                </span>
                
                <h3 className="text-base font-bold text-slate-900 group-hover:text-brand-600 transition-colors mb-2">
                  {tpl.name}
                </h3>
                
                <p className="text-xs sm:text-sm text-slate-600 line-clamp-3 leading-relaxed mb-4">
                  {tpl.description}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-100 mt-2 flex items-center justify-between text-xs text-slate-500">
                <div className="flex items-center gap-2">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-slate-400"></span>
                  <span>Tone: <strong className="text-slate-700 font-semibold">{tpl.defaultTone}</strong></span>
                </div>
                <div className="flex items-center gap-1 font-semibold text-brand-600 group-hover:translate-x-1 transition-transform">
                  <span>Use Blueprint</span>
                  <ArrowRightIcon className="w-3.5 h-3.5" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Blank Document Card Alternative */}
      <div className="p-6 rounded-2xl border-2 border-dashed border-slate-300 bg-slate-50/60 hover:bg-slate-50 transition-colors flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-slate-200 flex items-center justify-center text-slate-600">
            <SparklesIcon className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900">Need something specific or outside these categories?</h4>
            <p className="text-xs text-slate-500">
              Open the full prompt form directly with blank inputs and upload any bespoke reference guides.
            </p>
          </div>
        </div>
        <button
          onClick={onSelectCustom}
          className="px-4 py-2 text-xs font-semibold rounded-xl bg-white text-slate-700 border border-slate-300 hover:bg-slate-100 transition-all shadow-xs shrink-0"
        >
          Create Custom Document
        </button>
      </div>
    </div>
  );
};
