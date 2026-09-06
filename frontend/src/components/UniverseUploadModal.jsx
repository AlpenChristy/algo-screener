import React, { useState } from 'react';
import { X, UploadCloud, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { apiFetch } from '../lib/api';

export default function UniverseUploadModal({ onClose, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiFetch('/api/upload-universe', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }

      const data = await res.json();
      setSuccessMsg(`Successfully uploaded ${data.filename}`);
      setTimeout(() => {
        onUploadSuccess(data.filename);
        onClose();
      }, 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/50 backdrop-blur-xs">
      <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-2xl w-full max-w-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 rounded-xl">
              <UploadCloud className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white">Upload Stock Universe CSV</h3>
          </div>
          <button onClick={onClose} className="p-2 text-gray-400 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 rounded-full">
            <X className="w-4 h-4" />
          </button>
        </div>

        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
          Upload a CSV file containing a <code className="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/60 px-1 py-0.5 rounded">Symbol</code> column with stock tickers (e.g., RELIANCE, TCS, INFY).
        </p>

        {error && (
          <div className="mb-4 p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/40 text-rose-700 dark:text-rose-300 text-xs font-semibold rounded-xl flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="mb-4 p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/40 text-emerald-700 dark:text-emerald-300 text-xs font-semibold rounded-xl flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Drop Zone */}
        <label className="border-2 border-dashed border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 bg-gray-50 dark:bg-gray-800/50 p-6 rounded-2xl flex flex-col items-center justify-center cursor-pointer transition-colors mb-6">
          <FileText className="w-8 h-8 text-gray-400 dark:text-gray-500 mb-2" />
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">
            {file ? file.name : 'Click or drag CSV file here'}
          </span>
          <span className="text-xs text-gray-400 dark:text-gray-500 mt-1">Accepts .csv files</span>
          <input type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
        </label>

        <div className="flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2.5 text-xs font-semibold text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={uploading || !file}
            className="px-5 py-2.5 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-xs disabled:opacity-50 transition-all cursor-pointer"
          >
            {uploading ? 'Uploading...' : 'Upload Universe'}
          </button>
        </div>
      </div>
    </div>
  );
}
