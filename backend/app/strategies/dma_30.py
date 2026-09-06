import sys
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd

from app.strategies.base import BaseStrategy
from app.data.market_data import fetch_history, get_ticker_info
from app.data.delivery_data import NSEDeliveryLoader

STRATEGY_INFO = {
    "id": "30-dma",
    "name": "30-DMA + Volume Spike + Delivery",
    "description": "Flags stocks near 30-Day Moving Average with volume expansion and >50% deliverable quantity.",
}


def analyze_stock(
    symbol: str,
    exchange_suffix: str = ".NS",
    near_dma_pct: float = 2.0,
    min_mult: float = 1.5,
    max_mult: float = 2.5,
    min_tradable_vol_pct: float = 50.0,
    lookback: str = "6mo",
    dma_period: int = 30,
) -> Optional[Dict[str, Any]]:
    ticker_symbol = f"{symbol}{exchange_suffix}"
    hist = fetch_history(
        ticker_symbol,
        period=lookback,
        interval="1d",
        auto_adjust=False,
        dropna_cols=["Close", "Volume"],
        print_errors=True
    )

    if hist is None or len(hist) < dma_period + 1:
        return None

    hist["30_dma"] = hist["Close"].rolling(window=dma_period).mean()

    last = hist.iloc[-1]
    prev = hist.iloc[-2]

    last_close = float(last["Close"])
    dma_30_val = float(last["30_dma"])
    last_volume = float(last["Volume"])
    prev_volume = float(prev["Volume"])

    pct_from_30_dma = ((last_close - dma_30_val) / dma_30_val) * 100
    vol_multiple = (last_volume / prev_volume) if prev_volume > 0 else float("nan")

    info = get_ticker_info(ticker_symbol, raise_errors=False)

    # --- Delivery data from NSE Bhavdata (authoritative source) ---
    NSEDeliveryLoader.load_latest_delivery_data()
    delivery_info = NSEDeliveryLoader.get_delivery_info(symbol)
    delivery_pct = delivery_info.get("delivery_pct") if delivery_info else None

    float_shares = info.get("floatShares")
    shares_outstanding = info.get("sharesOutstanding")

    float_pct = None
    if float_shares and shares_outstanding and shares_outstanding > 0:
        try:
            float_pct = round((float(float_shares) / float(shares_outstanding)) * 100, 2)
        except (ValueError, TypeError):
            float_pct = None

    tradable_shares = float_shares if float_shares else shares_outstanding
    volume = info.get("regularMarketVolume") or last_volume

    tradable_vol_pct = None
    if volume and tradable_shares and tradable_shares > 0:
        try:
            tradable_vol_pct = round((float(volume) / float(tradable_shares)) * 100, 4)
        except (ValueError, TypeError):
            tradable_vol_pct = None

    near_30_dma = abs(pct_from_30_dma) <= near_dma_pct

    if np.isnan(vol_multiple):
        volume_spike = False
    else:
        volume_spike = (min_mult <= vol_multiple <= max_mult)

    high_delivery = (delivery_pct is not None) and (delivery_pct >= 50.0)

    signal = near_30_dma and volume_spike and high_delivery

    last_date = hist.index[-1]
    if isinstance(last_date, pd.Timestamp):
        date_str = last_date.strftime("%Y-%m-%d")
    else:
        date_str = str(last_date)

    return {
        "symbol": symbol,
        "ticker": ticker_symbol,
        "date": date_str,
        "close": round(last_close, 2),
        "30_dma": round(dma_30_val, 2),
        "pct_from_30_dma": round(pct_from_30_dma, 2),
        "volume": int(last_volume),
        "prev_volume": int(prev_volume),
        "volume_multiple": round(vol_multiple, 2) if not np.isnan(vol_multiple) else None,
        "delivery_pct": round(delivery_pct, 2) if delivery_pct is not None else None,
        "float_pct": float_pct,
        "tradable_vol_pct": tradable_vol_pct,
        "near_30_dma": near_30_dma,
        "volume_spike": volume_spike,
        "high_delivery": high_delivery,
        "signal": signal,
    }


