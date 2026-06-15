"""Dashboard web do BiFinance (Streamlit) — app completo conectado ao Supabase.

Espelha as funcionalidades do app desktop: Dashboard, Transações,
Investimentos, Dólar, Metas, Orçamento e Relatórios — lendo e escrevendo
dados reais no Supabase.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd
import streamlit as st

from bifinance import finance as fin
from bifinance.api_client import fetch_usd_brl
from bifinance.models import (
    ASSET_TYPES,
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    TX_LABELS,
    Budget,
    DollarEntry,
    Goal,
    Transaction,
)
from bifinance.storage import Storage

st.set_page_config(page_title="BiFinance", page_icon="💰", layout="wide")

# ── Credenciais Supabase via st.secrets ────────────────────────────────────────
def _secret(name: str) -> str:
    """Lê o secret do Streamlit; cai para variável de ambiente local (.env)."""
    try:
        val = st.secrets.get(name, "")
    except Exception:
        val = ""
    return val or os.environ.get(name, "")


# Sempre sobrescreve (não usa setdefault) para refletir mudanças de secret sem
# precisar reiniciar manualmente o processo.
os.environ["SUPABASE_URL"] = _secret("SUPABASE_URL")
os.environ["SUPABASE_KEY"] = _secret("SUPABASE_KEY")


@st.cache_resource
def get_storage() -> Storage:
    return Storage()


def _connected() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))


# ── Sidebar / navegação ─────────────────────────────────────────────────────────
st.sidebar.title("💰 BiFinance")
st.sidebar.caption("Gestor Financeiro Pessoal · web")

PAGES = [
    "📊 Dashboard",
    "💸 Transações",
    "📈 Investimentos",
    "💵 Dólar",
    "🎯 Metas",
    "🧮 Orçamento",
    "📋 Relatórios",
]
page = st.sidebar.radio("Navegação", PAGES, label_visibility="collapsed")

if not _connected():
    st.error(
        "⚠️ Banco de dados não configurado. Defina `SUPABASE_URL` e `SUPABASE_KEY` "
        "em **Manage app → Settings → Secrets** no Streamlit Cloud."
    )
    st.stop()

s = get_storage()


@st.cache_data(ttl=30)
def load_all() -> dict:
    return {
        "txs": s.load_transactions(),
        "entries": s.load_dollar_entries(),
        "goals": s.load_goals(),
        "budgets": s.load_budgets(),
        "settings": s.load_settings(),
        "prices": s.load_prices(),
    }


def _refresh() -> None:
    load_all.clear()


try:
    data = load_all()
except Exception as exc:  # conexão/credenciais inválidas
    st.error(f"Erro ao conectar no Supabase: {exc}")
    st.stop()

txs = data["txs"]
entries = data["entries"]
goals = data["goals"]
budgets = data["budgets"]
settings = data["settings"]
prices = data["prices"]

today = date.today()
rate = fetch_usd_brl() or 0.0


# ════════════════════════════════════════════════════════════════════════════════
# Dashboard
# ════════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Renda Real", fin.fmt_brl(fin.total_real_income(txs)))
    c2.metric("Despesas Reais", fin.fmt_brl(fin.total_real_expenses(txs)))
    c3.metric("Caixa Disponível", fin.fmt_brl(fin.available_cash(txs)))
    c4.metric("Total Proventos", fin.fmt_brl(fin.total_dividends(txs)))

    if rate:
        st.metric("Cotação USD/BRL (bid)", f"R$ {rate:.4f}")

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Receita vs Despesa (6 meses)")
        hist = fin.monthly_history(txs, 6)
        if hist:
            df = pd.DataFrame(hist).set_index("month")[["income", "expenses"]]
            df.columns = ["Receita", "Despesa"]
            st.bar_chart(df)

    with col_b:
        st.subheader(f"Gastos por categoria · {today.month:02d}/{today.year}")
        cats = fin.expenses_by_category(txs, today.year, today.month)
        if cats:
            df = pd.DataFrame(
                {"Categoria": list(cats.keys()), "Valor": list(cats.values())}
            ).set_index("Categoria")
            st.bar_chart(df)
        else:
            st.caption("Sem despesas no mês atual.")


# ════════════════════════════════════════════════════════════════════════════════
# Transações
# ════════════════════════════════════════════════════════════════════════════════
elif page == "💸 Transações":
    st.title("💸 Transações")

    with st.expander("➕ Nova transação", expanded=not txs):
        with st.form("nova_tx", clear_on_submit=True):
            colf = st.columns(3)
            tipo = colf[0].selectbox("Tipo", list(TX_LABELS.keys()),
                                     format_func=lambda t: TX_LABELS[t])
            desc = colf[1].text_input("Descrição")
            valor = colf[2].number_input("Valor (R$)", min_value=0.0, step=10.0)
            colg = st.columns(3)
            dt = colg[0].date_input("Data", value=today)
            cat = colg[1].selectbox("Categoria", ["—"] + EXPENSE_CATEGORIES + INCOME_CATEGORIES)
            ticker = colg[2].text_input("Ticker (investimentos)")
            colh = st.columns(2)
            qtd = colh[0].number_input("Quantidade", min_value=0.0, step=1.0)
            asset = colh[1].selectbox("Tipo de ativo", ["—"] + ASSET_TYPES)

            if st.form_submit_button("Adicionar", type="primary"):
                try:
                    t = Transaction(
                        type=tipo, description=desc, amount=float(valor),
                        date=dt.isoformat(),
                        category=None if cat == "—" else cat,
                        ticker=ticker.strip().upper() or None,
                        asset_type=None if asset == "—" else asset,
                        quantity=float(qtd) if qtd > 0 else None,
                    )
                    t.validate()
                    s.add_transaction(t)
                    _refresh()
                    st.success("Transação adicionada!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    st.subheader(f"{len(txs)} transações")
    for t in sorted(txs, key=lambda x: x.date, reverse=True):
        cols = st.columns([2, 3, 2, 2, 1])
        sign = "+" if t.type in ("income", "dividend", "investment_sell") else "−"
        cols[0].write(t.date)
        cols[1].write(f"**{t.description}**")
        cols[2].write(TX_LABELS.get(t.type, t.type))
        cols[3].write(f"{sign} {fin.fmt_brl(t.amount)}")
        if cols[4].button("🗑", key=f"del_tx_{t.id}"):
            s.remove_transaction(t.id)
            _refresh()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Investimentos
# ════════════════════════════════════════════════════════════════════════════════
elif page == "📈 Investimentos":
    st.title("📈 Investimentos")
    positions = fin.with_pnl(fin.portfolio_positions(txs), prices)

    if not positions:
        st.info("Nenhuma posição em carteira. Registre compras de ativos em Transações.")
    else:
        st.metric("Custo total investido", fin.fmt_brl(fin.total_invested_cost(txs)))
        rows = []
        for ticker, p in positions.items():
            rows.append({
                "Ticker": ticker,
                "Tipo": p["asset_type"],
                "Qtd": round(p["quantity"], 2),
                "Custo médio": fin.fmt_brl(p["avg_cost"]),
                "Preço atual": fin.fmt_brl(p["current_price"]),
                "Valor mercado": fin.fmt_brl(p["market_value"]),
                "P&L": f"{fin.fmt_brl(p['pnl'])} ({fin.fmt_pct(p['pnl_pct'])})",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("Atualizar preços")
        with st.form("precos"):
            new_prices = dict(prices)
            for ticker in positions:
                new_prices[ticker] = st.number_input(
                    ticker, value=float(prices.get(ticker, 0.0)), step=0.5, key=f"px_{ticker}"
                )
            if st.form_submit_button("Salvar preços", type="primary"):
                s.save_prices(new_prices)
                _refresh()
                st.success("Preços atualizados!")
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Dólar
# ════════════════════════════════════════════════════════════════════════════════
elif page == "💵 Dólar":
    st.title("💵 Posição em Dólar")
    if rate:
        st.metric("Cotação atual (bid)", f"R$ {rate:.4f}")

    with st.expander("➕ Nova compra de dólar"):
        with st.form("novo_dolar", clear_on_submit=True):
            c = st.columns(3)
            usd = c[0].number_input("Valor (USD)", min_value=0.0, step=100.0)
            tx_rate = c[1].number_input("Taxa (BRL/USD)", min_value=0.0, step=0.01, value=rate)
            dt = c[2].date_input("Data", value=today)
            c2 = st.columns(2)
            iof = c2[0].number_input("IOF (%)", min_value=0.0, value=1.1, step=0.1)
            spread = c2[1].number_input("Spread (%)", min_value=0.0, value=0.0, step=0.1)
            if st.form_submit_button("Adicionar", type="primary"):
                try:
                    e = DollarEntry(date=dt.isoformat(), amount_usd=float(usd),
                                    exchange_rate=float(tx_rate), iof_pct=float(iof),
                                    spread_pct=float(spread))
                    e.validate()
                    s.add_dollar_entry(e)
                    _refresh()
                    st.success("Compra registrada!")
                    st.rerun()
                except ValueError as ex:
                    st.error(str(ex))

    if entries:
        summary = fin.dollar_summary(entries, rate)
        c = st.columns(3)
        c[0].metric("Total em USD", f"USD {summary['total_usd']:,.2f}")
        c[1].metric("Custo Total (BRL)", fin.fmt_brl(summary["total_brl"]))
        c[2].metric("PM Efetivo", f"R$ {summary['avg_effective_rate']:.4f}")
        if rate:
            sign = "+" if summary["pnl"] >= 0 else ""
            st.metric("P&L", f"{sign}{fin.fmt_brl(summary['pnl'])} ({fin.fmt_pct(summary['pnl_pct'])})")

        for e in sorted(entries, key=lambda x: x.date, reverse=True):
            cols = st.columns([2, 2, 2, 1])
            cols[0].write(e.date)
            cols[1].write(f"USD {e.amount_usd:,.2f}")
            cols[2].write(f"@ R$ {e.exchange_rate:.4f}")
            if cols[3].button("🗑", key=f"del_usd_{e.id}"):
                s.remove_dollar_entry(e.id)
                _refresh()
                st.rerun()
    else:
        st.info("Nenhuma compra de dólar registrada.")


# ════════════════════════════════════════════════════════════════════════════════
# Metas
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Metas":
    st.title("🎯 Metas")

    with st.expander("➕ Nova meta"):
        with st.form("nova_meta", clear_on_submit=True):
            c = st.columns(3)
            nome = c[0].text_input("Nome")
            alvo = c[1].number_input("Valor alvo (R$)", min_value=0.0, step=100.0)
            atual = c[2].number_input("Valor atual (R$)", min_value=0.0, step=100.0)
            if st.form_submit_button("Criar meta", type="primary"):
                try:
                    g = Goal(name=nome, target=float(alvo), current=float(atual))
                    g.validate()
                    s.add_goal(g)
                    _refresh()
                    st.success("Meta criada!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    if not goals:
        st.info("Nenhuma meta cadastrada.")
    for g in goals:
        st.subheader(g.name)
        st.progress(g.progress, text=f"{g.progress * 100:.0f}% · "
                    f"{fin.fmt_brl(g.current)} de {fin.fmt_brl(g.target)}")
        cols = st.columns([3, 1])
        novo = cols[0].number_input(f"Atualizar valor — {g.name}", min_value=0.0,
                                    value=float(g.current), step=100.0, key=f"upd_{g.id}")
        if cols[1].button("Salvar", key=f"save_goal_{g.id}"):
            g.current = float(novo)
            s.update_goal(g)
            _refresh()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Orçamento
# ════════════════════════════════════════════════════════════════════════════════
elif page == "🧮 Orçamento":
    st.title(f"🧮 Orçamento Mensal · {today.month:02d}/{today.year}")

    with st.expander("➕ Definir orçamento"):
        with st.form("novo_orcamento", clear_on_submit=True):
            c = st.columns(2)
            cat = c[0].selectbox("Categoria", EXPENSE_CATEGORIES)
            limite = c[1].number_input("Limite mensal (R$)", min_value=0.0, step=50.0)
            if st.form_submit_button("Definir", type="primary"):
                try:
                    b = Budget(category=cat, limit=float(limite))
                    b.validate()
                    s.add_budget(b)
                    _refresh()
                    st.success("Orçamento definido!")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    status = fin.budget_status(txs, budgets, today.year, today.month)
    if not status:
        st.info("Nenhum orçamento definido.")
    else:
        total_l = fin.total_budgeted(budgets)
        total_s = sum(x["spent"] for x in status)
        st.caption(f"Gasto {fin.fmt_brl(total_s)} de {fin.fmt_brl(total_l)} orçados")
        id_by_cat = {b.category: b.id for b in budgets}
        emoji = {"ok": "🟢", "alerta": "🟡", "estourado": "🔴"}
        for x in status:
            st.write(f"{emoji[x['status']]} **{x['category']}** — "
                     f"{fin.fmt_brl(x['spent'])} de {fin.fmt_brl(x['limit'])} ({x['pct']:.0f}%)")
            st.progress(min(1.0, x["pct"] / 100))
            if st.button(f"Remover {x['category']}", key=f"del_b_{x['category']}"):
                s.remove_budget(id_by_cat[x["category"]])
                _refresh()
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# Relatórios
# ════════════════════════════════════════════════════════════════════════════════
elif page == "📋 Relatórios":
    st.title("📋 Relatórios")

    st.subheader("Histórico mensal")
    hist = fin.monthly_history(txs, 6)
    if hist:
        df = pd.DataFrame(hist)
        df.columns = ["Mês", "Receita", "Despesa"]
        df["Saldo"] = df["Receita"] - df["Despesa"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Patrimônio investido vs CDI")
    cdi = fin.patrimony_vs_cdi(txs, 6, settings.cdi_rate)
    if cdi:
        df = pd.DataFrame(cdi).set_index("month")
        df.columns = ["Investido", "CDI"]
        st.line_chart(df)

    st.divider()
    st.subheader("Pequenos vícios (gastos recorrentes)")
    vices = fin.small_vices(txs)
    if vices:
        rows = [{
            "Descrição": v["description"],
            "Ocorrências": v["count"],
            "Média": fin.fmt_brl(v["avg"]),
            "Projeção anual": fin.fmt_brl(v["annual_est"]),
        } for v in vices]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.caption("Sem gastos recorrentes identificados.")
