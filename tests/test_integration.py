"""Testes de integração: comunicação com a API de cotações."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

from bifinance.api_client import fetch_usd_brl


def test_fetch_usd_brl_success():
    """Resposta válida da API retorna float com o valor correto."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"USDBRL": {"bid": "5.8750"}}
    mock_resp.raise_for_status.return_value = None

    with patch("bifinance.api_client.requests.get", return_value=mock_resp):
        result = fetch_usd_brl()

    assert isinstance(result, float)
    assert result == 5.875


def test_fetch_usd_brl_connection_error():
    """Falha de rede retorna None sem lançar exceção."""
    with patch("bifinance.api_client.requests.get", side_effect=requests.ConnectionError):
        result = fetch_usd_brl()

    assert result is None


def test_fetch_usd_brl_http_error():
    """Resposta HTTP de erro retorna None sem lançar exceção."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError

    with patch("bifinance.api_client.requests.get", return_value=mock_resp):
        result = fetch_usd_brl()

    assert result is None
