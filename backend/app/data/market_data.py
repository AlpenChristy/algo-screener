import sys
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
import pandas as pd

from app.config import MARKET_DATA_PROVIDER
from app.data.providers.yahoo import YahooDataProvider
from app.data.providers.fyers import FyersDataProvider, HAS_FYERS
from app.data.providers.angelone import AngelOneDataProvider, HAS_SMARTAPI
from app.data.cache import MarketDataCache

_cache = MarketDataCache(default_ttl=300)
_active_provider_instances: Dict[str, Any] = {}
_active_provider_name = None


def get_active_provider() -> str:
    """
    Determine active market data provider based on configuration and available libraries/credentials.
    Priority: configured MARKET_DATA_PROVIDER -> falls back to 'angelone' -> 'fyers' -> 'yfinance'.
    """
    global _active_provider_name
    if _active_provider_name:
        return _active_provider_name

    requested = MARKET_DATA_PROVIDER

    if requested == "angelone":
        if not HAS_SMARTAPI:
            print("[WARN] SmartApi library not installed. Falling back to yfinance.", file=sys.stderr)
            _active_provider_name = "yfinance"
            return "yfinance"
        from app.config import ANGELONE_API_KEY, ANGELONE_CLIENT_CODE, ANGELONE_PIN, ANGELONE_TOTP_SECRET
        if not (ANGELONE_API_KEY and ANGELONE_CLIENT_CODE and ANGELONE_PIN and ANGELONE_TOTP_SECRET):
            print("[WARN] Angel One credentials missing in config. Falling back to yfinance.", file=sys.stderr)
            _active_provider_name = "yfinance"
            return "yfinance"
        _active_provider_name = "angelone"
        return "angelone"

    elif requested == "fyers":
        if not HAS_FYERS:
            print("[WARN] fyers_apiv3 library not installed. Falling back to yfinance.", file=sys.stderr)
            _active_provider_name = "yfinance"
            return "yfinance"
        from app.config import FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN
        if not (FYERS_CLIENT_ID and FYERS_ACCESS_TOKEN):
            print("[WARN] Fyers credentials not set. Falling back to yfinance.", file=sys.stderr)
            _active_provider_name = "yfinance"
            return "yfinance"
        _active_provider_name = "fyers"
        return "fyers"

    _active_provider_name = requested
    return requested


def _get_provider_instance(provider_name: Optional[str] = None):
    pname = provider_name or get_active_provider()
    if pname not in _active_provider_instances:
        if pname == "angelone":
            _active_provider_instances[pname] = AngelOneDataProvider()
        elif pname == "fyers":
            _active_provider_instances[pname] = FyersDataProvider()
        else:
            _active_provider_instances[pname] = YahooDataProvider()
    return _active_provider_instances[pname]


def fetch_history(
    symbol: str,
    period: str = "6mo",
    interval: str = "1d",
    auto_adjust: bool = False,
    dropna_cols: Optional[List[str]] = None,
    raise_errors: bool = False,
    print_errors: bool = True,
    provider_name: Optional[str] = None,
    use_cache: bool = True,
) -> Optional[pd.DataFrame]:
    """
    Unified dispatcher to fetch historical OHLCV data.
    Guarantees standard DataFrame format:
    - Index: pd.DatetimeIndex named 'Date'
    - Columns: ['Open', 'High', 'Low', 'Close', 'Volume']
    """
    cache_key = f"{symbol}_{period}_{interval}"
    if use_cache:
        cached = _cache.get_history(cache_key)
        if cached is not None:
            return cached

    pname = provider_name or get_active_provider()
    provider = _get_provider_instance(pname)

    try:
        df = provider.fetch_history(
            symbol=symbol,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            dropna_cols=dropna_cols,
        )
        if df is not None and use_cache:
            _cache.set_history(cache_key, df)
        return df
    except Exception as e:
        # If AngelOne or Fyers fails, attempt Yahoo Finance fallback before throwing
        if pname != "yfinance":
            try:
                fallback_provider = _get_provider_instance("yfinance")
                df = fallback_provider.fetch_history(
                    symbol=symbol,
                    period=period,
                    interval=interval,
                    auto_adjust=auto_adjust,
                    dropna_cols=dropna_cols,
                )
                if df is not None:
                    if use_cache:
                        _cache.set_history(cache_key, df)
                    return df
            except Exception:
                pass

        if raise_errors:
            raise e
        if print_errors:
            print(f"  [WARN] {symbol}: fetch failed using {pname} ({e})", file=sys.stderr)
        return None


def get_daily_data(
    symbols: Union[str, List[str]],
    start_date: Optional[Union[str, datetime]] = None,
    end_date: Optional[Union[str, datetime]] = None,
    period: str = "6mo",
    provider_name: Optional[str] = None,
    use_cache: bool = True,
) -> Union[Optional[pd.DataFrame], Dict[str, pd.DataFrame]]:
    """
    Batch abstraction helper to fetch daily historical data for one or multiple symbols.
    """
    if isinstance(symbols, str):
        pname = provider_name or get_active_provider()
        provider = _get_provider_instance(pname)
        if start_date and end_date:
            return provider.get_historical_data(
                symbol=symbols,
                start_date=start_date,
                end_date=end_date,
                interval="1d"
            )
        return fetch_history(
            symbol=symbols,
            period=period,
            interval="1d",
            provider_name=provider_name,
            use_cache=use_cache
        )

    results = {}
    for sym in symbols:
        df = fetch_history(
            symbol=sym,
            period=period,
            interval="1d",
            provider_name=provider_name,
            use_cache=use_cache
        )
        if df is not None:
            results[sym] = df
    return results


def get_ticker_info(
    symbol: str,
    raise_errors: bool = False,
    provider_name: Optional[str] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Unified dispatcher to fetch ticker metadata and real-time quotes.
    """
    if use_cache:
        cached = _cache.get_info(symbol)
        if cached is not None:
            return cached

    pname = provider_name or get_active_provider()
    provider = _get_provider_instance(pname)

    try:
        info = provider.get_ticker_info(symbol)
        if not info:
            info = {"symbol": symbol}

        # Enrich with official NSE Delivery Position data if deliveryQuantity is missing
        if info.get("deliveryQuantity") is None:
            from app.data.delivery_data import NSEDeliveryLoader
            deliv_info = NSEDeliveryLoader.get_delivery_info(symbol)
            if deliv_info:
                info["deliveryQuantity"] = deliv_info.get("deliverable_qty")
                info["deliveryPercentage"] = deliv_info.get("delivery_pct")
                if not info.get("regularMarketVolume"):
                    info["regularMarketVolume"] = deliv_info.get("total_traded_qty")

        if info and use_cache:
            _cache.set_info(symbol, info)
        return info
    except Exception as e:
        if raise_errors:
            raise e
        return {"symbol": symbol}
