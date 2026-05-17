"""Dashboard web do BiFinance — versão de demonstração (Streamlit)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from bifinance import finance as fin
from bifinance.api_client import fetch_usd_brl
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

# ── Dados financeiros ─────────────────────────────────────────────────────────
s = Storage()
txs = s.load_transactions()

if not txs:
    st.info(
        "Nenhum dado encontrado. Execute o aplicativo desktop localmente, "
        "registre suas transações e os indicadores aparecerão aqui."
    )
else:
    st.subheader("Resumo Financeiro")
    col1, col2, col3 = st.columns(3)
    col1.metric("Renda Real", fin.fmt_brl(fin.total_real_income(txs)))
    col2.metric("Despesas Reais", fin.fmt_brl(fin.total_real_expenses(txs)))
    col3.metric("Caixa Disponível", fin.fmt_brl(fin.available_cash(txs)))
