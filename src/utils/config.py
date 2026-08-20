"""
src/utils/config.py

Centralni nacitani config/settings.yaml a config/secrets.env.
Vsechny ostatni moduly by mely tahat konfiguraci odsud, ne primo ze souboru.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

import yaml
from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"
SECRETS_PATH = PROJECT_ROOT / "config" / "secrets.env"


@lru_cache
def load_settings() -> dict:
    """Nacte config/settings.yaml (necachuje mezi behy procesu, jen v ramci jednoho behu)."""
    with open(SETTINGS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@lru_cache
def load_secrets() -> dict:
    """
    Nacte config/secrets.env (API klice).
    Pokud soubor neexistuje, vrati prazdny dict - at to nespadne pri prvnim spusteni,
    jen jednotlive fetchery pak nahlasi chybejici klic.
    """
    if not SECRETS_PATH.exists():
        return {}
    return dotenv_values(SECRETS_PATH)


def get_secret(key: str) -> str | None:
    val = load_secrets().get(key)
    return val if val else None
