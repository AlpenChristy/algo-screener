import React from 'react';
import { TrendingUp, BarChart2, Zap, Layers, PlayCircle, History } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, strategyType, setStrategyType }) {
  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold text-slate-900 tracking-tight">AlgoScreener Pro</h1>
                <span className="px-2 py-0.5 text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 rounded-full">
                  v2.0
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Algorithmic Trading & Stock Screening Platform</p>
            </div>
          </div>

          {/* Strategy & View Tabs */}
          <div className="flex items-center space-x-2">
            {/* View Mode Toggle */}
            <div className="bg-slate-100 p-1 rounded-xl flex items-center border border-slate-200">
              <button
                onClick={() => setActiveTab('screener')}
                className={`flex items-center space-x-2 px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                  activeTab === 'screener'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <PlayCircle className="w-4 h-4" />
                <span>Live Screener</span>
              </button>
              <button
                onClick={() => setActiveTab('backtest')}
                className={`flex items-center space-x-2 px-4 py-2 text-sm font-semibold rounded-lg transition-all ${
                  activeTab === 'backtest'
                    ? 'bg-white text-blue-600 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                }`}
              >
                <History className="w-4 h-4" />
                <span>Backtester</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
