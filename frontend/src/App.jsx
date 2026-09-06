import React, { useState, useEffect, useRef } from 'react';
import Sidebar, { SIDEBAR_EXPANDED, SIDEBAR_COLLAPSED } from './components/Sidebar';
import ControlPanel, { STRATEGIES } from './components/ControlPanel';
import LiveProgressBar from './components/LiveProgressBar';
import KpiCards from './components/KpiCards';
import ResultsTable from './components/ResultsTable';
import BacktestDashboard from './components/BacktestDashboard';
import HistoryDashboard from './components/HistoryDashboard';
import StockModal from './components/StockModal';
import UniverseUploadModal from './components/UniverseUploadModal';
import ThemeToggle from './components/ThemeToggle';
import { Menu } from 'lucide-react';
import { apiFetch, apiUrl } from './lib/api';

const TAB_META = {
  screener: { title: 'Live Screener',  sub: 'Real-time market scanner'       },
  backtest: { title: 'Backtester',     sub: 'Historical strategy simulation'  },
  history:  { title: 'Signal History', sub: 'Supabase-backed daily record'    },
};

export default function App() {
  // ── Theme State ───────────────────────────────────────────────────────────
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  // ── Sidebar state (lifted here so main content can respond) ──────────────
  const [collapsed,       setCollapsed]       = useState(false);
  const [mobileOpen,      setMobileOpen]      = useState(false);

  // ── App state ─────────────────────────────────────────────────────────────
  const [activeTab,       setActiveTab]       = useState('screener');
  const [strategyType,    setStrategyType]    = useState('52w-low');
  const [universes,       setUniverses]       = useState([]);
  const [selectedUniverse,setSelectedUniverse]= useState('nifty100.csv');

  const [params, setParams] = useState({
    near_low_pct: 2.0, near_dma_pct: 2.0,
    min_mult: 3.0, max_mult: 4.0,
    exchange_suffix: '.NS', delay: 0.1,
    backtest_days: 60, stop_loss_pct: 5.0,
    target_pct: 10.0, max_holding_days: 20,
  });

  const [isScanning,      setIsScanning]      = useState(false);
  const [isComplete,      setIsComplete]      = useState(false);
  const [progress,        setProgress]        = useState({ current: 0, total: 0 });
  const [currentSymbol,   setCurrentSymbol]   = useState('');
  const [screenerResults, setScreenerResults] = useState([]);
  const [backtestResults, setBacktestResults] = useState(null);
  const [selectedStock,   setSelectedStock]   = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const wsRef = useRef(null);

  const fetchUniverses = () => {
    apiFetch('/api/universes')
      .then(r => r.json())
      .then(data => {
        setUniverses(data);
        if (data.length > 0 && !selectedUniverse) setSelectedUniverse(data[0].filename);
      })
      .catch(console.error);
  };
  useEffect(() => { fetchUniverses(); }, []);

  const handleRunScreener = () => {
    if (isScanning) return;
    setIsScanning(true); setIsComplete(false);
    setProgress({ current: 0, total: 0 }); setScreenerResults([]); setCurrentSymbol('');

    // Use SSE — works reliably through Render + Cloudflare proxies (unlike WebSocket)
    const paramsJson = JSON.stringify(params);
    const url = apiUrl(
      `/api/screener/stream?strategy_type=${encodeURIComponent(strategyType)}` +
      `&universe_name=${encodeURIComponent(selectedUniverse)}` +
      `&params_json=${encodeURIComponent(paramsJson)}`
    );

    const es = new EventSource(url);
    wsRef.current = { close: () => es.close() }; // uniform cleanup interface

    es.onmessage = e => {
      const d = JSON.parse(e.data);
      if (d.type === 'progress') {
        setProgress({ current: d.current, total: d.total });
        setCurrentSymbol(d.symbol);
        if (d.result) setScreenerResults(p => [...p, d.result]);
      } else if (d.type === 'complete') {
        setIsScanning(false); setIsComplete(true);
        if (d.results) setScreenerResults(d.results);
        es.close();
      } else if (d.type === 'error') {
        setIsScanning(false); es.close();
      }
    };
    es.onerror = () => { setIsScanning(false); es.close(); };
  };

  const handleRunBacktest = () => {
    setIsScanning(true);
    apiFetch('/api/run-backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ strategy_type: strategyType, universe_name: selectedUniverse, params }),
    })
      .then(r => r.json())
      .then(d => { setBacktestResults(d); setIsScanning(false); })
      .catch(() => setIsScanning(false));
  };

  const handleExport = (format, data, title = 'Screener_Results') => {
    apiFetch('/api/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ format, data, title }),
    })
      .then(r => r.blob())
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = Object.assign(document.createElement('a'), {
          href: url,
          download: `${title}_${strategyType}.${format === 'excel' ? 'xlsx' : 'csv'}`,
        });
        document.body.appendChild(a); a.click(); a.remove();
      });
  };

  // ── Derived ────────────────────────────────────────────────────────────────
  const stratLabel = STRATEGIES.find(s => s.id === strategyType)?.short ?? strategyType;
  const meta       = TAB_META[activeTab];
  const sidebarW   = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;

  return (
    <div className="min-h-screen bg-[#f0f2f5] dark:bg-[#0b0f19] text-gray-900 dark:text-gray-100 flex transition-colors duration-200">
      {/* ── Sidebar (fixed position) ── */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
      />

      {/* ── Spacer div (desktop only) ── */}
      <div
        className="hidden lg:block shrink-0 transition-[width] duration-200"
        style={{ width: sidebarW }}
      />

      {/* ── Main content ── */}
      <div className="flex-1 flex flex-col min-w-0 max-w-full">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-[60px] bg-white dark:bg-gray-900 border-b border-gray-200/80 dark:border-gray-800 flex items-center gap-3 px-4 sm:px-5 transition-colors duration-200">
          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden flex items-center justify-center w-9 h-9 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Page title */}
          <div className="flex-1 min-w-0 flex items-center gap-3">
            <h1 className="text-[15px] font-bold text-gray-900 dark:text-white truncate">{meta.title}</h1>
            <span className="hidden sm:block text-[12px] text-gray-400 dark:text-gray-500 truncate">{meta.sub}</span>
          </div>

          {/* Strategy badge */}
          {activeTab !== 'history' && (
            <span className="hidden sm:inline-flex items-center px-2.5 py-1.5 rounded-lg bg-green-50 dark:bg-green-950/40 border border-green-100 dark:border-green-800/40 text-green-700 dark:text-green-400 text-[12px] font-semibold shrink-0">
              {stratLabel}
            </span>
          )}

          {/* Dark / Light Mode Toggle Button */}
          <ThemeToggle theme={theme} setTheme={setTheme} />
        </header>

        {/* Page body */}
        <main className="flex-1 p-4 sm:p-5 lg:p-6 space-y-4 sm:space-y-5">
          {activeTab !== 'history' && (
            <ControlPanel
              strategyType={strategyType}
              setStrategyType={setStrategyType}
              universes={universes}
              selectedUniverse={selectedUniverse}
              setSelectedUniverse={setSelectedUniverse}
              params={params}
              setParams={setParams}
              onRunScreener={handleRunScreener}
              onRunBacktest={handleRunBacktest}
              isScanning={isScanning}
              activeTab={activeTab}
              onOpenUploadModal={() => setUploadModalOpen(true)}
            />
          )}

          {activeTab === 'screener' && (
            <>
              <LiveProgressBar progress={progress} currentSymbol={currentSymbol} isComplete={isComplete} />
              <KpiCards data={screenerResults} strategyType={strategyType} />
              <ResultsTable
                data={screenerResults}
                strategyType={strategyType}
                onExport={handleExport}
                onSelectStock={setSelectedStock}
              />
            </>
          )}

          {activeTab === 'backtest' && (
            <BacktestDashboard results={backtestResults} strategyType={strategyType} onExport={handleExport} />
          )}

          {activeTab === 'history' && (
            <HistoryDashboard strategyType={strategyType} onSelectStock={setSelectedStock} onExport={handleExport} />
          )}
        </main>
      </div>

      {/* Modals */}
      {selectedStock && (
        <StockModal stock={selectedStock} strategyType={strategyType} onClose={() => setSelectedStock(null)} />
      )}
      {uploadModalOpen && (
        <UniverseUploadModal
          onClose={() => setUploadModalOpen(false)}
          onUploadSuccess={filename => { fetchUniverses(); setSelectedUniverse(filename); }}
        />
      )}
    </div>
  );
}
