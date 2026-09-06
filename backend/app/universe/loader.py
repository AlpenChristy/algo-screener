import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
from app.config import UNIVERSES_DIR, DATA_DIR


def resolve_universe_path(universe_name: str) -> Path:
    """
    Resolve universe file path, checking universes subfolder and root data dir.
    """
    if not universe_name.endswith(".csv"):
        universe_name += ".csv"

    # Check backend/data/universes/
    target = UNIVERSES_DIR / universe_name
    if target.exists():
        return target

    # Check backend/data/
    target_data = DATA_DIR / universe_name
    if target_data.exists():
        return target_data

    # Fallback to nifty100.csv
    fallback = UNIVERSES_DIR / "nifty100.csv"
    if fallback.exists():
        return fallback
    return DATA_DIR / "nifty100.csv"


def load_symbols(csv_path: str | Path, symbol_col: Optional[str] = None) -> List[str]:
    """
    Load list of stock symbols from CSV file.
    """
    path = Path(csv_path)
    if not path.exists():
        path = resolve_universe_path(path.name)

    if not path.exists():
        raise FileNotFoundError(f"Universe CSV file not found: {csv_path}")

    df = pd.read_csv(path)

    if symbol_col is None:
        candidates = [c for c in df.columns if str(c).strip().lower() in
                      ("symbol", "symbols", "ticker", "tickers", "scrip", "stock")]
        if not candidates:
            raise ValueError(f"Could not auto-detect symbol column in {list(df.columns)}")
        symbol_col = candidates[0]

    symbols = (
        df[symbol_col]
        .dropna()
        .astype(str)
        .str.strip()
        .str.upper()
        .unique()
        .tolist()
    )
    return symbols


def list_available_universes() -> List[Dict[str, Any]]:
    """
    List all available universe CSV files in backend/data and backend/data/universes.
    """
    universes = {}
    search_dirs = [UNIVERSES_DIR, DATA_DIR]

    for d in search_dirs:
        if d.exists():
            for f in os.listdir(d):
                if f.endswith(".csv") and not f.startswith("backtest_"):
                    if f not in universes:
                        clean_name = f.replace(".csv", "").replace("_", " ").replace("-", " ").title()
                        universes[f] = {
                            "id": f,
                            "name": clean_name,
                            "filename": f,
                        }
    return list(universes.values())
