import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
from app.data.providers.base import BaseDataProvider
from app.config import FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN

try:
    from fyers_apiv3 import fyersModel
    HAS_FYERS = True
except ImportError:
    HAS_FYERS = False


class FyersDataProvider(BaseDataProvider):
    """
    Fyers API v3 Market Data Provider Driver.
    """
    def __init__(self, client_id: Optional[str] = None, access_token: Optional[str] = None):
        self.client_id = client_id or FYERS_CLIENT_ID
        self.access_token = access_token or FYERS_ACCESS_TOKEN
        self.client = None

    def _get_client(self):
        if not HAS_FYERS:
            raise RuntimeError("fyers_apiv3 library not installed.")
        if not self.client_id or not self.access_token:
            raise RuntimeError("Fyers credentials (FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN) missing.")
        if not self.client:
            self.client = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                is_async=False,
                log_path=""
            )
        return self.client

    def _to_fyers_symbol(self, symbol: str, exchange_suffix: str = ".NS") -> str:
        base_symbol = symbol.split(".")[0] if "." in symbol else symbol
        if exchange_suffix.upper() in (".NS", ".NSE"):
            exchange = "NSE"
        elif exchange_suffix.upper() in (".BO", ".BSE"):
            exchange = "BSE"
        else:
            exchange = "NSE"
        return f"{exchange}:{base_symbol}-EQ"

    def _parse_period_to_date(self, period: str) -> datetime:
        now = datetime.now()
        period = str(period).strip().lower()
        if period.endswith("d"):
            days = int(period[:-1])
            return now - timedelta(days=days)
        elif period.endswith("wk") or period.endswith("w"):
            weeks = int(period[:-2] if period.endswith("wk") else period[:-1])
            return now - timedelta(weeks=weeks)
        elif period.endswith("mo") or period.endswith("m"):
            months = int(period[:-2] if period.endswith("mo") else period[:-1])
            return now - timedelta(days=months * 30)
        elif period.endswith("y"):
            years = int(period[:-1])
            return now - timedelta(days=years * 365)
        return now - timedelta(days=180)

    def fetch_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        client = self._get_client()
        fyers_symbol = self._to_fyers_symbol(symbol)
        start_date = self._parse_period_to_date(period)
        end_date = datetime.now()

        resolution = "D"
        if interval == "1m":
            resolution = "1"
        elif interval == "5m":
            resolution = "5"
        elif interval == "15m":
            resolution = "15"
        elif interval == "60m" or interval == "1h":
            resolution = "60"

        data = {
            "symbol": fyers_symbol,
            "resolution": resolution,
            "date_format": "1",
            "range_from": start_date.strftime("%Y-%m-%d"),
            "range_to": end_date.strftime("%Y-%m-%d"),
            "cont_flag": "1"
        }

        response = client.history(data=data)
        if not response or response.get("s") != "ok":
            raise RuntimeError(f"Fyers history failed: {response.get('message', 'Unknown error')}")

        candles = response.get("candles", [])
        if not candles:
            return None

        df = pd.DataFrame(
            candles,
            columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"]
        )
        df["Date"] = pd.to_datetime(df["Timestamp"], unit="s")
        df.set_index("Date", inplace=True)
        df.drop(columns=["Timestamp"], inplace=True)

        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype(int)

        if dropna_cols:
            valid_drop = [c for c in dropna_cols if c in df.columns]
            if valid_drop:
                df = df.dropna(subset=valid_drop)

        return df.sort_index()

    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        client = self._get_client()
        fyers_symbol = self._to_fyers_symbol(symbol)
        response = client.quotes(data={"symbols": fyers_symbol})
        if not response or response.get("s") != "ok" or not response.get("d"):
            return {"symbol": symbol}

        v = response["d"][0].get("v", {})
        return {
            "symbol": symbol,
            "currentPrice": v.get("lp"),
            "open": v.get("open_price"),
            "dayHigh": v.get("high_price"),
            "dayLow": v.get("low_price"),
            "regularMarketPreviousClose": v.get("prev_close_price"),
            "regularMarketVolume": v.get("volume"),
            "deliveryQuantity": None,
            "floatShares": None,
            "sharesOutstanding": None,
        }