def run_backtest(
    symbols: List[str],
    exchange_suffix: str = ".NS",
    near_dma_pct: float = 2.0,
    min_mult: float = 1.5,
    max_mult: float = 2.5,
    backtest_days: int = 60,
    stop_loss_pct: float = 5.0,
    target_pct: float = 10.0,
    max_holding_days: int = 20,
    dedupe_consecutive: bool = True,
    fetch_period: str = "12mo",
    delay: float = 0.02,
) -> Optional[pd.DataFrame]:
    trades = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=backtest_days)

    for sym in symbols:
        ticker = f"{sym}{exchange_suffix}"
        hist = fetch_history(
            ticker,
            period=fetch_period,
            interval="1d",
            auto_adjust=False,
            dropna_cols=["Close", "Volume"],
            print_errors=False
        )

        if hist is None or len(hist) < 35:
            continue

        hist["30_dma"] = hist["Close"].rolling(window=30).mean()
        hist["vol_mult"] = hist["Volume"] / hist["Volume"].shift(1)
        hist["pct_from_30_dma"] = ((hist["Close"] - hist["30_dma"]) / hist["30_dma"]) * 100

        signal_mask = (
            (hist["pct_from_30_dma"].abs() <= near_dma_pct) &
            (hist["vol_mult"] >= min_mult) &
            (hist["vol_mult"] <= max_mult)
        )

        in_window_mask = signal_mask & (hist.index >= pd.Timestamp(start_date))
        signal_indices = np.where(in_window_mask)[0]

        if len(signal_indices) == 0:
            continue

        last_entry_idx = -999

        for idx in signal_indices:
            if dedupe_consecutive and (idx - last_entry_idx) < 3:
                continue

            entry_date = hist.index[idx]
            entry_price = float(hist["Close"].iloc[idx])
            stop_price = entry_price * (1.0 - stop_loss_pct / 100.0)
            target_price = entry_price * (1.0 + target_pct / 100.0)

            exit_date = None
            exit_price = None
            exit_reason = None
            holding_days = 0

            max_future = min(idx + max_holding_days + 1, len(hist))

            for f_idx in range(idx + 1, max_future):
                holding_days += 1
                curr_high = float(hist["High"].iloc[f_idx])
                curr_low = float(hist["Low"].iloc[f_idx])
                curr_close = float(hist["Close"].iloc[f_idx])
                curr_date = hist.index[f_idx]

                if curr_low <= stop_price:
                    exit_date = curr_date
                    exit_price = stop_price
                    exit_reason = "STOP_LOSS"
                    break
                elif curr_high >= target_price:
                    exit_date = curr_date
                    exit_price = target_price
                    exit_reason = "TARGET"
                    break

            if exit_date is None:
                last_available_idx = min(idx + max_holding_days, len(hist) - 1)
                exit_date = hist.index[last_available_idx]
                exit_price = float(hist["Close"].iloc[last_available_idx])
                exit_reason = "TIME_EXIT"
                holding_days = last_available_idx - idx

            return_pct = ((exit_price - entry_price) / entry_price) * 100.0

            trades.append({
                "symbol": sym,
                "entry_date": entry_date.strftime("%Y-%m-%d"),
                "entry_price": round(entry_price, 2),
                "exit_date": exit_date.strftime("%Y-%m-%d"),
                "exit_price": round(exit_price, 2),
                "return_pct": round(return_pct, 2),
                "exit_reason": exit_reason,
                "holding_days": holding_days,
            })

            last_entry_idx = idx

        if delay > 0:
            time.sleep(delay)

    return pd.DataFrame(trades) if trades else pd.DataFrame()


class DMA30Strategy(BaseStrategy):
    strategy_id = "30-dma"
    name = "30-DMA + Volume Spike + Delivery"
    description = "Flags stocks near 30-Day Moving Average with volume expansion and >50% deliverable quantity."

    def analyze_stock(self, symbol: str, **kwargs) -> Optional[Dict[str, Any]]:
        return analyze_stock(symbol, **kwargs)

    def run_backtest(self, symbols: List[str], **kwargs) -> Optional[pd.DataFrame]:
        return run_backtest(symbols, **kwargs)
