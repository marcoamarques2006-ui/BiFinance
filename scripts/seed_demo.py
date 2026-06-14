"""Insere dados de demonstração no BiFinance."""

import json
import uuid
from pathlib import Path


def uid():
    return str(uuid.uuid4())


transactions = [
    # ── Novembro 2025 ─────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2025-11-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  820.00, "date": "2025-11-08", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2025-11-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2025-11-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2025-11-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Farmácia",          "amount":   95.00, "date": "2025-11-14", "category": "Saúde",       "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Uber",              "amount":   88.40, "date": "2025-11-18", "category": "Transporte",  "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2025-11-20", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2025-11-22", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra KNRI11",     "amount": 2100.00, "date": "2025-11-25", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": "FII",  "quantity": 20.0,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra ITUB4",      "amount": 2880.00, "date": "2025-11-26", "category": None,           "is_recurring": False, "ticker": "ITUB4",  "asset_type": "Ação", "quantity": 120.0, "notes": None},
    # ── Dezembro 2025 ─────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2025-12-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "income",          "description": "Bônus anual",       "amount": 5000.00, "date": "2025-12-15", "category": "Bônus",       "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  760.00, "date": "2025-12-07", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2025-12-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2025-12-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2025-12-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Presente de Natal", "amount":  420.00, "date": "2025-12-20", "category": "Lazer",       "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2025-12-22", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2025-12-22", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Uber",              "amount":  112.00, "date": "2025-12-28", "category": "Transporte",  "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2025-12-12", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra XPML11",     "amount": 3120.00, "date": "2025-12-18", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": "FII",  "quantity": 30.0,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra VALE3",      "amount": 4500.00, "date": "2025-12-20", "category": None,           "is_recurring": False, "ticker": "VALE3",  "asset_type": "Ação", "quantity": 75.0,  "notes": None},
    # ── Janeiro 2026 ──────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2026-01-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  890.00, "date": "2026-01-08", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2026-01-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2026-01-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2026-01-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Farmácia",          "amount":  110.00, "date": "2026-01-15", "category": "Saúde",       "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Uber",              "amount":   95.20, "date": "2026-01-18", "category": "Transporte",  "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2026-01-20", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2026-01-22", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2026-01-14", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento XPML11",   "amount":  103.50, "date": "2026-01-14", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra ITUB4",      "amount": 2640.00, "date": "2026-01-28", "category": None,           "is_recurring": False, "ticker": "ITUB4",  "asset_type": "Ação", "quantity": 100.0, "notes": None},
    # ── Fevereiro 2026 ────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2026-02-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "income",          "description": "Freelance Design",  "amount": 1800.00, "date": "2026-02-12", "category": "Freelance",   "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  840.00, "date": "2026-02-07", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2026-02-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2026-02-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2026-02-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2026-02-22", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2026-02-24", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Roupas",            "amount":  320.00, "date": "2026-02-15", "category": "Vestuário",   "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Uber",              "amount":   78.60, "date": "2026-02-20", "category": "Transporte",  "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2026-02-13", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento XPML11",   "amount":  103.50, "date": "2026-02-13", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "investment_sell", "description": "Venda ITUB4",       "amount": 3250.00, "date": "2026-02-25", "category": None,           "is_recurring": False, "ticker": "ITUB4",  "asset_type": "Ação", "quantity": 120.0, "notes": "Lucro realizado"},
    # ── Março 2026 ────────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2026-03-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  910.00, "date": "2026-03-07", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2026-03-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2026-03-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2026-03-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2026-03-22", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2026-03-24", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Uber",              "amount":   91.80, "date": "2026-03-19", "category": "Transporte",  "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Curso Online",      "amount":  299.00, "date": "2026-03-05", "category": "Educação",    "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2026-03-13", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento XPML11",   "amount":  103.50, "date": "2026-03-13", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra KNRI11",     "amount": 2100.00, "date": "2026-03-20", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": "FII",  "quantity": 20.0,  "notes": None},
    {"id": uid(), "type": "investment_buy",  "description": "Compra MXRF11",     "amount": 1560.00, "date": "2026-03-22", "category": None,           "is_recurring": False, "ticker": "MXRF11", "asset_type": "FII",  "quantity": 150.0, "notes": None},
    # ── Abril 2026 ────────────────────────────────────────────────────────
    {"id": uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2026-04-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Supermercado",      "amount":  745.00, "date": "2026-04-07", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2026-04-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2026-04-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2026-04-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2026-04-09", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2026-04-10", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2026-04-10", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento XPML11",   "amount":  103.50, "date": "2026-04-10", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": None,  "quantity": None,  "notes": None},
    {"id": uid(), "type": "dividend",        "description": "Provento MXRF11",   "amount":   15.00, "date": "2026-04-10", "category": None,           "is_recurring": False, "ticker": "MXRF11", "asset_type": None,  "quantity": None,  "notes": None},
]

dollar_entries = [
    {"id": uid(), "date": "2025-12-10", "amount_usd": 500.0, "exchange_rate": 5.85, "iof_pct": 1.1, "spread_pct": 1.5, "description": "Dólar viagem"},
    {"id": uid(), "date": "2026-02-18", "amount_usd": 800.0, "exchange_rate": 5.95, "iof_pct": 1.1, "spread_pct": 1.2, "description": "Dólar reserva"},
    {"id": uid(), "date": "2026-03-25", "amount_usd": 300.0, "exchange_rate": 5.90, "iof_pct": 1.1, "spread_pct": 1.0, "description": "Dólar ETF"},
]

goals = [
    {"id": uid(), "name": "Viagem Europa",       "target": 18000.0, "current": 7200.0,  "deadline": "2026-12-31", "color": "#3b82f6"},
    {"id": uid(), "name": "Fundo de Emergência", "target": 25000.0, "current": 14500.0, "deadline": None,         "color": "#22c55e"},
    {"id": uid(), "name": "MacBook Pro",          "target":  9000.0, "current": 3800.0,  "deadline": "2026-08-01", "color": "#8b5cf6"},
    {"id": uid(), "name": "Moto",                 "target": 35000.0, "current": 5000.0,  "deadline": "2027-06-01", "color": "#f59e0b"},
]

settings = {"cdi_rate": 10.75, "default_iof_pct": 1.1}

current_prices = {
    "ITUB4":  28.40,
    "VALE3":  58.70,
    "KNRI11": 108.50,
    "XPML11": 107.20,
    "MXRF11":  10.52,
}

data = {
    "transactions":   transactions,
    "dollar_entries": dollar_entries,
    "goals":          goals,
    "settings":       settings,
    "current_prices": current_prices,
}

path = Path.home() / ".bifinance" / "data.json"
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK — {len(transactions)} transacoes, {len(dollar_entries)} entradas de dolar, {len(goals)} metas.")
