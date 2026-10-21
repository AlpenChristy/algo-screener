# Algo Screener & Backtester

> A personal algorithmic trading and market screening project designed to scan, analyze, and backtest quantitative trading strategies on Indian equities (NSE).

---

## What It Does

- **Real-Time Market Screener**: Scans Indian stock universes (Nifty 100, Nifty LargeMidcap 250, Nifty Smallcap 500, or user-uploaded CSVs) with live scan progress streamed via WebSockets.
- **Quantitative Strategy Scanning**: Evaluates technical and liquidity metrics including moving average proximity, 52-week price extremes, relative volume surges, and delivery percentages.
- **Historical Backtesting**: Runs historical simulations with configurable parameters (stop-loss, profit target, max holding period) and calculates win rate, P&L, Sharpe ratio, and drawdowns.
- **Signal History & Tracking**: Persists daily scan results and triggered signals into a database for historical review and tracking performance over time.
- **Interactive UI & Data Export**: Interactive charts and key metrics (float percentage, volume multiples, delivery share) with one-click export to CSV and Excel.

---

## Tech Stack

- **Frontend**: React 19, Vite, Tailwind CSS v4, Recharts, Lucide React
- **Backend**: Python 3, FastAPI, Uvicorn, WebSockets, Pandas, NumPy
- **Market Data & Abstraction**:
  - Multi-provider architecture supporting **Yahoo Finance** (`yfinance`), **Angel One** (SmartAPI), and **FYERS API**
  - **NSE Bhavcopy loader** for official daily delivery and traded quantity data
  - Automated broker instrument master mapping (symbol-to-token resolution)
- **Database**: Supabase (PostgreSQL)

---

## Where It Is Published

- **Repository**: [GitHub — AlpenChristy/algo-screener](https://github.com/AlpenChristy/algo-screener)
- **Frontend**: Deployed on **Cloudflare Pages** (configured with SPA fallback and API proxying)
- **Backend API**: Deployed on **Render** as a web service
- **Database**: Hosted on **Supabase**

---

## Strategies & Logic

### 1. 30-DMA + Volume Spike + Delivery (`30-dma`)
Captures momentum continuation and institutional accumulation near intermediate trend support.

**Logic & Entry Rules:**
- **Price Near 30-DMA**: Closing price is within **±2.0%** of its 30-Day Moving Average (`|Close - 30_DMA| / 30_DMA <= 2%`).
- **Volume Spike**: Current day's volume is between **1.5x and 2.5x** of the previous trading day's volume (`1.5 <= Volume / Prev_Volume <= 2.5`).
- **High Delivery Percentage**: Delivery volume is **≥ 50%** of total traded volume (sourced directly from NSE Bhavcopy), ensuring genuine institutional accumulation rather than pure intraday trading.
- **Signal Trigger**: Fires when all three conditions are satisfied on the same day.

### 2. 52-Week Low + Volume Spike (`52w-low`)
Identifies bottom-reversal and capitulation exhaustion setups at multi-month support levels.

**Logic & Entry Rules:**
- **Price Near 52-Week Low**: Closing price is within **2.0%** above its 52-week low over a 252 trading day lookback (`(Close - 52W_Low) / 52W_Low <= 2%`).
- **Abnormal Volume Expansion**: Current day's volume is between **3.0x and 4.0x** of the previous trading day's volume (`3.0 <= Volume / Prev_Volume <= 4.0`), reflecting high-volume absorption or capitulation at lows.
- **Signal Trigger**: Fires when both the 52-week low proximity and volume spike criteria are met.

### Backtesting Execution Model
Both strategies share a consistent trade execution and risk management model:
- **Stop-Loss**: 5.0% below entry price (configurable).
- **Target Profit**: 10.0% above entry price (configurable).
- **Time Stop**: 20 trading days max holding period (exits at market close if neither stop-loss nor target is triggered).
