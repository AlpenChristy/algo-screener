-- Supabase SQL Schema Migration for AlgoScreener Pro
-- Table: signal_history
-- Description: Stores daily stock signals and close calls with deduplication logic.

CREATE TABLE IF NOT EXISTS signal_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(50) NOT NULL,
    ticker VARCHAR(50) NOT NULL,
    strategy_type VARCHAR(50) NOT NULL, -- '52w-low' or '30-dma'
    record_date DATE NOT NULL,          -- e.g. '2026-08-18'
    status VARCHAR(20) NOT NULL,        -- 'SIGNAL' or 'CLOSE_CALL'
    close_price NUMERIC(12, 2),
    benchmark_value NUMERIC(12, 2),     -- 52W Low or 30-DMA price level
    distance_pct NUMERIC(8, 2),         -- % distance from benchmark
    volume BIGINT,
    prev_volume BIGINT,
    volume_multiple NUMERIC(8, 2),
    is_near_level BOOLEAN DEFAULT FALSE,
    is_vol_spike BOOLEAN DEFAULT FALSE,
    scan_time TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Composite Unique Constraint for daily deduplication per symbol and strategy
    CONSTRAINT uq_symbol_strategy_date UNIQUE (symbol, strategy_type, record_date)
);

-- Indices for performance optimizations
CREATE INDEX IF NOT EXISTS idx_signal_history_date ON signal_history(record_date DESC);
CREATE INDEX IF NOT EXISTS idx_signal_history_symbol ON signal_history(symbol);
CREATE INDEX IF NOT EXISTS idx_signal_history_strategy ON signal_history(strategy_type);
CREATE INDEX IF NOT EXISTS idx_signal_history_status ON signal_history(status);
