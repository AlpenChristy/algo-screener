import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project directories
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
ROOT_DIR = BACKEND_DIR.parent

# Load environment variables
load_dotenv(BACKEND_DIR / ".env")
load_dotenv(ROOT_DIR / ".env")
load_dotenv()

# Application Constants
APP_TITLE = "AlgoScreener Pro API"
APP_VERSION = "1.0.0"

# Directories
DATA_DIR = BACKEND_DIR / "data"
UNIVERSES_DIR = DATA_DIR / "universes"
CACHE_DIR = DATA_DIR / "cache"
FRONTEND_DIST = ROOT_DIR / "frontend" / "dist"

# Ensure required directories exist
UNIVERSES_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")

# AngelOne Credentials
ANGELONE_API_KEY = os.getenv("ANGELONE_API_KEY", "hS8rUbdC")
ANGELONE_CLIENT_CODE = os.getenv("ANGELONE_CLIENT_CODE", "AABO314616")
ANGELONE_PIN = os.getenv("ANGELONE_PIN", "0371")
ANGELONE_TOTP_SECRET = os.getenv("ANGELONE_TOTP_SECRET", "UVCFBM3PTLSOBWJYJKPTQ4ITCE")

# Fyers Credentials
FYERS_CLIENT_ID = os.getenv("FYERS_CLIENT_ID")
FYERS_SECRET_KEY = os.getenv("FYERS_SECRET_KEY")
FYERS_REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI", "http://127.0.0.1:8000/api/fyers/callback")
FYERS_ACCESS_TOKEN = os.getenv("FYERS_ACCESS_TOKEN")

# Default Market Data Provider ('yfinance', 'fyers', 'angelone')
MARKET_DATA_PROVIDER = os.getenv("MARKET_DATA_PROVIDER", "fyers").lower()
