import json
import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.engines.screener_engine import run_screener_async

router = APIRouter(tags=["Screener"])


@router.get("/api/screener/stream")
async def screener_sse(
    strategy_type: str = Query("52w-low"),
    universe_name: str = Query("nifty100.csv"),
    params_json: str = Query("{}"),
):
    """
    Server-Sent Events endpoint for real-time screener progress.
    Works through all HTTP proxies (Render, Cloudflare) unlike WebSockets.
    """
    try:
        params = json.loads(params_json)
    except json.JSONDecodeError:
        params = {}

    async def event_stream():
        try:
            async for event in run_screener_async(strategy_type, universe_name, params):
                # SSE format: "data: <json>\n\n"
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disables nginx/Render buffering
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ── Keep WebSocket endpoint as fallback for local dev ─────────────────────────
from fastapi import WebSocket, WebSocketDisconnect
from app.engines.screener_engine import run_screener_async as _run_async


@router.websocket("/ws/screener")
async def websocket_screener(websocket: WebSocket):
    await websocket.accept()
    try:
        init_data = await websocket.receive_text()
        config = json.loads(init_data)

        strategy_type = config.get("strategy_type", "52w-low")
        universe_name = config.get("universe_name", "nifty100.csv")
        params = config.get("params", {})

        async for event in _run_async(strategy_type, universe_name, params):
            await websocket.send_text(json.dumps(event))

    except WebSocketDisconnect:
        print("[INFO] Client disconnected from WebSocket screener")
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
