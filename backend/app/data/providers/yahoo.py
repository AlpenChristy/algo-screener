from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import yfinance as yf
from app.data.providers.base import BaseDataProvider


class YahooDataProvider(BaseDataProvider):
    """
    Yahoo Finance Market Data Provider Driver.
    """
    def fetch_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        # Append .NS if missing and not already an exchange suffix
        ticker_symbol = symbol if ("." in symbol or "^" in symbol) else f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=period, interval=interval, auto_adjust=auto_adjust)

        if hist is None or hist.empty:
            return None

        # Standardize index
        if not isinstance(hist.index, pd.DatetimeIndex):
            hist.index = pd.to_datetime(hist.index)
        if hist.index.tz is not None:
            hist.index = hist.index.tz_localize(None)
        hist.index.name = "Date"

        # Keep standard OHLCV columns
        standard_cols = ["Open", "High", "Low", "Close", "Volume"]
        existing_cols = [c for c in standard_cols if c in hist.columns]
        df = hist[existing_cols].copy()

        # Type conversion
        for col in ["Open", "High", "Low", "Close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "Volume" in df.columns:
            df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype(int)

        if dropna_cols:
            valid_drop = [c for c in dropna_cols if c in df.columns]
            if valid_drop:
                df = df.dropna(subset=valid_drop)

        return df.sort_index()

    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        ticker_symbol = symbol if ("." in symbol or "^" in symbol) else f"{symbol}.NS"
        ticker = yf.Ticker(ticker_symbol)
        try:
            info = ticker.info or {}
        except Exception:
            info = {}

        return {
            "symbol": symbol,
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
            "open": info.get("open") or info.get("regularMarketOpen"),
            "dayHigh": info.get("dayHigh") or info.get("regularMarketDayHigh"),
            "dayLow": info.get("dayLow") or info.get("regularMarketDayLow"),
            "regularMarketPreviousClose": info.get("previousClose") or info.get("regularMarketPreviousClose"),
            "regularMarketVolume": info.get("volume") or info.get("regularMarketVolume"),
            "deliveryQuantity": info.get("deliveryQuantity"),
            "floatShares": info.get("floatShares"),
            "sharesOutstanding": info.get("sharesOutstanding"),
        }
