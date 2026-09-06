import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add backend directory to sys.path to enable smooth python module imports
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import APP_TITLE, APP_VERSION, FRONTEND_DIST
from app.api.routes_screener import router as screener_router
from app.api.routes_backtest import router as backtest_router
from app.api.routes_data import router as data_router

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# ── CORS ─────────────────────────────────────────────────────────────────────
# Allow Cloudflare Pages domain + localhost dev.
# In production set ALLOWED_ORIGINS env var to your Cloudflare Pages URL.
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Always allow localhost variants for local development
ALLOWED_ORIGINS += [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(screener_router)
app.include_router(backtest_router)
app.include_router(data_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": APP_VERSION}


# ── Static frontend (only when running combined locally) ──────────────────────
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
