import React from 'react';
import { Award, Target, ShieldAlert, Clock, FileSpreadsheet, FileText } from 'lucide-react';

export default function BacktestDashboard({ results, strategyType, onExport }) {
  if (!results) {
    return (
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-12 text-center shadow-sm">
        <div className="w-16 h-16 bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <Award className="w-8 h-8" />
        </div>
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Backtesting Engine Ready</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-6">
          Configure your historical window, stop-loss, target profit, and exit rules above, then click "Run Backtest".
        </p>
      </div>
    );
  }

  const { total_trades, win_rate, avg_return, best_trade, worst_trade, exit_reasons, trades } = results;

  return (
    <div className="space-y-6">
      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Win Rate */}
        <div className="bg-gradient-to-tr from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/20 border border-emerald-200/80 dark:border-emerald-800/40 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider">Win Rate</span>
          <h3 className="text-3xl font-black text-emerald-900 dark:text-emerald-300 mt-2">{win_rate}%</h3>
          <p className="text-xs text-emerald-700 dark:text-emerald-400 font-medium mt-1">{trades.filter(t => t.return_pct > 0).length} wins of {total_trades} trades</p>
        </div>

        {/* Avg Return */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/80 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Avg Return / Trade</span>
          <h3 className={`text-3xl font-black mt-2 ${avg_return >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}`}>
            {avg_return >= 0 ? `+${avg_return}%` : `${avg_return}%`}
          </h3>
          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mt-1">Simulated performance</p>
        </div>

        {/* Total Trades */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/80 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Trades</span>
          <h3 className="text-3xl font-black text-gray-900 dark:text-white mt-2">{total_trades}</h3>
          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mt-1">Across historical window</p>
        </div>

        {/* Best Trade */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/80 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Best Trade</span>
          <h3 className="text-3xl font-black text-emerald-600 dark:text-emerald-400 mt-2">+{best_trade}%</h3>
          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mt-1">Single highest gain</p>
        </div>

        {/* Worst Trade */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200/80 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Worst Trade</span>
          <h3 className="text-3xl font-black text-rose-600 dark:text-rose-400 mt-2">{worst_trade}%</h3>
          <p className="text-xs text-gray-400 dark:text-gray-500 font-medium mt-1">Maximum single loss</p>
        </div>
      </div>

      {/* Exit Reason Breakdown */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 p-6 shadow-sm">
        <h3 className="text-base font-bold text-gray-900 dark:text-white mb-4">Exit Trigger Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-800/40 p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-emerald-600 dark:bg-emerald-500 text-white rounded-lg">
                <Target className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-300 uppercase">Target Exit</span>
                <p className="text-lg font-black text-emerald-900 dark:text-emerald-200">{exit_reasons.target || 0} Trades</p>
              </div>
            </div>
            <span className="text-xs font-bold text-emerald-700 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-900/60 px-2 py-1 rounded-md">
              {total_trades > 0 ? Math.round(((exit_reasons.target || 0) / total_trades) * 100) : 0}%
            </span>
          </div>

          <div className="bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-800/40 p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-rose-600 dark:bg-rose-500 text-white rounded-lg">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold text-rose-800 dark:text-rose-300 uppercase">Stop Loss Exit</span>
                <p className="text-lg font-black text-rose-900 dark:text-rose-200">{exit_reasons.stop_loss || 0} Trades</p>
              </div>
            </div>
            <span className="text-xs font-bold text-rose-700 dark:text-rose-300 bg-rose-100 dark:bg-rose-900/60 px-2 py-1 rounded-md">
              {total_trades > 0 ? Math.round(((exit_reasons.stop_loss || 0) / total_trades) * 100) : 0}%
            </span>
          </div>

          <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 p-4 rounded-xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gray-600 dark:bg-gray-500 text-white rounded-lg">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Max Time Holding</span>
                <p className="text-lg font-black text-gray-900 dark:text-white">{exit_reasons.time_exit || 0} Trades</p>
              </div>
            </div>
            <span className="text-xs font-bold text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-md">
              {total_trades > 0 ? Math.round(((exit_reasons.time_exit || 0) / total_trades) * 100) : 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Trade-by-Trade Table */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-gray-900 dark:text-white">Trade Execution History Log</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">Detailed record of each simulated entry and exit</p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => onExport('excel', trades, 'Backtest_Results')}
              className="flex items-center space-x-1.5 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 border border-emerald-200 dark:border-emerald-800/40 font-semibold px-3 py-2 rounded-xl text-xs transition-all cursor-pointer"
            >
              <FileSpreadsheet className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Excel</span>
            </button>
            <button
              onClick={() => onExport('csv', trades, 'Backtest_Results')}
              className="flex items-center space-x-1.5 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/40 border border-blue-200 dark:border-blue-800/40 font-semibold px-3 py-2 rounded-xl text-xs transition-all cursor-pointer"
            >
              <FileText className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>CSV</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/60 text-gray-500 dark:text-gray-400 uppercase text-xs font-bold border-b border-gray-100 dark:border-gray-800 tracking-wider">
              <tr>
                <th className="px-5 py-4">Symbol</th>
                <th className="px-5 py-4">Entry Date</th>
                <th className="px-5 py-4">Entry Price</th>
                <th className="px-5 py-4">Exit Date</th>
                <th className="px-5 py-4">Exit Price</th>
                <th className="px-5 py-4">Days Held</th>
                <th className="px-5 py-4">Exit Reason</th>
                <th className="px-5 py-4 text-right">Return %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
              {trades.map((t, idx) => (
                <tr key={idx} className="hover:bg-gray-50/80 dark:hover:bg-gray-800/50 transition-colors">
                  <td className="px-5 py-4 font-bold text-gray-900 dark:text-white">{t.symbol}</td>
                  <td className="px-5 py-4 font-medium text-gray-600 dark:text-gray-300">{t.signal_date}</td>
                  <td className="px-5 py-4 font-semibold text-gray-800 dark:text-gray-200">₹{t.entry_price}</td>
                  <td className="px-5 py-4 font-medium text-gray-600 dark:text-gray-300">{t.exit_date}</td>
                  <td className="px-5 py-4 font-semibold text-gray-800 dark:text-gray-200">₹{t.exit_price}</td>
                  <td className="px-5 py-4 font-medium text-gray-700 dark:text-gray-300">{t.days_held} days</td>
                  <td className="px-5 py-4">
                    <span className={`px-2.5 py-1 rounded-md text-xs font-bold uppercase ${
                      t.exit_reason === 'target' ? 'bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300' :
                      t.exit_reason === 'stop_loss' ? 'bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                    }`}>
                      {t.exit_reason}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right font-black">
                    <span className={t.return_pct >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}>
                      {t.return_pct >= 0 ? `+${t.return_pct}%` : `${t.return_pct}%`}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
