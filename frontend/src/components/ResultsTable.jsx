import React, { useState, useMemo } from 'react';
import {
  Search, ArrowUpDown, Check, AlertTriangle,
  FileSpreadsheet, FileText, ExternalLink, ChevronUp, ChevronDown,
} from 'lucide-react';

// ─── Pill filter button ───────────────────────────────────────────────────
function Pill({ active, onClick, children, activeClass = 'bg-green-600 text-white' }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 text-[12px] font-semibold rounded-lg transition-all whitespace-nowrap ${
        active ? activeClass : 'text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60'
      }`}
    >
      {children}
    </button>
  );
}

// ─── Column header with sort ──────────────────────────────────────────────
function Th({ field, sortField, sortOrder, onSort, children, right }) {
  const active = sortField === field;
  return (
    <th
      onClick={() => onSort(field)}
      className={`px-4 py-3 text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer select-none whitespace-nowrap hover:text-gray-800 dark:hover:text-gray-200 transition-colors ${right ? 'text-right' : ''}`}
    >
      <span className="inline-flex items-center gap-1">
        {children}
        {active
          ? (sortOrder === 'asc' ? <ChevronUp className="w-3 h-3 text-green-600 dark:text-green-400" /> : <ChevronDown className="w-3 h-3 text-green-600 dark:text-green-400" />)
          : <ArrowUpDown className="w-3 h-3 text-gray-300 dark:text-gray-600" />
        }
      </span>
    </th>
  );
}

export default function ResultsTable({ data, strategyType, onExport, onSelectStock }) {
  const [search,     setSearch]     = useState('');
  const [filterMode, setFilterMode] = useState('signals');
  const [sortField,  setSortField]  = useState('volume_multiple');
  const [sortOrder,  setSortOrder]  = useState('desc');

  const handleSort = f => {
    if (sortField === f) setSortOrder(o => o === 'asc' ? 'desc' : 'asc');
    else { setSortField(f); setSortOrder('desc'); }
  };

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.filter(item => {
      const q = search.toLowerCase();
      const matchSearch = item.symbol?.toLowerCase().includes(q) || item.ticker?.toLowerCase().includes(q);
      if (!matchSearch) return false;
      if (filterMode === 'signals') return item.signal;
      if (filterMode === 'near') return strategyType === '52w-low' ? item.near_52w_low : item.near_30_dma;
      return true;
    });
  }, [data, search, filterMode, strategyType]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      let vA = a[sortField], vB = b[sortField];
      if (vA == null) return 1;
      if (vB == null) return -1;
      if (typeof vA === 'string') return sortOrder === 'asc' ? vA.localeCompare(vB) : vB.localeCompare(vA);
      return sortOrder === 'asc' ? vA - vB : vB - vA;
    });
  }, [filtered, sortField, sortOrder]);

  if (!data || data.length === 0) return null;

  const sigCount  = data.filter(d => d.signal).length;
  const nearCount = data.filter(d => strategyType === '52w-low' ? d.near_52w_low : d.near_30_dma).length;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm overflow-hidden">
      {/* ── Toolbar ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-5 py-4 border-b border-gray-100 dark:border-gray-800">
        {/* Filter pills */}
        <div className="flex items-center gap-1 bg-gray-100/80 dark:bg-gray-800/80 rounded-xl p-1">
          <Pill active={filterMode === 'signals'} onClick={() => setFilterMode('signals')} activeClass="bg-green-600 text-white shadow-xs">
            Signals · {sigCount}
          </Pill>
          <Pill active={filterMode === 'near'}    onClick={() => setFilterMode('near')}    activeClass="bg-amber-500 text-white shadow-xs">
            Near Level · {nearCount}
          </Pill>
          <Pill active={filterMode === 'all'}     onClick={() => setFilterMode('all')}     activeClass="bg-gray-800 dark:bg-gray-700 text-white shadow-xs">
            All · {data.length}
          </Pill>
        </div>

        {/* Search + export */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search symbol…"
              className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl pl-8 pr-3 py-2 text-[13px] text-gray-800 dark:text-gray-200 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/20 w-44 sm:w-56 transition-colors"
            />
          </div>
          <button
            onClick={() => onExport('excel', sorted)}
            className="flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 hover:bg-green-100 dark:hover:bg-green-900/40 border border-green-200 dark:border-green-800/40 rounded-xl transition-colors"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" /> Excel
          </button>
          <button
            onClick={() => onExport('csv', sorted)}
            className="flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 hover:bg-blue-100 dark:hover:bg-blue-900/40 border border-blue-200 dark:border-blue-800/40 rounded-xl transition-colors"
          >
            <FileText className="w-3.5 h-3.5" /> CSV
          </button>
        </div>
      </div>

      {/* ── Table ── */}
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-gray-50 dark:bg-gray-800/60 border-b border-gray-100 dark:border-gray-800">
            <tr>
              <Th field="symbol"         sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Symbol</Th>
              <Th field="close"          sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Close</Th>
              <Th
                field={strategyType === '52w-low' ? '52w_low' : '30_dma'}
                sortField={sortField} sortOrder={sortOrder} onSort={handleSort}
              >
                {strategyType === '52w-low' ? '52W Low' : '30-DMA'}
              </Th>
              <Th
                field={strategyType === '52w-low' ? 'pct_above_52w_low' : 'pct_from_30_dma'}
                sortField={sortField} sortOrder={sortOrder} onSort={handleSort}
              >
                Distance
              </Th>
              <Th field="volume_multiple" sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Vol ×</Th>
              {strategyType !== '52w-low' && (
                <Th field="delivery_pct" sortField={sortField} sortOrder={sortOrder} onSort={handleSort} right>Deliv%</Th>
              )}
              <th className="px-4 py-3 text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
              <th className="px-4 py-3 w-10" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
            {sorted.length === 0 ? (
              <tr>
                <td colSpan={strategyType !== '52w-low' ? 8 : 7} className="text-center py-12 text-[13px] text-gray-400 dark:text-gray-500">
                  No stocks match the selected filter.
                </td>
              </tr>
            ) : (
              sorted.map((item, idx) => {
                const isNear    = strategyType === '52w-low' ? item.near_52w_low : item.near_30_dma;
                const distPct   = strategyType === '52w-low' ? item.pct_above_52w_low : item.pct_from_30_dma;
                const benchVal  = strategyType === '52w-low' ? item['52w_low'] : item['30_dma'];

                return (
                  <tr
                    key={item.symbol ?? idx}
                    onClick={() => onSelectStock(item)}
                    className="hover:bg-gray-50/80 dark:hover:bg-gray-800/50 transition-colors cursor-pointer group"
                  >
                    {/* Symbol */}
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className="text-[13px] font-bold text-gray-900 dark:text-white">{item.symbol}</span>
                        <span className="text-[11px] text-gray-400 dark:text-gray-500 font-medium">{item.ticker}</span>
                      </div>
                    </td>

                    {/* Close */}
                    <td className="px-4 py-3.5 text-[13px] font-semibold text-gray-800 dark:text-gray-200">
                      ₹{item.close?.toLocaleString()}
                    </td>

                    {/* Benchmark */}
                    <td className="px-4 py-3.5 text-[13px] text-gray-500 dark:text-gray-400">
                      ₹{benchVal?.toLocaleString()}
                    </td>

                    {/* Distance */}
                    <td className="px-4 py-3.5">
                      <span className={`inline-block px-2 py-0.5 rounded-lg text-[12px] font-semibold ${
                        distPct != null && Math.abs(distPct) <= 2
                          ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400'
                          : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300'
                      }`}>
                        {distPct != null ? (distPct > 0 ? `+${distPct}%` : `${distPct}%`) : '—'}
                      </span>
                    </td>

                    {/* Vol multiple */}
                    <td className="px-4 py-3.5">
                      <span className={`inline-block px-2 py-0.5 rounded-lg text-[12px] font-semibold ${
                        item.volume_spike ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400' : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {item.volume_multiple ? `${item.volume_multiple}×` : '—'}
                      </span>
                    </td>

                    {/* Delivery % — 30-DMA only */}
                    {strategyType !== '52w-low' && (
                      <td className="px-4 py-3.5 text-right">
                        {item.delivery_pct != null ? (
                          <span className={`inline-block px-2 py-0.5 rounded-lg text-[12px] font-semibold ${
                            item.high_delivery
                              ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400'
                              : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'
                          }`}>
                            {item.delivery_pct}%
                          </span>
                        ) : (
                          <span className="text-[11px] text-gray-300 dark:text-gray-600">—</span>
                        )}
                      </td>
                    )}

                    {/* Status */}
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        {item.signal && (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-green-600 dark:bg-green-500 text-white">
                            <Check className="w-3 h-3" /> Signal
                          </span>
                        )}
                        {!item.signal && isNear && (
                          <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">Near</span>
                        )}
                        {!item.signal && item.volume_spike && (
                          <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-400">Vol Spike</span>
                        )}
                        {!item.signal && item.high_delivery && (
                          <span className="px-2 py-0.5 rounded-md text-[11px] font-semibold bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400">Hi Deliv</span>
                        )}
                        {!item.signal && !isNear && !item.volume_spike && !item.high_delivery && (
                          <span className="text-[11px] text-gray-300 dark:text-gray-600">—</span>
                        )}
                      </div>
                    </td>

                    {/* Chart link */}
                    <td className="px-4 py-3.5">
                      <button className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-lg">
                        <ExternalLink className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
