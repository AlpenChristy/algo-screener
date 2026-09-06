import io
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import requests

from app.config import CACHE_DIR

NSE_ARCHIVES_URL = "https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
NSE_BACKUP_URL = "https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"


class NSEDeliveryLoader:
    """
    Service to fetch and cache official NSE Security-wise Delivery Position reports (Bhavdata Full).
    Provides exact EOD Deliverable Quantity and Delivery Percentage for all NSE equities.
    """
    _delivery_cache: Dict[str, Dict[str, Any]] = {}
    _last_loaded_date: Optional[str] = None
    _last_load_time: float = 0.0
    _cache_ttl_seconds: int = 14400  # 4 hours in-memory TTL

    @classmethod
    def _clean_symbol(cls, symbol: str) -> str:
        sym = str(symbol).strip().upper()
        if "." in sym:
            sym = sym.split(".")[0]
        if sym.endswith("-EQ"):
            sym = sym[:-3]
        return sym

    @classmethod
    def load_latest_delivery_data(cls, force_refresh: bool = False) -> bool:
        """
        Find and load the most recent available NSE Delivery Bhavdata into memory.
        """
        now_ts = time.time()
        if (
            cls._delivery_cache
            and not force_refresh
            and (now_ts - cls._last_load_time) < cls._cache_ttl_seconds
        ):
            return True

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        # Look back up to 7 days to find the latest trading day Bhavdata
        now = datetime.now()
        loaded_df = None
        found_date_str = None

        for days_back in range(7):
            d = now - timedelta(days=days_back)
            date_str = d.strftime("%d%m%Y")
            iso_date = d.strftime("%Y-%m-%d")
            local_cache_file = CACHE_DIR / f"delivery_bhavdata_{date_str}.csv"

            # 1. Try reading from local disk cache
            if not force_refresh and local_cache_file.exists():
                try:
                    loaded_df = pd.read_csv(local_cache_file)
                    found_date_str = iso_date
                    break
                except Exception as ex:
                    print(f"[WARN] Error reading cached delivery file {local_cache_file}: {ex}")

            # 2. Try downloading from NSE Archives
            for url_template in (NSE_ARCHIVES_URL, NSE_BACKUP_URL):
                url = url_template.format(date_str=date_str)
                try:
                    r = requests.get(url, headers=headers, timeout=6)
                    if r.status_code == 200 and len(r.content) > 1000:
                        loaded_df = pd.read_csv(io.StringIO(r.text))
                        # Save to disk cache
                        with open(local_cache_file, "w", encoding="utf-8") as f:
                            f.write(r.text)
                        found_date_str = iso_date
                        break
                except Exception:
                    continue

            if loaded_df is not None:
                break

        if loaded_df is None:
            return False

        # Clean columns and index by symbol
        loaded_df.columns = [c.strip() for c in loaded_df.columns]
        cache = {}

        for _, row in loaded_df.iterrows():
            sym = str(row.get("SYMBOL", "")).strip().upper()
            series = str(row.get("SERIES", "")).strip().upper()

            # Focus on equity series (EQ, BE, BZ, SM, etc.)
            if not sym or series not in ("EQ", "BE", "BZ", "SM", "ST"):
                continue

            try:
                traded_qty = int(float(str(row.get("TTL_TRD_QNTY", "0")).replace(",", "")))
            except (ValueError, TypeError):
                traded_qty = 0

            try:
                deliv_str = str(row.get("DELIV_QTY", "0")).strip().replace(",", "")
                deliv_qty = int(float(deliv_str)) if deliv_str and deliv_str != "-" else None
            except (ValueError, TypeError):
                deliv_qty = None

            try:
                pct_str = str(row.get("DELIV_PER", "0")).strip().replace(",", "")
                deliv_pct = float(pct_str) if pct_str and pct_str != "-" else None
            except (ValueError, TypeError):
                deliv_pct = None

            record = {
                "symbol": sym,
                "series": series,
                "date": str(row.get("DATE1", found_date_str)).strip(),
                "total_traded_qty": traded_qty,
                "deliverable_qty": deliv_qty,
                "delivery_pct": deliv_pct,
                "close_price": float(row.get("CLOSE_PRICE", 0.0)) if pd.notna(row.get("CLOSE_PRICE")) else None,
            }

            cache[sym] = record

        cls._delivery_cache = cache
        cls._last_loaded_date = found_date_str
        cls._last_load_time = now_ts
        return True

    @classmethod
    def get_delivery_info(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest official NSE deliverable quantity and percentage for a given symbol.
        """
        if not cls._delivery_cache:
            cls.load_latest_delivery_data()

        clean = cls._clean_symbol(symbol)
        return cls._delivery_cache.get(clean)
