import React from 'react';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle({ theme, setTheme, variant = 'button' }) {
  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  if (variant === 'segmented') {
    return (
      <div className="inline-flex items-center p-1 bg-gray-100 dark:bg-gray-800/80 rounded-xl border border-gray-200/80 dark:border-gray-700/80">
        <button
          type="button"
          onClick={() => setTheme('light')}
          className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            theme === 'light'
              ? 'bg-white text-amber-600 shadow-sm'
              : 'text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
          title="Light Mode"
        >
          <Sun className="w-3.5 h-3.5 text-amber-500" />
          <span className="hidden sm:inline">Light</span>
        </button>
        <button
          type="button"
          onClick={() => setTheme('dark')}
          className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
            theme === 'dark'
              ? 'bg-gray-900 text-indigo-400 shadow-sm'
              : 'text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
          title="Dark Mode"
        >
          <Moon className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden sm:inline">Dark</span>
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="p-2 rounded-xl text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white bg-gray-100/80 dark:bg-gray-800/80 hover:bg-gray-200/80 dark:hover:bg-gray-700/80 border border-gray-200/80 dark:border-gray-700/80 transition-all flex items-center justify-center shrink-0"
      title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
      aria-label="Toggle dark/light theme"
    >
      {theme === 'dark' ? (
        <Sun className="w-4 h-4 text-amber-400 transition-transform duration-200 hover:rotate-45" />
      ) : (
        <Moon className="w-4 h-4 text-slate-600 transition-transform duration-200 hover:-rotate-12" />
      )}
    </button>
  );
}
