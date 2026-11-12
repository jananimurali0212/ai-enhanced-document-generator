import React, { useState, useRef } from 'react';
import { UploadCloudIcon, TrashIcon, CheckIcon, FileTextIcon } from './Icons';

export const FileUpload = ({ files, setFiles }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const processFileList = (newFileList) => {
    const validExtensions = ['pdf', 'docx', 'doc', 'txt', 'md', 'csv', 'json'];
    const added = [];

    Array.from(newFileList).forEach((file) => {
      const ext = file.name.split('.').pop().toLowerCase();
      if (validExtensions.includes(ext) || file.type.includes('text') || file.type.includes('pdf')) {
        // Avoid duplicate filenames
        if (!files.some(f => f.name === file.name)) {
          added.push({
            id: `${file.name}-${Date.now()}`,
            name: file.name,
            size: file.size,
            type: ext.toUpperCase() || 'DOC',
            status: 'Ready',
            rawFile: file,
          });
        }
      }
    });

    if (added.length > 0) {
      setFiles((prev) => [...prev, ...added]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFileList(e.dataTransfer.files);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFileList(e.target.files);
    }
  };

  const handleRemoveFile = (fileId) => {
    setFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
          Reference Material Upload
        </label>
        <p className="text-xs text-slate-500">
          Upload existing documents, meeting notes, project briefs, or research papers to ground your output.
        </p>
      </div>

      {/* Drag & Drop Surface */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-brand-500 bg-brand-50/70 scale-[0.99]'
            : 'border-slate-300 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt,.md,.csv,.json"
          onChange={handleFileInputChange}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-2">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors ${
            isDragging ? 'bg-brand-500 text-white shadow-md' : 'bg-white text-slate-500 shadow-xs border border-slate-200'
          }`}>
            <UploadCloudIcon className="w-6 h-6" />
          </div>
          <div className="text-xs sm:text-sm">
            <span className="font-semibold text-brand-600 hover:text-brand-700">
              Click to browse
            </span>
            <span className="text-slate-600"> or drag and drop reference files</span>
          </div>
          <p className="text-[11px] text-slate-400">
            PDF, DOCX, Markdown (.md), Plain Text (.txt), CSV up to 25MB each
          </p>
        </div>
      </div>

      {/* Uploaded File List */}
      {files.length > 0 && (
        <div className="space-y-2 pt-2">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-600 px-1">
            <span>Attached Reference Documents ({files.length})</span>
            <button
              type="button"
              onClick={() => setFiles([])}
              className="text-rose-500 hover:text-rose-700 text-xs font-normal"
            >
              Clear all
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-2.5 rounded-xl bg-white border border-slate-200 shadow-xs hover:border-slate-300 transition-all"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200 uppercase shrink-0">
                    {file.type}
                  </span>
                  <div className="truncate">
                    <p className="text-xs font-medium text-slate-800 truncate" title={file.name}>
                      {file.name}
                    </p>
                    <p className="text-[10px] text-slate-400">
                      {formatFileSize(file.size)} • <span className="text-emerald-600 font-medium inline-flex items-center gap-0.5"><CheckIcon className="w-3 h-3 inline" /> {file.status}</span>
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRemoveFile(file.id);
                  }}
                  className="p-1 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors ml-2 shrink-0"
                  title="Remove file"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
