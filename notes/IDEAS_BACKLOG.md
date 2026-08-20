# Backlog napadu (parking lot)

Pravidlo: sem zapisujeme kazdy napad na "vysperkovani", ktery nas napadne
BEHEM prace na aktualni fazi. Nic z tohoto seznamu se nezacina resit,
dokud aktualni faze neni hotova a odzkousena.

## Faze 2 (az MVP jede end-to-end)
- [ ] Telegram bot - notifikace o obchodech, denni P&L summary, alerty
- [ ] Structured logging (loguru) + health-check cron na RPi
- [ ] Automaticke zalohovani (rsync/restic) na cloud nebo ThinkPad

## Faze 3 (az je vic nez jedna strategie)
- [ ] Triple-barrier labeling (Lopez de Prado)
- [ ] Purged k-fold cross-validation / walk-forward validace
- [ ] Feature store (centralni misto pro vypocitane featury)
- [ ] Experiment tracking (MLflow nebo aspon SQLite log backtestu)

## Faze 4 (risk management + provoz)
- [ ] Dashboard (Streamlit/Grafana) - equity curve, exposure, drawdown
- [ ] Alerting na anomalie (vypadek dat, burza neodpovida, drawdown limit)
- [ ] Circuit breakers

## Faze 5 (ve hvezdach)
- [ ] Multi-agent system (AI "osobnosti" pro/proti + manazer rozhodovani)
- [ ] Self-adapting/auto-optimalizujici se system
