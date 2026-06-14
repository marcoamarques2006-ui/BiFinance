"""View: Dashboard."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from bifinance import charts as ch
from bifinance import finance as fin
from bifinance.theme import C


def render(app) -> None:
    scroll = app._scroll(app._content)
    scroll.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

    txs      = app._s.load_transactions()
    settings = app._s.load_settings()
    today    = date.today()
    y, m     = today.year, today.month

    cash     = fin.available_cash(txs)
    invested = fin.total_invested_cost(txs)
    income_m = fin.monthly_income(txs, y, m)
    exp_m    = fin.monthly_expenses(txs, y, m)
    divs     = fin.total_dividends(txs)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpis = [
        ("PATRIMÔNIO TOTAL",    fin.fmt_brl(cash + invested),
         f"Caixa {fin.fmt_brl(cash)} + Invest. {fin.fmt_brl(invested)}", C["muted"]),
        ("RECEITA DO MÊS",      fin.fmt_brl(income_m),
         fin.fmt_pct((income_m - exp_m) / income_m * 100) + " saldo"
         if income_m > 0 else "— sem receitas",
         C["green"] if income_m >= exp_m else C["red"]),
        ("GASTOS DO MÊS",       fin.fmt_brl(exp_m),
         "Apenas despesas reais — invest. excluídos",
         C["red"] if exp_m > 0 else C["muted"]),
        ("PROVENTOS RECEBIDOS", fin.fmt_brl(divs),
         f"Investido: {fin.fmt_brl(invested)}", C["blue"]),
    ]
    for col, (title, value, sub, sc) in enumerate(kpis):
        app._kpi(scroll, col, title, value, sub, sc, padx=(0, 10) if col < 3 else 0)

    # ── Gráficos ──────────────────────────────────────────────────────────────
    charts_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    charts_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 16))
    charts_frame.grid_columnconfigure(0, weight=2)
    charts_frame.grid_columnconfigure(1, weight=1)

    hist   = fin.monthly_history(txs, 6)
    by_cat = fin.expenses_by_category(txs, y, m)

    bar_card = app._card(charts_frame, row=0, column=0, sticky="nsew", padx=(0, 8))
    bar_card.grid_columnconfigure(0, weight=1)
    app._lbl(bar_card, "Receitas vs Despesas Reais — Últimos 6 meses",
              size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
    ch.embed(ch.bar_income_expenses(hist), bar_card).get_tk_widget().grid(
        row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    donut_card = app._card(charts_frame, row=0, column=1, sticky="nsew", padx=(8, 0))
    donut_card.grid_columnconfigure(0, weight=1)
    app._lbl(donut_card, "Gastos por Categoria — Este mês",
              size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
    ch.embed(ch.donut_categories(by_cat), donut_card).get_tk_widget().grid(
        row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ── CDI ───────────────────────────────────────────────────────────────────
    cdi_card = app._card(scroll, row=2, column=0, columnspan=4, sticky="ew", pady=(0, 16))
    cdi_card.grid_columnconfigure(0, weight=1)
    app._lbl(cdi_card, f"Portfólio vs CDI ({settings.cdi_rate:.1f}% a.a.) — Últimos 6 meses",
              size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
    cdi_data = fin.patrimony_vs_cdi(txs, 6, settings.cdi_rate)
    ch.embed(ch.area_portfolio_cdi(cdi_data, settings.cdi_rate), cdi_card).get_tk_widget().grid(
        row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ── Transações recentes ───────────────────────────────────────────────────
    rec_card = app._card(scroll, row=3, column=0, columnspan=4, sticky="ew")
    rec_card.grid_columnconfigure(0, weight=1)
    recent = sorted(txs, key=lambda t: t.date, reverse=True)[:8]
    hdr = ctk.CTkFrame(rec_card, fg_color="transparent")
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_columnconfigure(0, weight=1)
    app._lbl(hdr, "Transações Recentes", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(16, 14))
    app._lbl(hdr, f"Últimas {len(recent)}", size=11, color=C["muted"]).grid(
        row=0, column=1, sticky="e", padx=16)
    app._sep(rec_card, 1)
    if not recent:
        app._lbl(rec_card, "Nenhuma transação registrada.", color=C["muted"]).grid(
            row=2, column=0, pady=24)
    else:
        for i, t in enumerate(recent):
            app._tx_row(rec_card, t, row=2 + i * 2, show_delete=False)
            if i < len(recent) - 1:
                app._sep(rec_card, 2 + i * 2 + 1, padx=16)
