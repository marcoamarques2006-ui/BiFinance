"""Cliente HTTP para cotações externas."""

from __future__ import annotations

import requests

_USD_BRL_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL"


def fetch_usd_brl(timeout: int = 5) -> float | None:
    """Retorna cotação atual USD/BRL (bid) ou None em caso de falha."""
    try:
        resp = requests.get(_USD_BRL_URL, timeout=timeout)
        resp.raise_for_status()
        return float(resp.json()["USDBRL"]["bid"])
    except Exception:
        return None
