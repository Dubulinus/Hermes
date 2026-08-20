"""
src/research/test_momentum_hypothesis.py

PRVNI test hypotezy: predikuje minuly hodinovy vynos ten pristi?

Pokud korelace vychazi vyrazne KLADNA -> momentum (co rostlo, roste dal)
Pokud korelace vychazi vyrazne ZAPORNA -> mean-reversion (co rostlo, se vraci zpet)
Pokud korelace je blizko 0 -> zadny jasny vzorec (nejcastejsi vysledek, a je to OK)

Pouzij # %% bunky ve VSCode (Shift+Enter), spoustet poporade shora dolu.
"""

# %% Setup
from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = PROJECT_ROOT / "data" / "raw"

TICKER = "AAPL"

# %% Nacteni dat a vypocet vynosu
df = pd.read_parquet(DATA_RAW / "ohlcv" / f"{TICKER}_1h.parquet")
df = df.sort_values("timestamp").reset_index(drop=True)

# Hodinovy vynos = procentualni zmena Close ceny oproti predchozi hodine
df["return"] = df["Close"].pct_change()

df[["timestamp", "Close", "return"]].head(10)

# %% FEATURE: minuly vynos (co uz znas v case t)
df["feature_lagged_return"] = df["return"]

# %% TARGET: pristi vynos (co se snazis predikovat)
df["target_next_return"] = df["return"].shift(-1)

# Zahodime radky, kde chybi feature nebo target (zacatek/konec serie)
clean = df.dropna(subset=["feature_lagged_return", "target_next_return"])

print(f"Pocet pouzitelnych pozorovani: {len(clean)}")
clean[["timestamp", "feature_lagged_return", "target_next_return"]].head(10)

# %% Statisticky test - Pearson korelace (klasicka) a Spearman (odolnejsi vuci outlierum)
from scipy import stats

pearson_corr, pearson_p = stats.pearsonr(
    clean["feature_lagged_return"], clean["target_next_return"]
)
spearman_corr, spearman_p = stats.spearmanr(
    clean["feature_lagged_return"], clean["target_next_return"]
)

print(f"--- {TICKER}: minuly vynos -> pristi vynos ---")
print(f"Pearson korelace:  {pearson_corr:.4f}  (p-hodnota: {pearson_p:.4f})")
print(f"Spearman korelace: {spearman_corr:.4f}  (p-hodnota: {spearman_p:.4f})")
print()
if pearson_p < 0.05:
    smer = (
        "MOMENTUM (kladna korelace)"
        if pearson_corr > 0
        else "MEAN-REVERSION (zaporna korelace)"
    )
    print(f"Statisticky vyznamne (p<0.05): {smer}")
else:
    print("Neni statisticky vyznamne - zadny jasny vzorec pri tomto lagu.")

# %% Quantile test - rozdel pozorovani do 5 skupin podle feature, over prumerny target v kazde
clean["quantile"] = pd.qcut(
    clean["feature_lagged_return"],
    q=5,
    labels=["Q1 (nejnizsi)", "Q2", "Q3", "Q4", "Q5 (nejvyssi)"],
)

quantile_summary = clean.groupby("quantile", observed=True)["target_next_return"].agg(
    ["mean", "std", "count"]
)
quantile_summary["mean"] = quantile_summary["mean"] * 100  # v procentech pro citelnost

print(f"--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu ({TICKER}) ---")
quantile_summary

print(f"--- Prumerny pristi vynos (%) podle kvintilu minuleho vynosu ({TICKER}) ---")
print(quantile_summary)
