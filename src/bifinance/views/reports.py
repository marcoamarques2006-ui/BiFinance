"""View: Relatórios."""

from __future__ import annotations

import customtkinter as ctk

from bifinance import charts as ch
from bifinance import finance as fin
from bifinance.theme import C


def render(app) -> None:
    scroll = app._scroll(app._content)
    scroll.grid_columnconfigure(0, weight=1)

    txs  = app._s.load_transactions()
    hist = fin.monthly_history(txs, 6)

    # ── Gráfico de saldo acumulado ─────────────────────────────────────────────
    bal_card = app._card(scroll, row=0, column=0, sticky="ew", pady=(0, 16))
    bal_card.grid_columnconfigure(0, weight=1)
    app._lbl(bal_card, "Saldo Acumulado (Receitas − Despesas Reais) — 6 meses",
              size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
    ch.embed(ch.line_balance(hist), bal_card).get_tk_widget().grid(
        row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

    # ── Pequenos vícios ────────────────────────────────────────────────────────
    vices = fin.small_vices(txs, min_count=2)
    vices_card = app._card(scroll, row=1, column=0, sticky="ew", pady=(0, 16))
    vices_card.grid_columnconfigure(0, weight=1)
    app._lbl(vices_card, "🕵️  Pequenos Vícios", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 4))
    app._lbl(vices_card, "Gastos recorrentes com projeção anual — pequenas despesas, grande impacto.",
              size=11, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
    app._sep(vices_card, 2)

    th = ctk.CTkFrame(vices_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
    th.grid(row=3, column=0, sticky="ew")
    th.grid_propagate(False)
    th.grid_columnconfigure(0, weight=1)
    for col, lbl in enumerate(["DESCRIÇÃO", "OCORRÊNCIAS", "VALOR MÉDIO", "EST. MENSAL", "EST. ANUAL"]):
        app._lbl(th, lbl, size=9, weight="bold", color=C["muted"],
                  anchor="w" if col == 0 else "center").grid(
            row=0, column=col, padx=(16 if col == 0 else 8, 8), pady=6,
            sticky="ew" if col == 0 else "")

    if not vices:
        app._lbl(vices_card, "Nenhum padrão recorrente encontrado ainda.", color=C["muted"]).grid(
            row=4, column=0, pady=24)
    else:
        for i, v in enumerate(vices):
            rf = ctk.CTkFrame(vices_card, fg_color="transparent")
            rf.grid(row=4 + i * 2, column=0, sticky="ew")
            rf.grid_columnconfigure(0, weight=1)
            app._lbl(rf, v["description"], size=13, weight="bold", anchor="w").grid(
                row=0, column=0, sticky="ew", padx=16, pady=10)
            app._lbl(rf, str(v["count"]),           size=12, mono=True, anchor="center").grid(row=0, column=1, padx=8)
            app._lbl(rf, fin.fmt_brl(v["avg"]),      size=12, mono=True, anchor="center").grid(row=0, column=2, padx=8)
            app._lbl(rf, fin.fmt_brl(v["monthly_est"]), size=12, mono=True, anchor="center").grid(row=0, column=3, padx=8)
            app._lbl(rf, fin.fmt_brl(v["annual_est"]),  size=13, weight="bold",
                      color=C["red"], mono=True, anchor="center").grid(row=0, column=4, padx=(8, 16))
            if i < len(vices) - 1:
                app._sep(vices_card, 4 + i * 2 + 1, padx=16)

    # ── Histórico mensal detalhado ─────────────────────────────────────────────
    hist_card = app._card(scroll, row=2, column=0, sticky="ew")
    hist_card.grid_columnconfigure(0, weight=1)
    app._lbl(hist_card, "Histórico Mensal Detalhado", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 14))
    app._sep(hist_card, 1)

    th2 = ctk.CTkFrame(hist_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
    th2.grid(row=2, column=0, sticky="ew")
    th2.grid_propagate(False)
    th2.grid_columnconfigure(0, weight=1)
    for col, lbl in enumerate(["MÊS", "RECEITAS", "DESPESAS REAIS", "SALDO"]):
        app._lbl(th2, lbl, size=9, weight="bold", color=C["muted"],
                  anchor="w" if col == 0 else "center").grid(
            row=0, column=col, padx=(16 if col == 0 else 8, 8), pady=6,
            sticky="ew" if col == 0 else "")

    for i, h in enumerate(reversed(hist)):
        saldo = h["income"] - h["expenses"]
        clr   = C["green"] if saldo >= 0 else C["red"]
        sign  = "+" if saldo >= 0 else ""
        rf    = ctk.CTkFrame(hist_card, fg_color="transparent")
        rf.grid(row=3 + i * 2, column=0, sticky="ew")
        rf.grid_columnconfigure(0, weight=1)
        app._lbl(rf, h["month"],              size=12, mono=True, anchor="w").grid(row=0, column=0, sticky="ew", padx=16, pady=10)
        app._lbl(rf, fin.fmt_brl(h["income"]),   size=12, mono=True, color=C["green"], anchor="center").grid(row=0, column=1, padx=8)
        app._lbl(rf, fin.fmt_brl(h["expenses"]), size=12, mono=True, color=C["red"],   anchor="center").grid(row=0, column=2, padx=8)
        app._lbl(rf, f"{sign}{fin.fmt_brl(saldo)}", size=12, mono=True, color=clr,     anchor="center").grid(row=0, column=3, padx=(8, 16))
        if i < len(hist) - 1:
            app._sep(hist_card, 3 + i * 2 + 1, padx=16)
