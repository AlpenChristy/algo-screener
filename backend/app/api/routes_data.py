import os
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Response, Query, HTTPException
from pydantic import BaseModel
import pandas as pd

from app.config import DATA_DIR, UNIVERSES_DIR
from app.universe.loader import list_available_universes
from app.data.market_data import fetch_history
from app.engines.export_engine import export_to_excel, export_to_csv
from app.db.supabase_client import get_signal_history, get_history_stats

router = APIRouter(prefix="/api", tags=["Data & Utilities"])


class ExportRequest(BaseModel):
    format: str  # "excel" or "csv"
    data: List[Dict[str, Any]]
    title: Optional[str] = "Screener_Results"


@router.get("/universes")
def get_universes():
    return list_available_universes()


@router.post("/upload-universe")
async def upload_universe(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    UNIVERSES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UNIVERSES_DIR / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return {"status": "success", "filename": file.filename}


@router.post("/export")
def api_export(req: ExportRequest):
    filename = f"{req.title}.{'xlsx' if req.format == 'excel' else 'csv'}"
    if req.format == "excel":
        file_bytes = export_to_excel(req.data, title=req.title)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        file_bytes = export_to_csv(req.data)
        media_type = "text/csv"

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stock-history")
def get_stock_history(symbol: str = Query(...), exchange_suffix: str = Query(".NS")):
    ticker_symbol = f"{symbol}{exchange_suffix}"
    try:
        hist = fetch_history(
            ticker_symbol,
            period="6mo",
            interval="1d",
            auto_adjust=False,
            dropna_cols=["Close"],
            raise_errors=True,
        )
        if hist is None or hist.empty:
            return {"symbol": symbol, "history": []}
        hist["30_dma"] = hist["Close"].rolling(window=30).mean()
        hist["52w_low"] = hist["Low"].cummin()

        records = []
        for date, row in hist.iterrows():
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
                "dma30": round(float(row["30_dma"]), 2) if not pd.isna(row["30_dma"]) else None,
                "low52w": round(float(row["52w_low"]), 2) if not pd.isna(row["52w_low"]) else None,
            })
        return {"symbol": symbol, "history": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
def api_get_history(
    strategy_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
):
    return get_signal_history(
        strategy_type=strategy_type,
        status=status,
        symbol=symbol,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get("/history/stats")
def api_get_history_stats():
    return get_history_stats()
