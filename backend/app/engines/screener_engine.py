import time
from typing import Dict, Any, Generator
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


def run_screener_generator(strategy_type: str, universe_name: str, params: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    csv_path = resolve_universe_path(universe_name)
    symbols = load_symbols(csv_path, symbol_col=params.get("symbol_col"))

    exchange_suffix = params.get("exchange_suffix", ".NS")
    delay = float(params.get("delay", 0.05))

    total = len(symbols)
    results = []

    strat_instance = get_strategy_module(strategy_type)
    if not strat_instance:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    for i, sym in enumerate(symbols, 1):
        stock_res = None
        if strategy_type in ("52w-low", "low_52w"):
            near_low_pct = float(params.get("near_low_pct", 2.0))
            min_mult = float(params.get("min_mult", 3.0))
            max_mult = float(params.get("max_mult", 4.0))
            stock_res = analyze_52w(
                sym,
                exchange_suffix=exchange_suffix,
                near_low_pct=near_low_pct,
                min_mult=min_mult,
                max_mult=max_mult,
            )
        elif strategy_type in ("30-dma", "dma_30"):
            near_dma_pct = float(params.get("near_dma_pct", 2.0))
            min_mult = float(params.get("min_mult", 1.5))
            max_mult = float(params.get("max_mult", 2.5))
            stock_res = analyze_30dma(
                sym,
                exchange_suffix=exchange_suffix,
                near_dma_pct=near_dma_pct,
                min_mult=min_mult,
                max_mult=max_mult,
            )
        else:
            stock_res = strat_instance.analyze_stock(sym, exchange_suffix=exchange_suffix)

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

        if delay > 0:
            time.sleep(delay)

    yield {
        "type": "complete",
        "total": total,
        "scanned_count": len(results),
        "results": results,
    }
