import React, { useState, useEffect, useMemo } from 'react';
import {
  Database, Search, RefreshCw, FileSpreadsheet, FileText,
  CheckCircle2, AlertTriangle, Calendar, ArrowUpDown,
  ChevronLeft, ChevronRight, Zap, Clock, TrendingUp,
  ChevronUp, ChevronDown,
} from 'lucide-react';
import { apiFetch } from '../lib/api';

// ─── Stat card ────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, iconBg, label, value, sub }) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm p-5 flex items-start justify-between gap-4">
      <div className="min-w-0">
        <p className="text-[11px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-1">{label}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white leading-none">{value}</p>
        {sub && <p className="text-[12px] text-gray-400 dark:text-gray-500 mt-1.5">{sub}</p>}
      </div>
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${iconBg}`}>
        <Icon className="w-5 h-5" />
      </div>
    </div>
  );
}

// ─── Sort-able column header ──────────────────────────────────────────────
function Th({ field, sortField, sortOrder, onSort, children }) {
  const active = sortField === field;
  return (
    <th
      onClick={() => onSort(field)}
      className="px-4 py-3 text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:text-gray-800 dark:hover:text-gray-200 transition-colors whitespace-nowrap"
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

// ─── Filter pill ──────────────────────────────────────────────────────────
function Pill({ active, onClick, children, activeClass }) {
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

export default function HistoryDashboard({ strategyType, onSelectStock, onExport }) {
  const [records,       setRecords]       = useState([]);
  const [total,         setTotal]         = useState(0);
  const [stats,         setStats]         = useState({ total_records: 0, total_signals: 0, total_close_calls: 0, today_signals: 0, today_close_calls: 0 });
  const [filterStrat,   setFilterStrat]   = useState('all');
  const [filterStatus,  setFilterStatus]  = useState('all');
  const [search,        setSearch]        = useState('');
  const [isLoading,     setIsLoading]     = useState(false);
  const [page,          setPage]          = useState(1);
  const [sortField,     setSortField]     = useState('record_date');
  const [sortOrder,     setSortOrder]     = useState('desc');
  const LIMIT = 25;

  const fetchStats = () => {
    apiFetch('/api/history/stats').then(r => r.json()).then(setStats).catch(console.error);
  };

  const fetchRecords = () => {
    setIsLoading(true);
    const q = new URLSearchParams({ limit: LIMIT, offset: (page - 1) * LIMIT });
    if (filterStrat  !== 'all') q.append('strategy_type', filterStrat);
    if (filterStatus !== 'all') q.append('status', filterStatus);
    if (search.trim())          q.append('symbol', search.trim());

    fetch(`/api/history?${q}`)
      .then(r => r.json())
      .then(d => { setRecords(d.records ?? []); setTotal(d.total ?? 0); })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => { fetchStats(); }, []);
  useEffect(() => { fetchRecords(); }, [filterStrat, filterStatus, search, page]);

  const handleSort = f => {
    if (sortField === f) setSortOrder(o => o === 'asc' ? 'desc' : 'asc');
    else { setSortField(f); setSortOrder('desc'); }
  };

  const sorted = useMemo(() => {
    return [...records].sort((a, b) => {
      let va = a[sortField], vb = b[sortField];
      if (va == null) return 1;
      if (vb == null) return -1;
      if (typeof va === 'string') return sortOrder === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
      return sortOrder === 'asc' ? va - vb : vb - va;
    });
  }, [records, sortField, sortOrder]);

  const totalPages = Math.max(1, Math.ceil(total / LIMIT));
  const todayStr   = new Date().toISOString().split('T')[0];

  return (
    <div className="space-y-5">
      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Zap}         iconBg="bg-green-100 dark:bg-green-950/60 text-green-600 dark:text-green-400"  label="Signals Logged"    value={stats.total_signals}     sub="All-time signal matches" />
        <StatCard icon={AlertTriangle} iconBg="bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400" label="Close Calls"       value={stats.total_close_calls} sub="Near level or vol spike" />
        <StatCard icon={Clock}        iconBg="bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400"   label="Today's Signals"   value={stats.today_signals}     sub={`+ ${stats.today_close_calls} close calls`} />
        <StatCard icon={Database}     iconBg="bg-purple-100 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400" label="Database"         value="Supabase"                sub="Auto-deduplicated daily" />
      </div>

      {/* Main table card */}
      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm overflow-hidden">
        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-5 py-4 border-b border-gray-100 dark:border-gray-800 bg-gray-50/40 dark:bg-gray-800/30">
          {/* Left: filters */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-0.5 bg-gray-100/80 dark:bg-gray-800/80 rounded-xl p-1">
              <Pill active={filterStrat==='all'}     onClick={() => { setFilterStrat('all'); setPage(1); }}     activeClass="bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs">All</Pill>
              <Pill active={filterStrat==='52w-low'} onClick={() => { setFilterStrat('52w-low'); setPage(1); }} activeClass="bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs">52W Low</Pill>
              <Pill active={filterStrat==='30-dma'}  onClick={() => { setFilterStrat('30-dma'); setPage(1); }}  activeClass="bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-xs">30-DMA</Pill>
            </div>
            <div className="flex items-center gap-0.5 bg-gray-100/80 dark:bg-gray-800/80 rounded-xl p-1">
              <Pill active={filterStatus==='all'}        onClick={() => { setFilterStatus('all'); setPage(1); }}        activeClass="bg-gray-800 dark:bg-gray-700 text-white shadow-xs">All</Pill>
              <Pill active={filterStatus==='SIGNAL'}     onClick={() => { setFilterStatus('SIGNAL'); setPage(1); }}     activeClass="bg-green-600 dark:bg-green-500 text-white shadow-xs">Signal</Pill>
              <Pill active={filterStatus==='CLOSE_CALL'} onClick={() => { setFilterStatus('CLOSE_CALL'); setPage(1); }} activeClass="bg-amber-500 dark:bg-amber-600 text-white shadow-xs">Close Call</Pill>
            </div>
          </div>

          {/* Right: search + refresh + export */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                value={search}
                onChange={e => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search ticker…"
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl pl-8 pr-3 py-2 text-[13px] text-gray-800 dark:text-gray-200 placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/20 w-40 sm:w-52 transition-colors"
              />
            </div>
            <button
              onClick={() => { fetchStats(); fetchRecords(); }}
              className="p-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 rounded-xl transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-green-600 dark:text-green-400' : ''}`} />
            </button>
            <button
              onClick={() => onExport('excel', sorted, 'Signal_History')}
              className="flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/40 hover:bg-green-100 dark:hover:bg-green-900/40 border border-green-200 dark:border-green-800/40 rounded-xl transition-colors"
            >
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Excel</span>
            </button>
            <button
              onClick={() => onExport('csv', sorted, 'Signal_History')}
              className="flex items-center gap-1.5 px-3 py-2 text-[12px] font-semibold text-blue-700 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 hover:bg-blue-100 dark:hover:bg-blue-900/40 border border-blue-200 dark:border-blue-800/40 rounded-xl transition-colors"
            >
              <FileText className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">CSV</span>
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-gray-50 dark:bg-gray-800/60 border-b border-gray-100 dark:border-gray-800">
              <tr>
                <Th field="record_date"    sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Date</Th>
                <Th field="symbol"         sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Symbol</Th>
                <Th field="strategy_type"  sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Strategy</Th>
                <Th field="status"         sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Status</Th>
                <Th field="close_price"    sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Close</Th>
                <Th field="benchmark_value" sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Benchmark</Th>
                <Th field="distance_pct"   sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Distance</Th>
                <Th field="volume_multiple" sortField={sortField} sortOrder={sortOrder} onSort={handleSort}>Vol ×</Th>
                <th className="px-4 py-3 text-[11px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">Scanned</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
              {isLoading ? (
                <tr>
                  <td colSpan="9" className="text-center py-12">
                    <div className="flex items-center justify-center gap-2 text-[13px] text-gray-400 dark:text-gray-500">
                      <RefreshCw className="w-4 h-4 animate-spin text-green-500" />
                      Loading from Supabase…
                    </div>
                  </td>
                </tr>
              ) : sorted.length === 0 ? (
                <tr>
                  <td colSpan="9" className="text-center py-12 text-[13px] text-gray-400 dark:text-gray-500">
                    No records found for the selected criteria.
                  </td>
                </tr>
              ) : (
                sorted.map((item, idx) => {
                  const isSignal = item.status === 'SIGNAL';
                  const isToday  = item.record_date === todayStr;
                  const scanTime = item.scan_time
                    ? new Date(item.scan_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                    : '';

                  return (
                    <tr
                      key={item.id ?? idx}
                      onClick={() => onSelectStock?.({ symbol: item.symbol, ticker: item.ticker, close: item.close_price })}
                      className="hover:bg-gray-50/80 dark:hover:bg-gray-800/50 transition-colors cursor-pointer group"
                    >
                      {/* Date */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <span className="text-[13px] font-medium text-gray-700 dark:text-gray-300">{item.record_date}</span>
                          {isToday && (
                            <span className="px-1.5 py-0.5 text-[10px] font-bold bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 rounded-md">Today</span>
                          )}
                        </div>
                      </td>

                      {/* Symbol */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-2">
                          <span className="text-[13px] font-bold text-gray-900 dark:text-white">{item.symbol}</span>
                          <span className="text-[11px] text-gray-400 dark:text-gray-500">{item.ticker}</span>
                        </div>
                      </td>

                      {/* Strategy */}
                      <td className="px-4 py-3.5">
                        <span className="px-2 py-0.5 text-[11px] font-semibold rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300">
                          {item.strategy_type === '52w-low' ? '52W Low' : '30-DMA'}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="px-4 py-3.5">
                        {isSignal ? (
                          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-green-600 dark:bg-green-500 text-white">
                            <CheckCircle2 className="w-3 h-3" /> Signal
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-semibold bg-amber-100 dark:bg-amber-950/60 text-amber-700 dark:text-amber-400">
                            <AlertTriangle className="w-3 h-3" /> Close Call
                          </span>
                        )}
                      </td>

                      {/* Close */}
                      <td className="px-4 py-3.5 text-[13px] font-semibold text-gray-800 dark:text-gray-200">
                        {item.close_price != null ? `₹${item.close_price.toLocaleString()}` : '—'}
                      </td>

                      {/* Benchmark */}
                      <td className="px-4 py-3.5 text-[13px] text-gray-500 dark:text-gray-400">
                        {item.benchmark_value != null ? `₹${item.benchmark_value.toLocaleString()}` : '—'}
                      </td>

                      {/* Distance */}
                      <td className="px-4 py-3.5">
                        <span className={`inline-block px-2 py-0.5 rounded-lg text-[12px] font-semibold ${
                          item.distance_pct != null && Math.abs(item.distance_pct) <= 2
                            ? 'bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300'
                        }`}>
                          {item.distance_pct != null
                            ? item.distance_pct > 0 ? `+${item.distance_pct}%` : `${item.distance_pct}%`
                            : '—'}
                        </span>
                      </td>

                      {/* Vol multiple */}
                      <td className="px-4 py-3.5">
                        <span className={`inline-block px-2 py-0.5 rounded-lg text-[12px] font-semibold ${
                          item.is_vol_spike ? 'bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400' : 'text-gray-400 dark:text-gray-500'
                        }`}>
                          {item.volume_multiple != null ? `${item.volume_multiple}×` : '—'}
                        </span>
                      </td>

                      {/* Scan time */}
                      <td className="px-4 py-3.5 text-right text-[12px] text-gray-400 dark:text-gray-500">{scanTime}</td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination footer */}
        <div className="flex items-center justify-between px-5 py-3.5 border-t border-gray-100 dark:border-gray-800 bg-gray-50/40 dark:bg-gray-800/30">
          <p className="text-[12px] text-gray-400 dark:text-gray-500">
            Showing <span className="font-semibold text-gray-700 dark:text-gray-300">{records.length}</span> of{' '}
            <span className="font-semibold text-gray-700 dark:text-gray-300">{total}</span> records
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-2 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:pointer-events-none transition-colors bg-white dark:bg-gray-800"
            >
              <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </button>
            <span className="text-[12px] font-semibold text-gray-700 dark:text-gray-300 min-w-[80px] text-center">
              Page {page} / {totalPages}
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-2 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-30 disabled:pointer-events-none transition-colors bg-white dark:bg-gray-800"
            >
              <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-300" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
