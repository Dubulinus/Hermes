"""
src/ingestion/base.py

Spolecne rozhrani pro vsechny data fetchery (ohlcv, sec_edgar, fred, weather...).
Cil: kazdy fetcher ma stejny "tvar" - snadno se pak kombinuji a testuji.

Konvence:
    - Kazdy fetcher vraci pandas.DataFrame se sloupcem "timestamp" (UTC) jako casovou osou.
    - Kazdy fetcher ma vlastni save_* funkci, ktera uklada do data/raw/<kategorie>/.
    - Zadny fetcher nesmi tise selhat - pri chybe se loguje a vraci None,
      volajici kod rozhoduje, co s tim (retry, skip, crash).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseFetcher(ABC):
    """Spolecny predek pro vsechny data fetchery."""

    #: podslozka v data/raw/, kam tento fetcher uklada (napr. "ohlcv", "sec_edgar")
    category: str = "unknown"

    @abstractmethod
    def fetch(self, *args, **kwargs) -> pd.DataFrame | None:
        """Stahne data a vrati DataFrame, nebo None pri chybe/prazdnem vysledku."""
        raise NotImplementedError

    def save(self, df: pd.DataFrame, filename: str, out_dir: Path | None = None) -> Path:
        """Ulozi DataFrame jako parquet do data/raw/<category>/<filename>.parquet."""
        from src.utils.config import PROJECT_ROOT

        base_dir = out_dir or (PROJECT_ROOT / "data" / "raw" / self.category)
        base_dir.mkdir(parents=True, exist_ok=True)

        path = base_dir / f"{filename}.parquet"
        df.to_parquet(path, index=False)
        return path
