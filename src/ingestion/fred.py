"""
src/ingestion/fred.py

Stahuje makro casove rady z FRED (Federal Reserve Economic Data).
Potrebuje FRED_API_KEY v config/secrets.env - zdarma na
https://fred.stlouisfed.org/docs/api/api_key.html

Seznam series (DGS10, CPIAUCSL, UNRATE...) se bere z config/settings.yaml,
sekce fred.series. Plny seznam dostupnych series ID: https://fred.stlouisfed.org
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from src.ingestion.base import BaseFetcher
from src.utils.config import load_settings, get_secret
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

FRED_URL = "https://api.stlouisfed.org/fred/series/observations"


class FredFetcher(BaseFetcher):
    """Stahuje jednu FRED time series."""

    category = "fred"

    def fetch(self, series_id: str) -> pd.DataFrame | None:
        api_key = get_secret("FRED_API_KEY")
        if not api_key:
            raise ValueError(
                "FRED_API_KEY chybi v config/secrets.env. "
                "Zdarma klic ziskas na fred.stlouisfed.org/docs/api/api_key.html"
            )

        params = {
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
        }

        try:
            resp = requests.get(FRED_URL, params=params)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"{series_id}: fetch selhal - {e}")
            return None

        data = resp.json()
        observations = data.get("observations", [])
        if not observations:
            logger.warning(f"{series_id}: zadna data nenalezena.")
            return None

        df = pd.DataFrame(observations)
        df = df[["date", "value"]].rename(columns={"date": "timestamp"})
        # FRED oznacuje chybejici hodnoty jako "." - prevedeme na skutecne NaN
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df["series_id"] = series_id

        logger.info(f"{series_id}: staženo {len(df)} pozorovani.")
        return df


def download_fred_data(series_ids: list[str]) -> None:
    fetcher = FredFetcher()
    for series_id in series_ids:
        df = fetcher.fetch(series_id)
        if df is not None:
            fetcher.save(df, series_id)
        time.sleep(
            0.2
        )  # slusnost vuci free API, zadny tvrdy limit ale netreba spamovat


if __name__ == "__main__":
    settings = load_settings()
    series_ids = settings.get("fred", {}).get("series", ["DGS10", "CPIAUCSL", "UNRATE"])
    download_fred_data(series_ids)
