import os
import sys
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
from app.data.providers.base import BaseDataProvider
from app.auth.angelone_auth import AngelOneAuth
from app.data.instrument_master import InstrumentMaster

try:
    from SmartApi import SmartConnect
    HAS_SMARTAPI = True
except ImportError:
    HAS_SMARTAPI = False


class AngelOneDataProvider(BaseDataProvider):
    """
    Angel One SmartAPI Market Data Provider.
    Implements historical candle retrieval and live quotes using SmartConnect.
    """
    INTERVAL_MAP = {
        "1d": "ONE_DAY",
        "1D": "ONE_DAY",
        "day": "ONE_DAY",
        "D": "ONE_DAY",
        "1m": "ONE_MINUTE",
        "1min": "ONE_MINUTE",
        "3m": "THREE_MINUTE",
        "5m": "FIVE_MINUTE",
        "10m": "TEN_MINUTE",
        "15m": "FIFTEEN_MINUTE",
        "30m": "THIRTY_MINUTE",
        "1h": "ONE_HOUR",
        "60m": "ONE_HOUR",
    }

    def __init__(self, auth: Optional[AngelOneAuth] = None):
        self.auth = auth or AngelOneAuth()
        self._smart_api = None

    def _get_api(self):
        """
        Get or initialize active SmartConnect session.
        """
        if not HAS_SMARTAPI:
            raise RuntimeError("smartapi-python library is not installed.")
        if not self._smart_api:
            session = self.auth.login()
            if not session or not session.get("status"):
                raise RuntimeError(f"Angel One login failed: {session}")
            self._smart_api = self.auth.smart_api
        return self._smart_api

    def _parse_period_to_dates(self, period: str) -> tuple[datetime, datetime]:
        """
        Convert relative period string (e.g. '1mo', '6mo', '1y') into (start_datetime, end_datetime).
        """
        now = datetime.now()
        period = str(period).strip().lower()
        if period.endswith("d"):
            days = int(period[:-1])
            start = now - timedelta(days=days)
        elif period.endswith("wk") or period.endswith("w"):
            weeks = int(period[:-2] if period.endswith("wk") else period[:-1])
            start = now - timedelta(weeks=weeks)
        elif period.endswith("mo") or period.endswith("m"):
            months = int(period[:-2] if period.endswith("mo") else period[:-1])
            start = now - timedelta(days=months * 30)
        elif period.endswith("y"):
            years = int(period[:-1])
            start = now - timedelta(days=years * 365)
        else:
            start = now - timedelta(days=180)  # default 6 months
        return start, now

    def fetch_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
        exchange: str = "NSE",
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data using Angel One getCandleData.
        """
        start_date, end_date = self._parse_period_to_dates(period)
        return self.get_historical_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=interval,
            auto_adjust=auto_adjust,
            dropna_cols=dropna_cols,
            exchange=exchange,
        )

    def get_historical_data(
        self,
        symbol: str,
        start_date: str | datetime,
        end_date: str | datetime,
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
        exchange: str = "NSE",
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical candle data between specific start and end dates.
        """
        api = self._get_api()

        # Format dates as YYYY-MM-DD HH:MM
        if isinstance(start_date, (datetime, pd.Timestamp)):
            from_str = start_date.strftime("%Y-%m-%d 09:15")
        else:
            from_str = f"{str(start_date).split(' ')[0]} 09:15"

        if isinstance(end_date, (datetime, pd.Timestamp)):
            to_str = end_date.strftime("%Y-%m-%d 15:30")
        else:
            to_str = f"{str(end_date).split(' ')[0]} 15:30"

        # Resolve symbol token
        clean_sym = InstrumentMaster.clean_symbol(symbol)
        token = InstrumentMaster.get_token(clean_sym, exchange)

        if not token:
            # Fallback to searchScrip
            try:
                search_res = api.searchScrip(exchange=exchange, searchscrip=clean_sym)
                if search_res and search_res.get("status") and search_res.get("data"):
                    for item in search_res["data"]:
                        if item.get("tradingsymbol", "").endswith("-EQ") or item.get("tradingsymbol") == clean_sym:
                            token = str(item.get("symboltoken"))
                            InstrumentMaster.register_instrument(clean_sym, token, exchange)
                            break
            except Exception as ex:
                print(f"[WARN] searchScrip failed for {clean_sym}: {ex}")

        if not token:
            raise ValueError(f"Could not resolve Angel One instrument token for {symbol} on {exchange}")

        angel_interval = self.INTERVAL_MAP.get(interval, "ONE_DAY")

        payload = {
            "exchange": exchange.upper(),
            "symboltoken": str(token),
            "interval": angel_interval,
            "fromdate": from_str,
            "todate": to_str,
        }

        try:
            response = api.getCandleData(payload)
        except Exception as e:
            # If session expired, re-login and retry once
            self._smart_api = None
            api = self._get_api()
            response = api.getCandleData(payload)

        if not response or not response.get("status") or not response.get("data"):
            return None

        candles = response["data"]
        df = pd.DataFrame(
            candles,
            columns=["Timestamp", "Open", "High", "Low", "Close", "Volume"]
        )

        df["Date"] = pd.to_datetime(df["Timestamp"])
        # If timezone aware, convert to naive UTC or local date
        if df["Date"].dt.tz is not None:
            df["Date"] = df["Date"].dt.tz_localize(None)

        df.set_index("Date", inplace=True)
        df.drop(columns=["Timestamp"], inplace=True)

        # Ensure correct numeric types
        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce").fillna(0).astype(int)

        if dropna_cols:
            valid_cols = [c for c in dropna_cols if c in df.columns]
            if valid_cols:
                df = df.dropna(subset=valid_cols)

        return df.sort_index()

    def get_ticker_info(self, symbol: str, exchange: str = "NSE") -> Dict[str, Any]:
        """
        Fetch real-time quote, traded volume, and market data via Angel One getMarketData API.
        """
        api = self._get_api()
        clean_sym = InstrumentMaster.clean_symbol(symbol)
        token = InstrumentMaster.get_token(clean_sym, exchange)

        if not token:
            return {"symbol": symbol}

        try:
            res = api.getMarketData("FULL", {exchange.upper(): [str(token)]})
            if res and res.get("status") and res.get("data", {}).get("fetched"):
                item = res["data"]["fetched"][0]
                return {
                    "symbol": symbol,
                    "currentPrice": item.get("ltp"),
                    "open": item.get("open"),
                    "dayHigh": item.get("high"),
                    "dayLow": item.get("low"),
                    "regularMarketPreviousClose": item.get("close"),
                    "regularMarketVolume": item.get("tradeVolume"),
                    "avgPrice": item.get("avgPrice"),
                    "52WeekHigh": item.get("52WeekHigh"),
                    "52WeekLow": item.get("52WeekLow"),
                    "totalBuyQuantity": item.get("totBuyQuan"),
                    "totalSellQuantity": item.get("totSellQuan"),
                    "netChange": item.get("netChange"),
                    "percentChange": item.get("percentChange"),
                    "deliveryQuantity": None,
                    "floatShares": None,
                    "sharesOutstanding": None,
                }

            # Fallback to ltpData if FULL market data is empty
            tradingsymbol = f"{clean_sym}-EQ"
            ltp_res = api.ltpData(exchange=exchange.upper(), tradingsymbol=tradingsymbol, symboltoken=str(token))
            if ltp_res and ltp_res.get("status") and ltp_res.get("data"):
                data = ltp_res["data"]
                return {
                    "symbol": symbol,
                    "currentPrice": data.get("ltp"),
                    "open": data.get("open"),
                    "dayHigh": data.get("high"),
                    "dayLow": data.get("low"),
                    "regularMarketPreviousClose": data.get("close"),
                    "regularMarketVolume": None,
                    "deliveryQuantity": None,
                    "floatShares": None,
                    "sharesOutstanding": None,
                }
            return {"symbol": symbol}
        except Exception as e:
            print(f"[WARN] Angel One get_ticker_info failed for {symbol}: {e}")
            return {"symbol": symbol}
