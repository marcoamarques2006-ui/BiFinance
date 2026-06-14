"""Cliente HTTP para cotações externas."""

from __future__ import annotations

import requests

_HEADERS = {"User-Agent": "BiFinance/1.0"}

_SOURCES = [
    ("https://economia.awesomeapi.com.br/json/last/USD-BRL",
     lambda d: float(d["USDBRL"]["bid"])),
    ("https://open.er-api.com/v6/latest/USD",
     lambda d: float(d["rates"]["BRL"])),
]


def fetch_usd_brl(timeout: int = 10) -> float | None:
    """Retorna cotação atual USD/BRL ou None se todas as fontes falharem."""
    for url, extract in _SOURCES:
        try:
            resp = requests.get(url, timeout=timeout, headers=_HEADERS)
            resp.raise_for_status()
            return extract(resp.json())
        except Exception:
            continue
    return None
