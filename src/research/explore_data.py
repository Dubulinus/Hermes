"""
src/research/explore_data.py

Rychly prozkoumavaci skript. Otevri ve VSCode a pouzij "Run Cell"
(nebo Shift+Enter) nad kazdym blokem s "# %%" - spusti se jen ta cast,
ne cely soubor. Bunky spoustej VZDY POPORADE SHORA DOLU (sdili spolecnou
pamet, kazda dalsi casto pracuje s promennou z te predchozi).
"""

# %% Nastaveni cesty k datum (nezavisle na working directory VSCode)
from pathlib import Path
import pandas as pd

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)  # src/research/ -> src/ -> koren projektu
DATA_RAW = PROJECT_ROOT / "data" / "raw"

print(f"Koren projektu: {PROJECT_ROOT}")
print(f"Existuje slozka data/raw? {DATA_RAW.exists()}")

# %% Nacteni OHLCV dat
df_aapl = pd.read_parquet(DATA_RAW / "ohlcv" / "AAPL_1h.parquet")
print(df_aapl.info())
df_aapl.head(10)

# %% Zakladni statistiky (min, max, prumer, atd.)
df_aapl.describe()

# %% Chybejici hodnoty - dulezite zkontrolovat pred jakymkoliv modelovanim
df_aapl.isna().sum()

# %% Fundamentaly - kolik ruznych metrik SEC nabizi
df_fund = pd.read_parquet(DATA_RAW / "sec_fundamentals" / "AAPL.parquet")
print(f"Pocet unikatnich metrik: {df_fund['metric'].nunique()}")
df_fund["metric"].value_counts().head(20)

# %% Konkretni metrika v case (napr. Revenues)
revenues = df_fund[df_fund["metric"] == "Revenues"].sort_values("end")
revenues[["end", "value", "form", "fiscal_period"]]

# %% Whale filings - rozlozeni podle typu formulare
df_filings = pd.read_parquet(DATA_RAW / "sec_filings" / "AAPL.parquet")
df_filings["form"].value_counts()

# %% Form 4 (insider trading) - poslednich 10 filings
df_filings[df_filings["form"] == "4"].sort_values("filing_date", ascending=False).head(
    10
)
