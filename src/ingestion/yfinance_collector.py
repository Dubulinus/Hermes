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
import os
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

from src.ingestion.base import BaseFetcher
from src.utils.config import PROJECT_ROOT

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

    def fetch(
        self,
        ticker: str,
        interval: str,
        period: str | None = None,
        start: pd.Timestamp | None = None,
    ) -> pd.DataFrame | None:
        """
        Download OHLCV data for one ticker.

        Parameters
        ----------
        ticker : str
            Ticker symbol (e.g., "AAPL").
        interval : str
            Data interval (e.g., "1h", "1d").
        period : str | None
            Period of data to download (e.g., "730d", "max"). Used when
            ``start`` is not provided.
        start : pandas.Timestamp | None
            Download data starting at this timestamp. Takes precedence over
            ``period``.

        Returns
        -------
        pandas.DataFrame | None
            DataFrame with columns: timestamp (UTC), open, high, low, close, volume, ticker.
            Returns None on failure or empty data.
        """
        try:
            if start is not None:
                df = yf.download(
                    ticker,
                    interval=interval,
                    start=start,
                    auto_adjust=True,
                    progress=False,
                )
            elif period is not None:
                df = yf.download(
                    ticker,
                    interval=interval,
                    period=period,
                    auto_adjust=True,
                    progress=False,
                )
            else:
                raise ValueError("Either period or start must be provided")
        except (
            KeyError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            requests.RequestException,
        ) as error:
            logger.error(f"{ticker}: fetch failed - {error}")
            return None

        if df is None or df.empty:
            logger.warning(f"{ticker}: no data returned (invalid ticker? delisted?)")
            return None

        # yfinance sometimes returns MultiIndex columns (Price, Ticker) - unify
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Ensure the index is timezone-aware and in UTC.
        datetime_index = pd.DatetimeIndex(df.index)
        if datetime_index.tz is None:
            # If naive, localize to UTC
            df.index = datetime_index.tz_localize("UTC")
        else:
            # If already timezone-aware, convert to UTC
            df.index = datetime_index.tz_convert("UTC")

        # Reset index to make timestamp a column
        df.index.name = "timestamp"
        df = df.reset_index()

        # Add ticker column for identification (consistent with existing ohlcv.py)
        df["ticker"] = ticker

        # Reorder columns to have timestamp first
        cols = ["timestamp", "ticker"] + [
            c for c in df.columns if c not in ["timestamp", "ticker"]
        ]
        df = df[cols]

        return df

    def save_data(
        self, df: pd.DataFrame, ticker: str, interval: str, out_dir: Path | None = None
    ) -> Path:
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
        filename = f"{ticker}_{interval}"
        base_dir = out_dir or (PROJECT_ROOT / "data" / "raw" / self.category)
        base_dir.mkdir(parents=True, exist_ok=True)
        path = base_dir / f"{filename}.parquet"
        temporary_path = base_dir / f".{filename}.tmp.parquet"

        try:
            df.to_parquet(temporary_path, index=False)
            os.replace(temporary_path, path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()

        return path


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
    target_dir = out_dir or (PROJECT_ROOT / "data" / "raw" / collector.category)

    for ticker in tickers:
        target_path = target_dir / f"{ticker}_{interval}.parquet"
        existing_df: pd.DataFrame | None = None

        if target_path.exists():
            existing_df = pd.read_parquet(target_path)
            latest_timestamp = pd.to_datetime(existing_df["timestamp"], utc=True).max()
            logger.info(
                f"Downloading {ticker} ({interval}, start={latest_timestamp})..."
            )
            df = collector.fetch(ticker, interval, start=latest_timestamp)
        else:
            logger.info(f"Downloading {ticker} ({interval}, {period})...")
            df = collector.fetch(ticker, interval, period=period)

        if df is None:
            if existing_df is not None:
                logger.info(f"{ticker}: up to date")
            continue

        if existing_df is not None:
            df = pd.concat([existing_df, df], ignore_index=True)
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df = (
                df.drop_duplicates(subset=["timestamp"], keep="last")
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

        path = collector.save_data(df, ticker, interval, out_dir)
        saved[ticker] = path
        logger.info(f"{ticker}: saved {len(df)} rows -> {path}")

    logger.info(
        f"Finished. Successfully downloaded {len(saved)}/{len(tickers)} tickers."
    )
    return saved


if __name__ == "__main__":
    from src.utils.config import load_settings

    settings = load_settings()
    universe = settings.get("universe", {})
    tickers = universe.get("equities", []) + universe.get("benchmarks", [])
    download_ohlcv(tickers, DEFAULT_INTERVAL, DEFAULT_PERIOD)
