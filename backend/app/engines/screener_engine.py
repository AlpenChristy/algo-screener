import asyncio
import json
from typing import AsyncGenerator, Dict, Any

from app.universe.loader import load_symbols, resolve_universe_path
from app.strategies.dma_30 import DMA30Strategy, analyze_stock as analyze_30dma
from app.strategies.low_52w import Low52WStrategy, analyze_stock as analyze_52w

try:
    from app.db.supabase_client import upsert_signal_record
except Exception as e:
    print(f"[WARN] Could not import supabase_client in screener_engine: {e}")
    upsert_signal_record = None


def get_strategy_module(strategy_type: str):
    if strategy_type in ("52w-low", "low_52w"):
        return Low52WStrategy()
    elif strategy_type in ("30-dma", "dma_30"):
        return DMA30Strategy()
    return None


def _analyze_stock_sync(strategy_type: str, sym: str, exchange_suffix: str, params: dict):
    """Run synchronous per-stock analysis. Called inside run_in_executor to avoid blocking."""
    if strategy_type in ("52w-low", "low_52w"):
        return analyze_52w(
            sym,
            exchange_suffix=exchange_suffix,
            near_low_pct=float(params.get("near_low_pct", 2.0)),
            min_mult=float(params.get("min_mult", 3.0)),
            max_mult=float(params.get("max_mult", 4.0)),
        )
    elif strategy_type in ("30-dma", "dma_30"):
        return analyze_30dma(
            sym,
            exchange_suffix=exchange_suffix,
            near_dma_pct=float(params.get("near_dma_pct", 2.0)),
            min_mult=float(params.get("min_mult", 1.5)),
            max_mult=float(params.get("max_mult", 2.5)),
        )
    else:
        strat = get_strategy_module(strategy_type)
        if strat:
            return strat.analyze_stock(sym, exchange_suffix=exchange_suffix)
    return None


async def run_screener_async(
    strategy_type: str, universe_name: str, params: Dict[str, Any]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Async generator that yields SSE-compatible event dicts.
    Each stock is analyzed in a thread pool so the event loop stays
    unblocked and progress messages are streamed in real time.
    """
    csv_path = resolve_universe_path(universe_name)
    symbols = load_symbols(csv_path, symbol_col=params.get("symbol_col"))

    exchange_suffix = params.get("exchange_suffix", ".NS")
    delay = float(params.get("delay", 0.05))

    total = len(symbols)
    results = []
    loop = asyncio.get_event_loop()

    strat_instance = get_strategy_module(strategy_type)
    if not strat_instance and strategy_type not in ("52w-low", "low_52w", "30-dma", "dma_30"):
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    for i, sym in enumerate(symbols, 1):
        # Run blocking I/O in a thread so we don't freeze the event loop
        stock_res = await loop.run_in_executor(
            None, _analyze_stock_sync, strategy_type, sym, exchange_suffix, params
        )

        if stock_res:
            results.append(stock_res)
            if upsert_signal_record:
                try:
                    upsert_signal_record(stock_res, strategy_type)
                except Exception as ex:
                    print(f"[WARN] Failed to record signal history for {sym}: {ex}")

        yield {
            "type": "progress",
            "current": i,
            "total": total,
            "symbol": sym,
            "result": stock_res,
        }

        # Non-blocking delay between stocks
        if delay > 0:
            await asyncio.sleep(delay)

    yield {
        "type": "complete",
        "total": total,
        "scanned_count": len(results),
        "results": results,
    }


# ── Legacy sync generator (kept for backward compat / local testing) ──────────
def run_screener_generator(strategy_type: str, universe_name: str, params: Dict[str, Any]):
    """Sync generator — only use for local CLI testing. Prefer run_screener_async in API routes."""
    import time
    csv_path = resolve_universe_path(universe_name)
    symbols = load_symbols(csv_path, symbol_col=params.get("symbol_col"))
    exchange_suffix = params.get("exchange_suffix", ".NS")
    delay = float(params.get("delay", 0.05))
    total = len(symbols)
    results = []

    for i, sym in enumerate(symbols, 1):
        stock_res = _analyze_stock_sync(strategy_type, sym, exchange_suffix, params)
        if stock_res:
            results.append(stock_res)
        yield {"type": "progress", "current": i, "total": total, "symbol": sym, "result": stock_res}
        if delay > 0:
            time.sleep(delay)

    yield {"type": "complete", "total": total, "scanned_count": len(results), "results": results}
