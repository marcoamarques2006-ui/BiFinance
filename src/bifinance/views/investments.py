"""View: Investimentos."""

from __future__ import annotations

import customtkinter as ctk

from bifinance import finance as fin
from bifinance.theme import C


def render(app) -> None:
    scroll = app._scroll(app._content)
    scroll.grid_columnconfigure(0, weight=1)

    txs       = app._s.load_transactions()
    prices    = app._s.load_prices()
    positions = fin.portfolio_positions(txs)
    with_pl   = fin.with_pnl(positions, prices)

    total_cost = fin.total_invested_cost(txs)
    total_mkt  = sum(p["market_value"] for p in with_pl.values() if p["current_price"] > 0)
    total_pnl  = total_mkt - total_cost if total_mkt > 0 else 0.0
    divs       = fin.total_dividends(txs)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
    kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="ikpi")
    kpi_data = [
        ("CUSTO TOTAL",       fin.fmt_brl(total_cost), "Valor aportado (PM × Qtd)",  C["muted"]),
        ("VALOR DE MERCADO",  fin.fmt_brl(total_mkt),  "Preços atuais inseridos",     C["blue"]),
        ("P&L NÃO REALIZADO", fin.fmt_brl(total_pnl),
         fin.fmt_pct(total_pnl / total_cost * 100) if total_cost > 0 else "—",
         C["green"] if total_pnl >= 0 else C["red"]),
        ("PROVENTOS",         fin.fmt_brl(divs),       "Dividendos e JCP recebidos",  C["blue"]),
    ]
    for col, (title, val, sub, sc) in enumerate(kpi_data):
        app._kpi(kpi_frame, col, title, val, sub, sc, padx=(0, 10) if col < 3 else 0)

    # ── Tabela de posições ─────────────────────────────────────────────────────
    table_card = app._card(scroll, row=1, column=0, sticky="ew", pady=(0, 16))
    table_card.grid_columnconfigure(0, weight=1)

    app._lbl(table_card, "Posições em Carteira", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 4))
    app._lbl(table_card, "Insira o preço atual para calcular P&L não realizado.",
              size=11, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
    app._sep(table_card, 2)

    th = ctk.CTkFrame(table_card, fg_color=C["muted_bg"], height=36, corner_radius=0)
    th.grid(row=3, column=0, sticky="ew")
    th.grid_propagate(False)
    th.grid_columnconfigure(1, weight=1)
    for col, (label, w) in enumerate([
        ("TICKER", 80), ("TIPO", 0), ("QTD", 70), ("PM (R$)", 90),
        ("PREÇO ATUAL", 100), ("VLR MERCADO", 110), ("P&L (R$)", 100), ("P&L (%)", 80),
    ]):
        kw: dict = {"anchor": "w" if col == 1 else "center"}
        if w:
            kw["width"] = w
        app._lbl(th, label, size=10, weight="bold", color=C["muted"], **kw).grid(
            row=0, column=col, padx=(16, 4) if col == 0 else 4, pady=8,
            sticky="ew" if col == 1 else "")

    if not with_pl:
        app._lbl(table_card, "Nenhuma posição em carteira.", color=C["muted"]).grid(
            row=4, column=0, pady=24)
        return

    for i, (ticker, pos) in enumerate(sorted(with_pl.items())):
        rf = ctk.CTkFrame(table_card, fg_color="transparent")
        rf.grid(row=4 + i * 2, column=0, sticky="ew")
        rf.grid_columnconfigure(1, weight=1)

        pnl_clr  = C["green"] if pos["pnl"] >= 0 else C["red"]
        pnl_sign = "+" if pos["pnl"] >= 0 else ""

        app._lbl(rf, ticker, size=13, weight="bold", mono=True, width=80, anchor="center").grid(
            row=0, column=0, padx=(16, 4), pady=10)
        app._lbl(rf, pos["asset_type"], size=11, color=C["muted"], anchor="w").grid(
            row=0, column=1, sticky="ew", padx=4)
        app._lbl(rf, f"{pos['quantity']:.2f}", size=12, mono=True, width=70, anchor="center").grid(
            row=0, column=2, padx=4)
        app._lbl(rf, fin.fmt_brl(pos["avg_cost"]), size=12, mono=True, width=90, anchor="center").grid(
            row=0, column=3, padx=4)

        price_e = ctk.CTkEntry(rf, width=95, height=30, corner_radius=5,
                                border_color=C["border"], fg_color=C["muted_bg"],
                                text_color=C["text"])
        if pos["current_price"] > 0:
            price_e.insert(0, f"{pos['current_price']:.2f}")
        price_e.grid(row=0, column=4, padx=4)

        mkt_lbl = app._lbl(rf, fin.fmt_brl(pos["market_value"]) if pos["current_price"] > 0 else "—",
                             size=12, mono=True, width=110, anchor="center")
        mkt_lbl.grid(row=0, column=5, padx=4)
        pnl_lbl = app._lbl(
            rf, f"{pnl_sign}{fin.fmt_brl(pos['pnl'])}" if pos["current_price"] > 0 else "—",
            size=12, mono=True, color=pnl_clr if pos["current_price"] > 0 else C["muted"],
            width=100, anchor="center")
        pnl_lbl.grid(row=0, column=6, padx=4)
        pnl_pct_lbl = app._lbl(
            rf, fin.fmt_pct(pos["pnl_pct"]) if pos["current_price"] > 0 else "—",
            size=12, mono=True, color=pnl_clr if pos["current_price"] > 0 else C["muted"],
            width=80, anchor="center")
        pnl_pct_lbl.grid(row=0, column=7, padx=(4, 16))

        def _save_price(e, t=ticker, ml=mkt_lbl, pl=pnl_lbl, pp=pnl_pct_lbl,
                         qty=pos["quantity"], cost=pos["total_cost"]) -> None:
            try:
                p   = float(e.widget.get().replace(",", "."))
                prices[t] = p
                app._s.save_prices(prices)
                mkt     = p * qty
                pnl     = mkt - cost
                pnl_pct = pnl / cost * 100 if cost > 0 else 0.0
                clr     = C["green"] if pnl >= 0 else C["red"]
                sign    = "+" if pnl >= 0 else ""
                ml.configure(text=fin.fmt_brl(mkt))
                pl.configure(text=f"{sign}{fin.fmt_brl(pnl)}", text_color=clr)
                pp.configure(text=fin.fmt_pct(pnl_pct), text_color=clr)
            except ValueError:
                pass

        price_e.bind("<FocusOut>", _save_price)
        price_e.bind("<Return>",   _save_price)

        if i < len(with_pl) - 1:
            app._sep(table_card, 4 + i * 2 + 1, padx=16)
