import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


def calculate_dma(df: pd.DataFrame, window: int = 30, col: str = "Close") -> pd.Series:
    """Calculate Simple Moving Average (DMA)."""
    return df[col].rolling(window=window).mean()


def calculate_ema(df: pd.DataFrame, window: int = 30, col: str = "Close") -> pd.Series:
    """Calculate Exponential Moving Average (EMA)."""
    return df[col].ewm(span=window, adjust=False).mean()


def calculate_52w_low(df: pd.DataFrame, col: str = "Low") -> float:
    """Calculate 52-Week Low price from historical dataframe."""
    lookback = min(len(df), 252)
    return float(df[col].tail(lookback).min())


def calculate_52w_high(df: pd.DataFrame, col: str = "High") -> float:
    """Calculate 52-Week High price from historical dataframe."""
    lookback = min(len(df), 252)
    return float(df[col].tail(lookback).max())


def calculate_volume_spike(
    last_vol: float,
    prev_vol: float,
    min_mult: float = 2.0,
    max_mult: float = 4.0
) -> Dict[str, Any]:
    """Check volume spike conditions and calculate volume expansion multiple."""
    if prev_vol <= 0:
        return {"volume_multiple": 0.0, "is_spike": False}
    
    vol_multiple = round(last_vol / prev_vol, 2)
    is_spike = min_mult <= vol_multiple <= max_mult
    return {
        "volume_multiple": vol_multiple,
        "is_spike": is_spike,
    }


def calculate_rsi(df: pd.DataFrame, window: int = 14, col: str = "Close") -> pd.Series:
    """Calculate Relative Strength Index (RSI)."""
    delta = df[col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
