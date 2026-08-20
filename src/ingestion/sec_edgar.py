"""
src/ingestion/sec_edgar.py

Stahuje data ze SEC EDGAR (data.sec.gov) - zdarma, ale vyzaduje smysluplnou
User-Agent hlavicku (jmeno + email), jinak SEC requesty blokuje.

Co stahuje:
    - CIK mapping: ticker -> SEC interni ID firmy (potreba pro vsechno ostatni)
    - Company facts: fundamentaly (rozvahy, vysledovky) jako XBRL data
    - Recent filings: seznam filings vc. Form 4 (insider trading),
      13D/13G (aktivisticti investori, >5% podil), 8-K (material events)

Pozn.: Form 4 tady stahuje jen METADATA (datum, typ, odkaz), ne detailni
obsah (kdo presne kolik koupil - to je v XML uvnitr filingu). To je
dalsi krok, az bude tohle overene a funkcni.
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

from src.ingestion.base import BaseFetcher
from src.utils.config import load_settings, PROJECT_ROOT
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

CIK_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
CIK_MAP_CACHE = PROJECT_ROOT / "data" / "cache" / "sec_cik_map.parquet"

# Filings, ktere nas zajimaji jako "whale" signaly
WHALE_FORMS = {"4", "13D", "13D/A", "13G", "13G/A", "8-K"}


def _get_headers() -> dict:
    """SEC vyzaduje smysluplny User-Agent, jinak vraci 403."""
    settings = load_settings()
    user_agent = settings.get("sec_edgar", {}).get("user_agent", "")
    if not user_agent or "your-email" in user_agent:
        raise ValueError(
            "Nastav sec_edgar.user_agent v config/settings.yaml na sve "
            "skutecne jmeno + email, SEC to vyzaduje."
        )
    return {"User-Agent": user_agent}


def get_cik_map(force_refresh: bool = False) -> pd.DataFrame:
    """
    Stahne/nacte mapovani ticker -> CIK. Cachuje lokalne, protoze se
    tento seznam meni jen zridka (nema smysl stahovat pri kazdem behu).
    """
    if CIK_MAP_CACHE.exists() and not force_refresh:
        return pd.read_parquet(CIK_MAP_CACHE)

    logger.info("Stahuji CIK mapping ze SEC...")
    resp = requests.get(CIK_MAP_URL, headers=_get_headers())
    resp.raise_for_status()

    raw = resp.json()  # format: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
    df = pd.DataFrame(raw.values())
    df["cik_str"] = (
        df["cik_str"].astype(str).str.zfill(10)
    )  # SEC chce 10-mistny CIK s nulami

    CIK_MAP_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(CIK_MAP_CACHE, index=False)
    return df


def get_cik_for_ticker(ticker: str) -> str | None:
    df = get_cik_map()
    match = df[df["ticker"] == ticker.upper()]
    if match.empty:
        logger.warning(f"{ticker}: CIK nenalezen v SEC mapovani.")
        return None
    return match.iloc[0]["cik_str"]


class SecFundamentalsFetcher(BaseFetcher):
    """Stahuje XBRL fundamentaly (rozvahy, vysledovky) pro ticker."""

    category = "sec_fundamentals"

    def fetch(self, ticker: str) -> pd.DataFrame | None:
        cik = get_cik_for_ticker(ticker)
        if cik is None:
            return None

        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        try:
            resp = requests.get(url, headers=_get_headers())
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"{ticker}: fetch fundamentals selhal - {e}")
            return None

        data = resp.json()
        facts = data.get("facts", {}).get("us-gaap", {})
        if not facts:
            logger.warning(f"{ticker}: zadna us-gaap fakta nenalezena.")
            return None

        # Rozbalime vsechny metriky (Revenues, Assets, NetIncomeLoss...) do jedne dlouhe tabulky
        rows = []
        for metric_name, metric_data in facts.items():
            for unit, entries in metric_data.get("units", {}).items():
                for entry in entries:
                    rows.append(
                        {
                            "ticker": ticker,
                            "metric": metric_name,
                            "unit": unit,
                            "value": entry.get("val"),
                            "start": entry.get("start"),
                            "end": entry.get("end"),
                            "fiscal_year": entry.get("fy"),
                            "fiscal_period": entry.get("fp"),
                            "form": entry.get("form"),
                            "filed": entry.get("filed"),
                        }
                    )

        df = pd.DataFrame(rows)
        logger.info(f"{ticker}: staženo {len(df)} fundamentalnich zaznamu.")
        return df


class SecFilingsFetcher(BaseFetcher):
    """Stahuje seznam poslednich filings (Form 4, 13D/13G, 8-K...) pro ticker."""

    category = "sec_filings"

    def fetch(self, ticker: str, forms: set[str] = WHALE_FORMS) -> pd.DataFrame | None:
        cik = get_cik_for_ticker(ticker)
        if cik is None:
            return None

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        try:
            resp = requests.get(url, headers=_get_headers())
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"{ticker}: fetch filings selhal - {e}")
            return None

        data = resp.json()
        recent = data.get("filings", {}).get("recent", {})
        if not recent:
            logger.warning(f"{ticker}: zadne recent filings nenalezeny.")
            return None

        df = pd.DataFrame(
            {
                "form": recent.get("form", []),
                "filing_date": recent.get("filingDate", []),
                "accession_number": recent.get("accessionNumber", []),
                "primary_document": recent.get("primaryDocument", []),
            }
        )
        df["ticker"] = ticker

        df = df[df["form"].isin(forms)]
        logger.info(
            f"{ticker}: nalezeno {len(df)} 'whale' filings ({', '.join(forms)})."
        )
        return df


def download_sec_data(tickers: list[str]) -> None:
    """Stahne fundamentaly + whale filings pro seznam tickeru."""
    fundamentals_fetcher = SecFundamentalsFetcher()
    filings_fetcher = SecFilingsFetcher()

    for ticker in tickers:
        logger.info(f"--- {ticker} ---")

        fdf = fundamentals_fetcher.fetch(ticker)
        if fdf is not None:
            fundamentals_fetcher.save(fdf, ticker)

        time.sleep(0.15)  # SEC rate limit: max ~10 req/s, davame si rezervu

        filings_df = filings_fetcher.fetch(ticker)
        if filings_df is not None:
            filings_fetcher.save(filings_df, ticker)

        time.sleep(0.15)


if __name__ == "__main__":
    settings = load_settings()
    tickers = settings.get("universe", {}).get("equities", [])
    download_sec_data(tickers)
