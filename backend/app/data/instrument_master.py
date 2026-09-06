import os
import json
import time
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import CACHE_DIR

SCRIP_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
CACHE_FILE = CACHE_DIR / "angelone_instruments.json"
CACHE_TTL_SECONDS = 86400  # 24 hours


class InstrumentMaster:
    """
    Symbol to Instrument Token & Exchange Mapping Service for Indian Equity Brokers (Angel One, etc.).
    Maintains a local cached copy of Angel One's Open API Scrip Master with fast O(1) in-memory lookup.
    """
    _master_loaded: bool = False
    _token_map: Dict[str, Dict[str, Any]] = {}  # key: f"{exchange}:{symbol}" -> scrip info

    @classmethod
    def clean_symbol(cls, symbol: str) -> str:
        """
        Normalize symbol string (e.g. 'RELIANCE.NS' -> 'RELIANCE', 'TCS-EQ' -> 'TCS').
        """
        sym = str(symbol).strip().upper()
        if "." in sym:
            sym = sym.split(".")[0]
        if sym.endswith("-EQ"):
            sym = sym[:-3]
        return sym

    @classmethod
    def load_master(cls, force_refresh: bool = False) -> bool:
        """
        Load instrument master into memory from local cache or remote download.
        """
        if cls._master_loaded and not force_refresh:
            return True

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        raw_data = None

        # Check if local cache file exists and is fresh
        if not force_refresh and CACHE_FILE.exists():
            file_age = time.time() - CACHE_FILE.stat().st_mtime
            if file_age < CACHE_TTL_SECONDS:
                try:
                    with open(CACHE_FILE, "r", encoding="utf-8") as f:
                        raw_data = json.load(f)
                except Exception as e:
                    print(f"[WARN] Failed to read cached instrument master: {e}")

        # Download if not loaded from cache
        if raw_data is None:
            try:
                print(f"[INFO] Downloading Angel One instrument master from {SCRIP_MASTER_URL}...")
                req = urllib.request.Request(SCRIP_MASTER_URL, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as response:
                    raw_data = json.loads(response.read().decode("utf-8"))

                # Save to local cache file
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(raw_data, f)
                print(f"[INFO] Cached {len(raw_data)} instruments to {CACHE_FILE}")
            except Exception as e:
                print(f"[WARN] Failed to download Angel One instrument master: {e}")
                if CACHE_FILE.exists():
                    try:
                        with open(CACHE_FILE, "r", encoding="utf-8") as f:
                            raw_data = json.load(f)
                    except Exception:
                        pass

        if not raw_data:
            return False

        # Index instruments by exchange:symbol and exchange:tradingsymbol
        token_map = {}
        for item in raw_data:
            exch = item.get("exch_seg", "").upper()
            token = item.get("token")
            symbol = item.get("symbol", "")
            name = item.get("name", "")

            if not exch or not token:
                continue

            info = {
                "token": str(token),
                "symbol": symbol,
                "name": name,
                "exchange": exch,
                "lotsize": item.get("lotsize", "1"),
                "tick_size": item.get("tick_size"),
            }

            # Map raw symbol (e.g. RELIANCE-EQ)
            if symbol:
                token_map[f"{exch}:{symbol.upper()}"] = info
                cleaned = cls.clean_symbol(symbol)
                token_map[f"{exch}:{cleaned}"] = info

            # Map scrip name (e.g. RELIANCE)
            if name:
                cleaned_name = cls.clean_symbol(name)
                # Prefer -EQ / cash segment over others for base name
                if symbol.endswith("-EQ") or f"{exch}:{cleaned_name}" not in token_map:
                    token_map[f"{exch}:{cleaned_name}"] = info

        cls._token_map = token_map
        cls._master_loaded = True
        return True

    @classmethod
    def get_token(cls, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """
        Get instrument token for a given symbol and exchange (default: NSE).
        """
        info = cls.get_instrument_info(symbol, exchange)
        return info.get("token") if info else None

    @classmethod
    def get_instrument_info(cls, symbol: str, exchange: str = "NSE") -> Optional[Dict[str, Any]]:
        """
        Get full instrument metadata for a given symbol and exchange.
        """
        if not cls._master_loaded:
            cls.load_master()

        exch = exchange.upper()
        clean = cls.clean_symbol(symbol)

        # 1. Direct match with clean symbol (e.g. NSE:RELIANCE)
        key = f"{exch}:{clean}"
        if key in cls._token_map:
            return cls._token_map[key]

        # 2. Match with -EQ suffix (e.g. NSE:RELIANCE-EQ)
        key_eq = f"{exch}:{clean}-EQ"
        if key_eq in cls._token_map:
            return cls._token_map[key_eq]

        # 3. Match raw symbol as passed
        raw_key = f"{exch}:{symbol.upper()}"
        if raw_key in cls._token_map:
            return cls._token_map[raw_key]

        return None

    @classmethod
    def register_instrument(cls, symbol: str, token: str, exchange: str = "NSE"):
        """
        Manually register an instrument token mapping.
        """
        if not cls._master_loaded:
            cls.load_master()

        clean = cls.clean_symbol(symbol)
        exch = exchange.upper()
        info = {
            "token": str(token),
            "symbol": f"{clean}-EQ",
            "name": clean,
            "exchange": exch,
        }
        cls._token_map[f"{exch}:{clean}"] = info
        cls._token_map[f"{exch}:{clean}-EQ"] = info
