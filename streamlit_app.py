"""Dashboard web do BiFinance — versão de demonstração (Streamlit)."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from bifinance import finance as fin
from bifinance.api_client import fetch_usd_brl
from bifinance.models import DollarEntry, Transaction
from bifinance.storage import Storage

st.set_page_config(page_title="BiFinance", page_icon="💰", layout="wide")
st.title("💰 BiFinance")
st.caption("Gerenciador de finanças pessoais · versão web (demonstração)")

# ── Cotação USD/BRL ao vivo ───────────────────────────────────────────────────
st.subheader("Cotação USD/BRL")
rate = fetch_usd_brl()
if rate is not None:
    st.metric("Taxa atual (bid)", f"R$ {rate:.4f}")
else:
    st.warning("Não foi possível obter a cotação do dólar no momento.")

st.divider()

# ── Dados: reais ou demonstração ─────────────────────────────────────────────
s = Storage()
txs = s.load_transactions()
entries = s.load_dollar_entries()

def _uid() -> str:
    return str(uuid.uuid4())

if not txs:
    st.caption("Exibindo dados de demonstração.")
    raw_txs = [
        {"id": _uid(), "type": "income",          "description": "Salário",           "amount": 8500.00, "date": "2026-04-05", "category": "Salário",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "income",          "description": "Freelance Design",  "amount": 1800.00, "date": "2026-04-12", "category": "Freelance",   "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Supermercado",      "amount":  745.00, "date": "2026-04-07", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Aluguel",           "amount": 1600.00, "date": "2026-04-10", "category": "Moradia",     "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Netflix",           "amount":   39.90, "date": "2026-04-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Spotify",           "amount":   21.90, "date": "2026-04-12", "category": "Assinaturas", "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Academia",          "amount":   89.90, "date": "2026-04-09", "category": "Saúde",       "is_recurring": True,  "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "expense",         "description": "Café",              "amount":   14.50, "date": "2026-04-10", "category": "Alimentação", "is_recurring": False, "ticker": None,     "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "investment_buy",  "description": "Compra KNRI11",     "amount": 2100.00, "date": "2026-04-15", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": "FII",  "quantity": 20.0, "notes": None},
        {"id": _uid(), "type": "dividend",        "description": "Provento KNRI11",   "amount":   84.00, "date": "2026-04-10", "category": None,           "is_recurring": False, "ticker": "KNRI11", "asset_type": None,  "quantity": None, "notes": None},
        {"id": _uid(), "type": "dividend",        "description": "Provento XPML11",   "amount":  103.50, "date": "2026-04-10", "category": None,           "is_recurring": False, "ticker": "XPML11", "asset_type": None,  "quantity": None, "notes": None},
    ]
    txs = [Transaction.from_dict(d) for d in raw_txs]

    raw_entries = [
        {"id": _uid(), "date": "2026-02-18", "amount_usd": 800.0, "exchange_rate": 5.95, "iof_pct": 1.1, "spread_pct": 1.2, "description": "Dólar reserva"},
        {"id": _uid(), "date": "2026-03-25", "amount_usd": 300.0, "exchange_rate": 5.90, "iof_pct": 1.1, "spread_pct": 1.0, "description": "Dólar ETF"},
    ]
    entries = [DollarEntry.from_dict(d) for d in raw_entries]

# ── Resumo Financeiro ─────────────────────────────────────────────────────────
st.subheader("Resumo Financeiro")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Renda Real",        fin.fmt_brl(fin.total_real_income(txs)))
col2.metric("Despesas Reais",    fin.fmt_brl(fin.total_real_expenses(txs)))
col3.metric("Caixa Disponível",  fin.fmt_brl(fin.available_cash(txs)))
col4.metric("Total Proventos",   fin.fmt_brl(fin.total_dividends(txs)))

st.divider()

# ── Posição em Dólar ──────────────────────────────────────────────────────────
if entries:
    st.subheader("Posição em Dólar")
    summary = fin.dollar_summary(entries, rate)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total em USD",      f"USD {summary['total_usd']:,.2f}")
    c2.metric("Custo Total (BRL)", fin.fmt_brl(summary["total_brl"]))
    c3.metric("PM Efetivo",        f"R$ {summary['avg_effective_rate']:.4f}")
    if rate:
        sign = "+" if summary["pnl"] >= 0 else ""
        c1.metric("P&L", f"{sign}{fin.fmt_brl(summary['pnl'])} ({fin.fmt_pct(summary['pnl_pct'])})")
