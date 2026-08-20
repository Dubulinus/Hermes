"""
src/ingestion/ohlcv.py

Downloads OHLCV data via yfinance and stores it as Parquet files.

Usage:
    python ohlcv.py

Notes:
    - Hourly data from Yahoo Finance is limited to the last ~730 days.
      Daily data has much longer history (decades).
    - Each ticker is saved as its own parquet file under data/raw/ohlcv/,
      so re-running the script only touches the tickers you ask for.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

# --- Config -----------------------------------------------------------

TICKERS = [
    "AAPL",
    "MSFT",
    "SPY",
    # doplň si vlastní seznam
]

INTERVAL = "1h"  # "1m","5m","15m","1h","1d", ... (viz yfinance docs)
PERIOD = "730d"  # max pro 1h interval; pro "1d" muzes dat "max"

OUTPUT_DIR = Path("data/raw/ohlcv")

# --- Logging ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def download_ticker(ticker: str, interval: str, period: str) -> pd.DataFrame | None:
    """Stahne OHLCV data pro jeden ticker. Vrati None pri chybe/prazdnych datech."""
    try:
        df = yf.download(
            ticker,
            interval=interval,
            period=period,
            auto_adjust=True,
            progress=False,
        )
    except Exception as e:
        logger.error(f"{ticker}: fetch failed - {e}")
        return None

    if df is None or df.empty:
        logger.warning(f"{ticker}: no data returned (spatny ticker? delisted?)")
        return None

    # yfinance obcas vraci MultiIndex sloupce (Price, Ticker) - sjednotime
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "timestamp"
    df = df.reset_index()
    df["ticker"] = ticker

    return df


def save_parquet(df: pd.DataFrame, ticker: str, interval: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{ticker}_{interval}.parquet"
    df.to_parquet(path, index=False)
    return path


def download_ohlcv(
    tickers: list[str],
    interval: str = INTERVAL,
    period: str = PERIOD,
    out_dir: Path = OUTPUT_DIR,
) -> dict[str, Path]:
    """Stahne OHLCV pro seznam tickeru, ulozi kazdy jako samostatny parquet."""
    saved: dict[str, Path] = {}

    for ticker in tickers:
        logger.info(f"Stahuji {ticker} ({interval}, {period})...")
        df = download_ticker(ticker, interval, period)

        if df is None:
            continue

        path = save_parquet(df, ticker, interval, out_dir)
        saved[ticker] = path
        logger.info(f"{ticker}: ulozeno {len(df)} radku -> {path}")

    logger.info(f"Hotovo. Uspesne staženo {len(saved)}/{len(tickers)} tickeru.")
    return saved


if __name__ == "__main__":
    from src.utils.config import load_settings

    settings = load_settings()
    universe = settings.get("universe", {})
    tickers = universe.get("equities", []) + universe.get("benchmarks", [])
    download_ohlcv(tickers, INTERVAL, PERIOD, OUTPUT_DIR)
