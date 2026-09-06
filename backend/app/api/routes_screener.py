import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.engines.screener_engine import run_screener_generator

router = APIRouter(tags=["Screener"])


@router.websocket("/ws/screener")
async def websocket_screener(websocket: WebSocket):
    await websocket.accept()
    try:
        init_data = await websocket.receive_text()
        config = json.loads(init_data)

        strategy_type = config.get("strategy_type", "52w-low")
        universe_name = config.get("universe_name", "nifty100.csv")
        params = config.get("params", {})

        for event in run_screener_generator(strategy_type, universe_name, params):
            await websocket.send_text(json.dumps(event))

    except WebSocketDisconnect:
        print("[INFO] Client disconnected from WebSocket screener")
    except Exception as e:
        await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
