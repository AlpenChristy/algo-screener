import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.config import SUPABASE_URL, SUPABASE_KEY

supabase_client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"[INFO] Connected to Supabase at {SUPABASE_URL}")
    except Exception as e:
        print(f"[WARN] Failed to initialize Supabase client: {e}")


def upsert_signal_record(stock_res: Dict[str, Any], strategy_type: str) -> Optional[Dict[str, Any]]:
    if not stock_res or not supabase_client:
        return None

    is_signal = stock_res.get("signal", False)
    is_near = stock_res.get("near_52w_low", False) or stock_res.get("near_30_dma", False)
    is_vol_spike = stock_res.get("volume_spike", False)

    if is_signal:
        status = "SIGNAL"
    elif is_near or is_vol_spike:
        status = "CLOSE_CALL"
    else:
        return None

    if strategy_type == "52w-low":
        benchmark_val = stock_res.get("52w_low")
        distance_pct = stock_res.get("pct_above_52w_low")
    else:
        benchmark_val = stock_res.get("30_dma")
        distance_pct = stock_res.get("pct_from_30_dma")

    record_date = stock_res.get("date") or datetime.now().strftime("%Y-%m-%d")

    payload = {
        "symbol": stock_res["symbol"],
        "ticker": stock_res.get("ticker", stock_res["symbol"]),
        "strategy_type": strategy_type,
        "record_date": record_date,
        "status": status,
        "close_price": stock_res.get("close"),
        "benchmark_value": benchmark_val,
        "distance_pct": distance_pct,
        "volume": stock_res.get("volume"),
        "prev_volume": stock_res.get("prev_volume"),
        "volume_multiple": stock_res.get("volume_multiple"),
        "is_near_level": is_near,
        "is_vol_spike": is_vol_spike,
        "scan_time": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    try:
        response = supabase_client.table("signal_history").upsert(
            payload,
            on_conflict="symbol,strategy_type,record_date"
        ).execute()
        return response.data[0] if response.data else payload
    except Exception as e:
        print(f"[WARN] Supabase upsert error for {stock_res.get('symbol')}: {e}")
        return None


def get_signal_history(
    strategy_type: Optional[str] = None,
    status: Optional[str] = None,
    symbol: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    if not supabase_client:
        return {"records": [], "total": 0, "error": "Supabase client not connected"}

    try:
        query = supabase_client.table("signal_history").select("*", count="exact")

        if strategy_type and strategy_type != "all":
            query = query.eq("strategy_type", strategy_type)

        if status and status != "all":
            query = query.eq("status", status)

        if symbol and symbol.strip():
            query = query.ilike("symbol", f"%{symbol.strip()}%")

        if date_from:
            query = query.gte("record_date", date_from)

        if date_to:
            query = query.lte("record_date", date_to)

        query = query.order("record_date", desc=True).order("scan_time", desc=True)
        query = query.range(offset, offset + limit - 1)

        res = query.execute()

        return {
            "records": res.data or [],
            "total": res.count if res.count is not None else len(res.data or []),
        }
    except Exception as e:
        print(f"[WARN] Error fetching signal history from Supabase: {e}")
        return {"records": [], "total": 0, "error": str(e)}


def get_history_stats() -> Dict[str, Any]:
    if not supabase_client:
        return {
            "total_records": 0,
            "total_signals": 0,
            "total_close_calls": 0,
            "today_signals": 0,
            "today_close_calls": 0,
            "db_connected": False,
        }

    try:
        today_str = datetime.now().strftime("%Y-%m-%d")

        all_res = supabase_client.table("signal_history").select("status, record_date", count="exact").execute()
        records = all_res.data or []

        total_signals = sum(1 for r in records if r.get("status") == "SIGNAL")
        total_close_calls = sum(1 for r in records if r.get("status") == "CLOSE_CALL")

        today_signals = sum(1 for r in records if r.get("status") == "SIGNAL" and r.get("record_date") == today_str)
        today_close_calls = sum(1 for r in records if r.get("status") == "CLOSE_CALL" and r.get("record_date") == today_str)

        return {
            "total_records": len(records),
            "total_signals": total_signals,
            "total_close_calls": total_close_calls,
            "today_signals": today_signals,
            "today_close_calls": today_close_calls,
            "db_connected": True,
        }
    except Exception as e:
        print(f"[WARN] Error fetching history stats: {e}")
        return {
            "total_records": 0,
            "total_signals": 0,
            "total_close_calls": 0,
            "today_signals": 0,
            "today_close_calls": 0,
            "db_connected": False,
            "error": str(e),
        }
