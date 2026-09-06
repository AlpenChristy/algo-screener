from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any
import pandas as pd


class BaseDataProvider(ABC):
    """
    Abstract Base Class defining the standardized interface for all Market Data Providers
    (Angel One, Fyers, Yahoo Finance, etc.).

    All providers must guarantee return values conforming to the standardized OHLCV schema:
    - Index: pd.DatetimeIndex with name 'Date'
    - Columns: ['Open', 'High', 'Low', 'Close', 'Volume']
    - Chronologically sorted in ascending order
    """

    @abstractmethod
    def fetch_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical candle data for a given relative period (e.g. '1mo', '6mo', '1y', '18mo').
        """
        pass

    def get_historical_data(
        self,
        symbol: str,
        start_date: str | datetime,
        end_date: str | datetime,
        interval: str = "1d",
        auto_adjust: bool = False,
        dropna_cols: Optional[List[str]] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical candle data for explicit start and end dates.
        Default implementation delegates to fetch_history or calculates period.
        """
        return self.fetch_history(
            symbol=symbol,
            period="1y",
            interval=interval,
            auto_adjust=auto_adjust,
            dropna_cols=dropna_cols,
        )

    @abstractmethod
    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch standardized real-time market quote and metadata for a given symbol.
        Standard keys returned:
        - symbol: str
        - currentPrice: float | None
        - open: float | None
        - dayHigh: float | None
        - dayLow: float | None
        - regularMarketPreviousClose: float | None
        - regularMarketVolume: int | float | None
        - deliveryQuantity: int | float | None
        - floatShares: int | float | None
        - sharesOutstanding: int | float | None
        """
        pass
