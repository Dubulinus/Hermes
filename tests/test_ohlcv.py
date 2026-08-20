"""
tests/test_ohlcv.py

Priklad testu - overuje, ze download_ticker() spravne zachazi s chybami
(spatny ticker) a ze save_parquet() vytvori soubor se spravnym obsahem.

Toto je KOSTRA testu, ne hotovy test - doplnime az bude ohlcv.py stabilni.
Spusteni: pytest tests/
"""

import pandas as pd

from src.ingestion.ohlcv import download_ticker


def test_invalid_ticker_returns_none():
    """Neexistujici ticker by mel vratit None, ne spadnout."""
    result = download_ticker("TOTO_TICKER_NEEXISTUJE_XYZ", interval="1d", period="5d")
    assert result is None


def test_valid_ticker_returns_dataframe():
    """Platny ticker by mel vratit neprazdny DataFrame se spravnymi sloupci."""
    result = download_ticker("AAPL", interval="1d", period="5d")
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert "timestamp" in result.columns
    assert "ticker" in result.columns
