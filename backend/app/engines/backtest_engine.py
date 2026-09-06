from typing import Dict, Any
import pandas as pd
from app.universe.loader import load_symbols, resolve_universe_path
from app.strategies.dma_30 import DMA30Strategy, run_backtest as backtest_30dma
from app.strategies.low_52w import Low52WStrategy, run_backtest as backtest_52w


def run_backtest_service(strategy_type: str, universe_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    csv_path = resolve_universe_path(universe_name)
    symbols = load_symbols(csv_path, symbol_col=params.get("symbol_col"))

    exchange_suffix = params.get("exchange_suffix", ".NS")
    backtest_days = int(params.get("backtest_days", 60))
    stop_loss_pct = float(params.get("stop_loss_pct", 5.0))
    target_pct = float(params.get("target_pct", 10.0))
    max_holding_days = int(params.get("max_holding_days", 20))
    delay = float(params.get("delay", 0.02))

    if strategy_type in ("52w-low", "low_52w"):
        near_low_pct = float(params.get("near_low_pct", 2.0))
        min_mult = float(params.get("min_mult", 3.0))
        max_mult = float(params.get("max_mult", 4.0))

        df_trades = backtest_52w(
            symbols=symbols,
            exchange_suffix=exchange_suffix,
            near_low_pct=near_low_pct,
            min_mult=min_mult,
            max_mult=max_mult,
            backtest_days=backtest_days,
            stop_loss_pct=stop_loss_pct,
            target_pct=target_pct,
            max_holding_days=max_holding_days,
            dedupe_consecutive=True,
            fetch_period="18mo",
            delay=delay,
        )
    elif strategy_type in ("30-dma", "dma_30"):
        near_dma_pct = float(params.get("near_dma_pct", 2.0))
        min_mult = float(params.get("min_mult", 1.5))
        max_mult = float(params.get("max_mult", 2.5))

        df_trades = backtest_30dma(
            symbols=symbols,
            exchange_suffix=exchange_suffix,
            near_dma_pct=near_dma_pct,
            min_mult=min_mult,
            max_mult=max_mult,
            backtest_days=backtest_days,
            stop_loss_pct=stop_loss_pct,
            target_pct=target_pct,
            max_holding_days=max_holding_days,
            dedupe_consecutive=True,
            fetch_period="12mo",
            delay=delay,
        )
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

    if df_trades is None or df_trades.empty:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "best_trade": 0.0,
            "worst_trade": 0.0,
            "exit_reasons": {},
            "trades": [],
        }

    total_trades = len(df_trades)
    win_rate = round((df_trades["return_pct"] > 0).mean() * 100, 1)
    avg_return = round(float(df_trades["return_pct"].mean()), 2)
    best_trade = round(float(df_trades["return_pct"].max()), 2)
    worst_trade = round(float(df_trades["return_pct"].min()), 2)

    reason_counts = df_trades["exit_reason"].value_counts().to_dict()
    trades_list = df_trades.to_dict(orient="records")

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "exit_reasons": reason_counts,
        "trades": trades_list,
    }
