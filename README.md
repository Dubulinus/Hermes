# Hermes (faze Fenix)

Osobni quant trading system. Filozofie: hledani alfy pres velke mnozstvi
ruznorodych dat (OHLCV, SEC fundamentals/insider trading, makro, alt data),
statisticke overeni vzorcu, a az pak stavba obchodnich strategii s risk
managementem.

## Stroje
- **ThinkPad** - vyvoj, VSCode, git
- **Ghettoserver** - dlouhe vypocty, stahovani/zpracovani velkych dat
- **Raspberry Pi 4B** - execution (posilani prikazu brokerovi)

## Setup
```bash
uv sync   # nebo: pip install -e .
cp config/secrets.env.example config/secrets.env
# doplnit API klice do secrets.env
```

## Struktura
- `src/ingestion/` - stahovaci moduly pro jednotlive datove zdroje
- `src/research/` - hledani vzorcu, feature engineering
- `src/backtest/` - backtest engine, validace strategii
- `src/strategy/` - jednotlive obchodni strategie
- `src/risk/` - position sizing, stop-loss, circuit breakers
- `src/execution/` - broker API, order management (bezi na RPi)

## Data zdroje (vse zdarma)
| Kategorie | Zdroj | Klic potreba |
|---|---|---|
| OHLCV | yfinance | ne |
| Fundamentals | SEC EDGAR | ne (jen User-Agent) |
| Insider trading | SEC EDGAR Form 4 | ne (jen User-Agent) |
| Makro | FRED | ano (zdarma) |
| Pocasi | Open-Meteo | ne |
| Pozary | NASA FIRMS | ano (zdarma) |
| News/sentiment | GDELT, RSS, Reddit | castecne |

Viz `IDEAS_BACKLOG.md` pro napady do budoucna (nerozptylovat se jimi ted).
