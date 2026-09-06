import React, { useState, useRef, useEffect } from 'react';
import { Play, Upload, Database, Sliders, RefreshCw, BarChart, ChevronDown, Check } from 'lucide-react';

// ─── Strategy registry ────────────────────────────────────────────────────────
export const STRATEGIES = [
  { id: '52w-low', label: '52-Week Low + Volume Spike', short: '52W Low' },
  { id: '30-dma',  label: '30-Day MA + Volume Spike',   short: '30-DMA'  },
];

// ─── Shared dropdown styles ───────────────────────────────────────────────────
const TRIGGER_CLS = [
  'w-full flex items-center justify-between gap-2',
  'border border-gray-200 dark:border-gray-700/80 hover:border-gray-300 dark:hover:border-gray-600',
  'rounded-xl bg-white dark:bg-gray-800 px-3.5 py-2.5',
  'text-[13px] font-medium text-gray-800 dark:text-gray-200',
  'transition-colors shadow-sm',
  'focus:outline-none focus:ring-2 focus:ring-green-500/20',
].join(' ');

const MENU_CLS = [
  'absolute left-0 right-0 top-[calc(100%+4px)] z-[200]',
  'bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700/80 rounded-xl',
  'shadow-xl shadow-black/10 dark:shadow-black/40',
  'max-h-60 overflow-y-auto py-1',
].join(' ');

const ITEM_CLS = (active) =>
  `w-full flex items-center justify-between gap-3 px-3.5 py-2.5 text-[13px] transition-colors ${
    active
      ? 'bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400 font-medium'
      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50/80 dark:hover:bg-gray-800/80'
  }`;

// ─── Field label wrapper ──────────────────────────────────────────────────────
function Field({ label, hint, children }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{label}</span>
        {hint && <span className="text-[11px] text-gray-400 dark:text-gray-500">{hint}</span>}
      </div>
      {children}
    </div>
  );
}

// ─── Number input — minimal focus ring ───────────────────────────────────────
function NumInput({ value, onChange, step = 1, min, max }) {
  return (
    <input
      type="number"
      step={step} min={min} max={max} value={value}
      onChange={e => {
        const v = step < 1 ? parseFloat(e.target.value) : parseInt(e.target.value);
        onChange(isNaN(v) ? value : v);
      }}
      className="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700/80 hover:border-gray-300 dark:hover:border-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500/20 text-gray-900 dark:text-gray-100 text-[13px] font-semibold rounded-xl py-2.5 px-3.5 transition-colors"
    />
  );
}

