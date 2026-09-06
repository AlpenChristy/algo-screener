import sys
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd

from app.strategies.base import BaseStrategy
from app.data.market_data import fetch_history, get_ticker_info

STRATEGY_INFO = {
    "id": "52w-low",
    "name": "52-Week Low + Volume Spike",
    "description": "Flags stocks near 52-Week Low price levels with abnormal volume expansion.",
}


def analyze_stock(
    symbol: str,
    exchange_suffix: str = ".NS",
    near_low_pct: float = 2.0,
    min_mult: float = 3.0,
    max_mult: float = 4.0,
    min_tradable_vol_pct: float = 50.0,
    lookback: str = "18mo",
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

    if hist is None or len(hist) < 252:
        return None

    hist_52w = hist.tail(252)
    low_52w = float(hist_52w["Low"].min())

    last = hist.iloc[-1]
    prev = hist.iloc[-2]

    last_close = float(last["Close"])
    last_volume = float(last["Volume"])
    prev_volume = float(prev["Volume"])

    pct_above_52w_low = ((last_close - low_52w) / low_52w) * 100
    vol_multiple = (last_volume / prev_volume) if prev_volume > 0 else float("nan")

    info = get_ticker_info(ticker_symbol, raise_errors=False)

    delivery_qty = info.get("deliveryQuantity")
    volume = info.get("regularMarketVolume") or last_volume

    delivery_pct = None
    if delivery_qty is not None and volume and volume > 0:
        try:
            delivery_pct = round((float(delivery_qty) / float(volume)) * 100, 2)
        except (ValueError, TypeError):
            delivery_pct = None

    float_shares = info.get("floatShares")
    shares_outstanding = info.get("sharesOutstanding")

    float_pct = None
    if float_shares and shares_outstanding and shares_outstanding > 0:
        try:
            float_pct = round((float(float_shares) / float(shares_outstanding)) * 100, 2)
        except (ValueError, TypeError):
            float_pct = None

    tradable_shares = float_shares if float_shares else shares_outstanding

    tradable_vol_pct = None
    if volume and tradable_shares and tradable_shares > 0:
        try:
            tradable_vol_pct = round((float(volume) / float(tradable_shares)) * 100, 4)
        except (ValueError, TypeError):
            tradable_vol_pct = None

    near_52w_low = pct_above_52w_low <= near_low_pct

    if np.isnan(vol_multiple):
        volume_spike = False
    else:
        volume_spike = (min_mult <= vol_multiple <= max_mult)

    signal = near_52w_low and volume_spike

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
        "52w_low": round(low_52w, 2),
        "pct_above_52w_low": round(pct_above_52w_low, 2),
        "volume": int(last_volume),
        "prev_volume": int(prev_volume),
        "volume_multiple": round(vol_multiple, 2) if not np.isnan(vol_multiple) else None,
        "delivery_pct": delivery_pct,
        "float_pct": float_pct,
        "tradable_vol_pct": tradable_vol_pct,
        "near_52w_low": near_52w_low,
        "volume_spike": volume_spike,
        "signal": signal,
    }


def run_backtest(
    symbols: List[str],
    exchange_suffix: str = ".NS",
    near_low_pct: float = 2.0,
    min_mult: float = 3.0,
    max_mult: float = 4.0,
    backtest_days: int = 60,
    stop_loss_pct: float = 5.0,
    target_pct: float = 10.0,
    max_holding_days: int = 20,
    dedupe_consecutive: bool = True,
    fetch_period: str = "18mo",
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

        if hist is None or len(hist) < 252:
            continue

        hist["52w_low"] = hist["Low"].rolling(window=252, min_periods=200).min()
        hist["vol_mult"] = hist["Volume"] / hist["Volume"].shift(1)
        hist["pct_above_low"] = ((hist["Close"] - hist["52w_low"]) / hist["52w_low"]) * 100

        signal_mask = (
            (hist["pct_above_low"] <= near_low_pct) &
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


class Low52WStrategy(BaseStrategy):
    strategy_id = "52w-low"
    name = "52-Week Low + Volume Spike"
    description = "Flags stocks near 52-Week Low price levels with abnormal volume expansion."

    def analyze_stock(self, symbol: str, **kwargs) -> Optional[Dict[str, Any]]:
        return analyze_stock(symbol, **kwargs)

    def run_backtest(self, symbols: List[str], **kwargs) -> Optional[pd.DataFrame]:
        return run_backtest(symbols, **kwargs)
