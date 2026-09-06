"""
Database Access Layer
"""
from .supabase_client import (
    supabase_client,
    upsert_signal_record,
    get_signal_history,
    get_history_stats,
)

__all__ = [
    "supabase_client",
    "upsert_signal_record",
    "get_signal_history",
    "get_history_stats",
]