// ─── Generic custom select (reused for strategy + universe) ───────────────────
function CustomSelect({ value, onChange, options, icon: Icon, placeholder }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  const sel = options.find(o => o.value === value);

  useEffect(() => {
    const fn = e => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', fn);
    return () => document.removeEventListener('mousedown', fn);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button onClick={() => setOpen(o => !o)} className={TRIGGER_CLS} type="button">
        <div className="flex items-center gap-2 min-w-0">
          {Icon && <Icon className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 shrink-0" />}
          <span className="truncate text-gray-800 dark:text-gray-200">{sel?.label ?? placeholder ?? 'Select…'}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 dark:text-gray-500 shrink-0 transition-transform duration-150 ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className={MENU_CLS}>
          {options.map(opt => {
            const active = opt.value === value;
            return (
              <button
                key={opt.value}
                onClick={() => { onChange(opt.value); setOpen(false); }}
                className={ITEM_CLS(active)}
              >
                <span className="truncate">{opt.label}</span>
                {active && <Check className="w-3.5 h-3.5 text-green-500 dark:text-green-400 shrink-0" />}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ─── Strategy select (exported for header badge) ─────────────────────────────
export function StrategySelect({ value, onChange }) {
  return (
    <div className="min-w-[220px]">
      <CustomSelect
        value={value}
        onChange={onChange}
        options={STRATEGIES.map(s => ({ value: s.id, label: s.label }))}
      />
    </div>
  );
}

// ─── Main ControlPanel ────────────────────────────────────────────────────────
export default function ControlPanel({
  strategyType, setStrategyType,
  universes, selectedUniverse, setSelectedUniverse,
  params, setParams,
  onRunScreener, onRunBacktest,
  isScanning, activeTab, onOpenUploadModal,
}) {
  const p     = (k, v) => setParams(prev => ({ ...prev, [k]: v }));
  const is52w = strategyType === '52w-low';

  const universeOptions = universes.map(u => ({ value: u.filename, label: u.name }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200/80 dark:border-gray-800 shadow-sm relative">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 border-b border-gray-100 dark:border-gray-800 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0">
            <Sliders className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </div>
          <div>
            <p className="text-[13px] font-semibold text-gray-900 dark:text-white">Strategy Configuration</p>
            <p className="text-[12px] text-gray-400 dark:text-gray-500 mt-0.5">Set parameters and stock universe</p>
          </div>
        </div>
        <StrategySelect value={strategyType} onChange={setStrategyType} />
      </div>

      {/* Params grid */}
      <div className="p-5 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Universe */}
        <Field label="Stock Universe">
          <CustomSelect
            value={selectedUniverse}
            onChange={setSelectedUniverse}
            options={universeOptions}
            icon={Database}
            placeholder="Select universe…"
          />
          <button
            onClick={onOpenUploadModal}
            className="flex items-center gap-1.5 text-[12px] text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300 font-medium mt-0.5 w-fit"
          >
            <Upload className="w-3.5 h-3.5" />
            Upload CSV
          </button>
        </Field>

        {/* Strategy threshold */}
        <Field label={is52w ? 'Near 52W Low' : 'Near 30-DMA'} hint="% threshold">
          <NumInput
            value={is52w ? params.near_low_pct : params.near_dma_pct}
            onChange={v => p(is52w ? 'near_low_pct' : 'near_dma_pct', v)}
            step={0.5} min={0.1} max={20}
          />
        </Field>

        <Field label="Min Vol Multiple" hint="× prev day">
          <NumInput value={params.min_mult} onChange={v => p('min_mult', v)} step={0.5} min={1} max={10} />
        </Field>

        <Field label="Max Vol Multiple" hint="× prev day">
          <NumInput value={params.max_mult} onChange={v => p('max_mult', v)} step={0.5} min={1} max={20} />
        </Field>
      </div>

      {/* Backtest-only params */}
      {activeTab === 'backtest' && (
        <div className="px-5 pb-5 border-t border-gray-100 dark:border-gray-800 grid grid-cols-2 lg:grid-cols-4 gap-4 pt-4">
          <Field label="Backtest Window" hint="days">
            <NumInput value={params.backtest_days} onChange={v => p('backtest_days', v)} step={10} min={10} max={365} />
          </Field>
          <Field label="Stop-Loss" hint="%">
            <NumInput value={params.stop_loss_pct} onChange={v => p('stop_loss_pct', v)} step={1} min={1} max={50} />
          </Field>
          <Field label="Target Exit" hint="%">
            <NumInput value={params.target_pct} onChange={v => p('target_pct', v)} step={1} min={1} max={100} />
          </Field>
          <Field label="Max Hold Days">
            <NumInput value={params.max_holding_days} onChange={v => p('max_holding_days', v)} step={5} min={1} max={120} />
          </Field>
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between px-5 py-3.5 border-t border-gray-100 dark:border-gray-800 bg-gray-50/60 dark:bg-gray-800/40 rounded-b-2xl">
        <p className="text-[12px] text-gray-400 dark:text-gray-500">
          {activeTab === 'screener' ? 'Scan live market data via WebSocket' : 'Simulate strategy on historical OHLCV data'}
        </p>
        {activeTab === 'screener' ? (
          <button
            onClick={onRunScreener} disabled={isScanning}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none text-white font-semibold px-4 py-2.5 rounded-xl transition-all text-[13px]"
          >
            {isScanning
              ? <><RefreshCw className="w-4 h-4 animate-spin" /><span>Scanning…</span></>
              : <><Play className="w-4 h-4 fill-current" /><span>Run Screener</span></>
            }
          </button>
        ) : (
          <button
            onClick={onRunBacktest} disabled={isScanning}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none text-white font-semibold px-4 py-2.5 rounded-xl transition-all text-[13px]"
          >
            <BarChart className="w-4 h-4" />
            <span>Run Backtest</span>
          </button>
        )}
      </div>
    </div>
  );
}
