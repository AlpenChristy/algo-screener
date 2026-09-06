import React from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';

export default function LiveProgressBar({ progress, currentSymbol, isComplete }) {
  if (!progress || progress.total === 0) return null;
  const pct = Math.round((progress.current / progress.total) * 100);

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm px-5 py-4 flex items-center gap-5">
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
        isComplete
          ? 'bg-green-100 dark:bg-green-950/60 text-green-600 dark:text-green-400'
          : 'bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400'
      }`}>
        {isComplete
          ? <CheckCircle2 className="w-4 h-4" />
          : <Loader2 className="w-4 h-4 animate-spin" />
        }
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <p className="text-[13px] font-semibold text-gray-800 dark:text-gray-200 truncate">
            {isComplete ? 'Scan complete' : `Scanning ${currentSymbol || '…'}`}
          </p>
          <span className={`text-[13px] font-bold ml-4 shrink-0 ${
            isComplete ? 'text-green-600 dark:text-green-400' : 'text-blue-600 dark:text-blue-400'
          }`}>
            {pct}%
          </span>
        </div>
        <div className="w-full h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-300 ${
              isComplete ? 'bg-green-500' : 'bg-blue-500'
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-1">{progress.current} / {progress.total} stocks processed</p>
      </div>
    </div>
  );
}
