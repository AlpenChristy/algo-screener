import React from 'react';
import { Activity, CheckCircle, Target, Zap } from 'lucide-react';

function Card({ icon: Icon, iconBg, label, value, sub }) {
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

export default function KpiCards({ data, strategyType }) {
  if (!data || data.length === 0) return null;

  const total      = data.length;
  const signals    = data.filter(d => d.signal).length;
  const near       = strategyType === '52w-low'
    ? data.filter(d => d.near_52w_low).length
    : data.filter(d => d.near_30_dma).length;
  const volSpikes  = data.filter(d => d.volume_spike).length;
  const avgVol     = (data.reduce((s, d) => s + (d.volume_multiple || 0), 0) / total).toFixed(1);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card
        icon={Activity}
        iconBg="bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
        label="Stocks Scanned"
        value={total.toLocaleString()}
      />
      <Card
        icon={CheckCircle}
        iconBg="bg-green-100 dark:bg-green-950/60 text-green-600 dark:text-green-400"
        label="Signal Matches"
        value={signals}
        sub={`${total > 0 ? ((signals / total) * 100).toFixed(1) : 0}% hit rate`}
      />
      <Card
        icon={Target}
        iconBg="bg-amber-100 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400"
        label={strategyType === '52w-low' ? 'Near 52W Low' : 'Near 30-DMA'}
        value={near}
      />
      <Card
        icon={Zap}
        iconBg="bg-blue-100 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400"
        label="Volume Spikes"
        value={volSpikes}
        sub={`avg ${avgVol}× vol multiple`}
      />
    </div>
  );
}
