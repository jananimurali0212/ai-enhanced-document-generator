import React from 'react';
import { SparklesIcon, FileTextIcon, SlidersIcon, Edit3Icon, FolderIcon } from './Icons';

export const Header = ({ currentStep, setStep, selectedTemplate, onOpenHistory }) => {
  const steps = [
    { id: 1, name: 'Templates', icon: FileTextIcon },
    { id: 2, name: 'Prompt & Inputs', icon: SlidersIcon },
    { id: 3, name: 'Document Editor', icon: Edit3Icon },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Product Title */}
          <div 
            onClick={() => setStep(1)} 
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
              <SparklesIcon className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg tracking-tight text-slate-900 group-hover:text-brand-600 transition-colors">
                  DocuGen <span className="text-brand-600">AI</span>
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-brand-50 text-brand-700 border border-brand-200">
                  Day 3 Ready
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                AI Generation • Supabase Persistence • PDF & DOCX Export
              </p>
            </div>
          </div>

          {/* Stepper Navigation */}
          <nav className="flex items-center gap-1 sm:gap-2">
            {steps.map((step) => {
              const isActive = currentStep === step.id;
              const isPassed = currentStep > step.id;

              return (
                <button
                  key={step.id}
                  onClick={() => setStep(step.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-brand-50 text-brand-700 ring-1 ring-brand-300 font-semibold shadow-xs'
                      : isPassed
                      ? 'text-slate-700 hover:bg-slate-100'
                      : 'text-slate-400 hover:text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                      isActive
                        ? 'bg-brand-600 text-white'
                        : isPassed
                        ? 'bg-slate-200 text-slate-700'
                        : 'bg-slate-100 text-slate-400'
                    }`}
                  >
                    {step.id}
                  </span>
                  <span className="hidden md:inline">{step.name}</span>
                </button>
              );
            })}
          </nav>

          {/* Action & Status Indicator */}
          <div className="flex items-center gap-2 sm:gap-3">
            {onOpenHistory && (
              <button
                type="button"
                onClick={onOpenHistory}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 transition-colors shadow-2xs"
                title="View saved documents history"
              >
                <FolderIcon className="w-4 h-4 text-brand-600" />
                <span className="hidden sm:inline">History</span>
              </button>
            )}

            {selectedTemplate && (
              <span className="hidden lg:inline-flex items-center gap-1.5 text-xs text-slate-600 bg-slate-100 px-2.5 py-1 rounded-md border border-slate-200">
                <span className="w-2 h-2 rounded-full bg-brand-500 animate-ping"></span>
                <span className="font-medium text-slate-800 truncate max-w-[120px]">
                  {selectedTemplate.name}
                </span>
              </span>
            )}
            
            <div className="hidden sm:flex items-center gap-1.5 text-xs font-medium text-slate-600 bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-md">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Backend Active
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
