import time
from typing import Dict, Any, Optional
import pandas as pd

class MarketDataCache:
    """
    In-memory TTL Cache for historical data and ticker metadata.
    """
    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._history_cache: Dict[str, Dict[str, Any]] = {}
        self._info_cache: Dict[str, Dict[str, Any]] = {}

    def get_history(self, cache_key: str) -> Optional[pd.DataFrame]:
        item = self._history_cache.get(cache_key)
        if item and (time.time() - item["timestamp"]) < item["ttl"]:
            return item["data"].copy()
        return None

    def set_history(self, cache_key: str, df: pd.DataFrame, ttl: Optional[int] = None):
        if df is not None:
            self._history_cache[cache_key] = {
                "data": df.copy(),
                "timestamp": time.time(),
                "ttl": ttl or self.default_ttl,
            }

    def get_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        item = self._info_cache.get(symbol)
        if item and (time.time() - item["timestamp"]) < item["ttl"]:
            return item["data"]
        return None

    def set_info(self, symbol: str, info: Dict[str, Any], ttl: Optional[int] = None):
        if info:
            self._info_cache[symbol] = {
                "data": info,
                "timestamp": time.time(),
                "ttl": ttl or self.default_ttl,
            }

    def clear(self):
        self._history_cache.clear()
        self._info_cache.clear()
