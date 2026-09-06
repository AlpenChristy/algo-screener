from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engines.backtest_engine import run_backtest_service

router = APIRouter(prefix="/api", tags=["Backtest"])


class BacktestRequest(BaseModel):
    strategy_type: str
    universe_name: str
    params: Dict[str, Any]


@router.post("/run-backtest")
def api_run_backtest(req: BacktestRequest):
    try:
        results = run_backtest_service(
            strategy_type=req.strategy_type,
            universe_name=req.universe_name,
            params=req.params,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
