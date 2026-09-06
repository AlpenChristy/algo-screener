from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import pandas as pd
from app.universe.loader import load_symbols


class BaseStrategy(ABC):
    """
    Abstract Base Class for Screener & Backtest Strategies.
    """
    strategy_id: str = "base"
    name: str = "Base Strategy"
    description: str = ""

    @abstractmethod
    def analyze_stock(self, symbol: str, **kwargs) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def run_backtest(self, symbols: List[str], **kwargs) -> Optional[pd.DataFrame]:
        pass
