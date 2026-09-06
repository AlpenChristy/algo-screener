import React from 'react';
import {
  LayoutDashboard, TrendingUp, History, BarChart2, Database,
  ChevronLeft, ChevronRight, X,
} from 'lucide-react';

const NAV_GROUPS = [
  {
    label: 'SCREENER',
    items: [
      { id: 'screener', icon: LayoutDashboard, label: 'Live Screener' },
      { id: 'backtest', icon: BarChart2,       label: 'Backtester'    },
    ],
  },
  {
    label: 'RECORDS',
    items: [
      { id: 'history', icon: History, label: 'Signal History' },
    ],
  },
];

export const SIDEBAR_EXPANDED = 248;
export const SIDEBAR_COLLAPSED = 64;

export default function Sidebar({
  activeTab, setActiveTab,
  collapsed, setCollapsed,
  mobileOpen, setMobileOpen,
}) {
  const w = collapsed ? SIDEBAR_COLLAPSED : SIDEBAR_EXPANDED;

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-xs z-40 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <aside
        style={{ width: w }}
        className={`
          fixed top-0 bottom-0 left-0 z-50
          bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800
          flex flex-col
          transition-[width] duration-200 ease-in-out
          overflow-hidden
          lg:translate-x-0
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* ── Header ── */}
        <div
          className="flex items-center h-[60px] border-b border-gray-100 dark:border-gray-800 shrink-0 overflow-hidden"
          style={{ padding: collapsed ? '0 12px' : '0 16px' }}
        >
          {/* Logo — hidden when collapsed */}
          {!collapsed && (
            <div className="flex items-center gap-2.5 flex-1 min-w-0">
              <div className="w-7 h-7 rounded-lg bg-green-600 flex items-center justify-center shrink-0">
                <TrendingUp className="w-4 h-4 text-white" />
              </div>
              <div className="flex flex-col leading-none min-w-0">
                <span className="text-[13px] font-bold text-gray-900 dark:text-white truncate">AlgoScreener</span>
                <span className="text-[11px] text-gray-400 dark:text-gray-500 truncate mt-0.5">Quant Platform</span>
              </div>
            </div>
          )}

          {/* Desktop collapse toggle */}
          <button
            onClick={() => setCollapsed(c => !c)}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className={`
              hidden lg:flex items-center justify-center rounded-lg
              text-gray-400 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors
              shrink-0
              ${collapsed ? 'w-10 h-10 mx-auto' : 'w-7 h-7 ml-auto'}
            `}
          >
            {collapsed
              ? <ChevronRight className="w-4 h-4" />
              : <ChevronLeft  className="w-4 h-4" />
            }
          </button>

          {/* Mobile close button */}
          <button
            onClick={() => setMobileOpen(false)}
            className="lg:hidden flex items-center justify-center w-7 h-7 rounded-lg text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors ml-auto shrink-0"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* ── Navigation ── */}
        <nav className="flex-1 overflow-y-auto py-3 px-2 space-y-4">
          {NAV_GROUPS.map(group => (
            <div key={group.label}>
              {!collapsed && (
                <div className="text-[10px] font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-widest px-2 mb-1.5">
                  {group.label}
                </div>
              )}
              <div className="space-y-0.5">
                {group.items.map(({ id, icon: Icon, label }) => {
                  const active = activeTab === id;
                  return (
                    <button
                      key={id}
                      title={collapsed ? label : undefined}
                      onClick={() => { setActiveTab(id); setMobileOpen?.(false); }}
                      className={`
                        w-full flex items-center rounded-xl transition-all duration-100 text-[13px] font-medium
                        ${collapsed
                          ? 'justify-center p-3'
                          : 'gap-3 px-3 py-2.5 text-left'
                        }
                        ${active
                          ? 'bg-green-50 dark:bg-green-950/40 text-green-700 dark:text-green-400'
                          : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100/80 dark:hover:bg-gray-800/80'
                        }
                      `}
                    >
                      <Icon className={`shrink-0 w-4.5 h-4.5 ${active ? 'text-green-600 dark:text-green-400' : 'text-gray-400 dark:text-gray-500'}`} style={{ width: 18, height: 18 }} />
                      {!collapsed && <span className="truncate">{label}</span>}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* ── DB Status footer ── */}
        <div className="px-2 pb-4 pt-3 border-t border-gray-100 dark:border-gray-800 shrink-0">
          <div
            title={collapsed ? 'Supabase · Connected' : undefined}
            className={`flex items-center gap-2.5 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-100 dark:border-gray-800 ${collapsed ? 'justify-center p-3' : 'px-3 py-2.5'}`}
          >
            <Database className="shrink-0 text-green-500" style={{ width: 14, height: 14 }} />
            {!collapsed && (
              <div className="flex flex-col leading-none min-w-0 flex-1">
                <span className="text-[12px] font-semibold text-gray-700 dark:text-gray-300">Supabase</span>
                <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-0.5">PostgreSQL · Connected</span>
              </div>
            )}
            {!collapsed && (
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 shrink-0 animate-pulse ml-auto" />
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
