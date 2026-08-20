"""
src/ingestion/yfinance_collector.py

Alternative program for downloading OHLCV data via yfinance, adhering to the 6 iron rules:

1. UTC Standard: All datetime objects normalized to UTC timezone-aware.
2. Inherits from BaseFetcher for consistent interface.
3. Saves data to data/raw/ohlcv/ using the base class save method.
4. Logs errors and returns None on failure (no silent failures).
5. Does not make assumptions beyond the data provided by yfinance.
6. Each ticker saved as its own parquet file for efficient re-runs.

Usage:
    python yfinance_collector.py

Notes:
    - Hourly data from Yahoo Finance is limited to the last ~730 days.
    - Daily data has much longer history (decades).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
import yfinance as yf

from src.ingestion.base import BaseFetcher

# --- Config -----------------------------------------------------------

# Default interval and period (can be overridden in fetch calls)
DEFAULT_INTERVAL = "1h"  # "1m","5m","15m","1h","1d", ... (see yfinance docs)
DEFAULT_PERIOD = "730d"  # max for 1h interval; for "1d" can use "max"

# --- Logging ----------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class YFinanceCollector(BaseFetcher):
    """Downloads OHLCV data via yfinance, adhering to project conventions."""

    category = "ohlcv"

    def fetch(self, ticker: str, interval: str, period: str) -> pd.DataFrame | None:
        """
        Download OHLCV data for one ticker.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g., "AAPL").
        interval : str
            Data interval (e.g., "1h", "1d").
        period : str
            Period of data to download (e.g., "730d", "max").

        Returns
        -------
        pandas.DataFrame | None
            DataFrame with columns: timestamp (UTC), open, high, low, close, volume, ticker.
            Returns None on failure or empty data.
        """
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
            logger.warning(f"{ticker}: no data returned (invalid ticker? delisted?)")
            return None

        # yfinance sometimes returns MultiIndex columns (Price, Ticker) - unify
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Ensure the index is timezone-aware and in UTC
        # yfinance returns timezone-naive index for some data? We make it UTC.
        if df.index.tz is None:
            # If naive, localize to UTC
            df.index = df.index.tz_localize("UTC")
        else:
            # If already timezone-aware, convert to UTC
            df.index = df.index.tz_convert("UTC")

        # Reset index to make timestamp a column
        df.index.name = "timestamp"
        df = df.reset_index()

        # Add ticker column for identification (consistent with existing ohlcv.py)
        df["ticker"] = ticker

        # Reorder columns to have timestamp first
        cols = ["timestamp", "ticker"] + [c for c in df.columns if c not in ["timestamp", "ticker"]]
        df = df[cols]

        return df

    def save_data(self, df: pd.DataFrame, ticker: str, interval: str, out_dir: Path | None = None) -> Path:
        """
        Save DataFrame as parquet in data/raw/ohlcv/ using the base class save method.

        Parameters
        ----------
        df : pd.DataFrame
            Data to save.
        ticker : str
            Ticker symbol.
        interval : str
            Data interval.
        out_dir : Path | None
            Output directory. If None, uses base class default (data/raw/ohlcv/).

        Returns
        -------
        Path
            Path to the saved file.
        """
        # Use the base class save method, which expects a filename and optional directory
        filename = f"{ticker}_{interval}"
        return self.save(df, filename, out_dir=out_dir)


def download_ohlcv(
    tickers: list[str],
    interval: str = DEFAULT_INTERVAL,
    period: str = DEFAULT_PERIOD,
    out_dir: Path | None = None,
) -> dict[str, Path]:
    """
    Download OHLCV for a list of tickers, saving each as a separate parquet file.

    Parameters
    ----------
    tickers : list[str]
        List of ticker symbols.
    interval : str
        Data interval (default: "1h").
    period : str
        Period of data to download (default: "730d").
    out_dir : Path | None
        Output directory. If None, uses collector's default (data/raw/ohlcv/).

    Returns
    -------
    dict[str, Path]
        Mapping of ticker to saved file path.
    """
    collector = YFinanceCollector()
    saved: dict[str, Path] = {}

    for ticker in tickers:
        logger.info(f"Downloading {ticker} ({interval}, {period})...")
        df = collector.fetch(ticker, interval, period)

        if df is None:
            continue

        path = collector.save_data(df, ticker, interval, out_dir)
        saved[ticker] = path
        logger.info(f"{ticker}: saved {len(df)} rows -> {path}")

    logger.info(f"Finished. Successfully downloaded {len(saved)}/{len(tickers)} tickers.")
    return saved


if __name__ == "__main__":
    from src.utils.config import load_settings

    settings = load_settings()
    universe = settings.get("universe", {})
    tickers = universe.get("equities", []) + universe.get("benchmarks", [])
    download_ohlcv(tickers, DEFAULT_INTERVAL, DEFAULT_PERIOD)