import React, { useEffect, useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function StockModal({ stock, strategyType, onClose }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!stock) return;
    setLoading(true);
    fetch(`/api/stock-history?symbol=${stock.symbol}&exchange_suffix=${stock.ticker.includes('.NS') ? '.NS' : ''}`)
      .then((res) => res.json())
      .then((data) => {
        setHistory(data.history || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [stock]);

  if (!stock) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-gray-900/50 backdrop-blur-xs">
      <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 flex items-center justify-center font-black text-xl">
              {stock.symbol.slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center space-x-3">
                <h2 className="text-2xl font-black text-gray-900 dark:text-white">{stock.symbol}</h2>
                <span className="text-xs font-semibold px-2.5 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-full">
                  {stock.ticker}
                </span>
                {stock.signal && (
                  <span className="text-xs font-bold px-3 py-1 bg-green-600 text-white rounded-full">
                    SIGNAL MATCH
                  </span>
                )}
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-medium">Historical Performance & Technical Benchmarks</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-gray-100 dark:bg-gray-800 rounded-full transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6">
          {/* Key Metrics Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-2xl border border-gray-100 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Close Price</span>
              <p className="text-xl font-black text-gray-900 dark:text-white mt-1">₹{stock.close?.toLocaleString()}</p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-2xl border border-gray-100 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                {strategyType === '52w-low' ? '52W Low' : '30-DMA'}
              </span>
              <p className="text-xl font-black text-gray-900 dark:text-white mt-1">
                ₹{(strategyType === '52w-low' ? stock['52w_low'] : stock['30_dma'])?.toLocaleString()}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-2xl border border-gray-100 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Distance %</span>
              <p className="text-xl font-black text-blue-600 dark:text-blue-400 mt-1">
                {strategyType === '52w-low' ? `+${stock.pct_above_52w_low}%` : `${stock.pct_from_30_dma}%`}
              </p>
            </div>
            <div className="bg-gray-50 dark:bg-gray-800/50 p-4 rounded-2xl border border-gray-100 dark:border-gray-800">
              <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Volume Multiple</span>
              <p className="text-xl font-black text-green-600 dark:text-green-400 mt-1">
                {stock.volume_multiple}x
              </p>
            </div>
          </div>

          {/* Chart Section */}
          <div className="bg-gray-50 dark:bg-gray-800/50 p-5 rounded-2xl border border-gray-200 dark:border-gray-800">
            <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200 mb-4 flex items-center justify-between">
              <span>6-Month Price Trend & Moving Average</span>
              <span className="text-xs font-normal text-gray-500 dark:text-gray-400">Daily Close vs Indicator</span>
            </h3>

            {loading ? (
              <div className="h-64 flex items-center justify-center text-gray-400">
                <Loader2 className="w-8 h-8 animate-spin text-green-500" />
              </div>
            ) : history.length === 0 ? (
              <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-500 font-medium">
                No historic chart data available for this stock.
              </div>
            ) : (
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={history}>
                    <defs>
                      <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} stroke="#9ca3af" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1f2937', borderRadius: '12px', borderColor: '#374151', color: '#f3f4f6' }}
                    />
                    <Area type="monotone" dataKey="close" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#colorClose)" name="Close Price" />
                    {strategyType === '30-dma' && (
                      <Area type="monotone" dataKey="dma30" stroke="#f59e0b" strokeWidth={2} fill="none" name="30-DMA" />
                    )}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
