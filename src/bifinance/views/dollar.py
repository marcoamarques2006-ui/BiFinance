"""View: Dólar."""

from __future__ import annotations

import threading
from datetime import date

import customtkinter as ctk

from bifinance import api_client
from bifinance import finance as fin
from bifinance.models import DollarEntry
from bifinance.theme import C


def render(app) -> None:
    outer = ctk.CTkFrame(app._content, fg_color=C["bg"])
    outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(1, weight=1)

    entries  = app._s.load_dollar_entries()
    settings = app._s.load_settings()
    summary  = fin.dollar_summary(entries)

    # ── Taxa atual / P&L ──────────────────────────────────────────────────────
    rate_card = app._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
    rate_card.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
    app._lbl(rate_card, "Taxa Atual (BRL/USD) para P&L",
              size=13, weight="bold").grid(row=0, column=0, columnspan=5,
                                            sticky="w", padx=16, pady=(14, 10))
    app._sep(rate_card, 1)
    fetch_frame = ctk.CTkFrame(rate_card, fg_color="transparent")
    fetch_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=10)
    fetch_frame.grid_columnconfigure(0, weight=1)

    rate_e = ctk.CTkEntry(fetch_frame, height=38, corner_radius=6,
                           border_color=C["border"], fg_color=C["card"],
                           text_color=C["text"], placeholder_text="Ex: 5,85")
    rate_e.grid(row=0, column=0, sticky="ew")

    fetch_btn = ctk.CTkButton(
        fetch_frame, text="Buscar Cotação", height=30, corner_radius=6,
        font=ctk.CTkFont(size=11),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
    )
    fetch_btn.grid(row=1, column=0, sticky="ew", pady=(4, 0))

    kpi_frame = ctk.CTkFrame(rate_card, fg_color="transparent")
    kpi_frame.grid(row=2, column=1, columnspan=4, sticky="ew", padx=8)
    kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="dkpi")

    app._lbl(kpi_frame, "TOTAL EM DÓLAR", size=9, weight="bold", color=C["muted"]).grid(
        row=0, column=0, sticky="w", padx=8)
    app._lbl(kpi_frame, f"USD {summary['total_usd']:,.2f}", size=16, weight="bold", mono=True).grid(
        row=1, column=0, sticky="w", padx=8)
    app._lbl(kpi_frame, "CUSTO TOTAL (BRL)", size=9, weight="bold", color=C["muted"]).grid(
        row=0, column=1, sticky="w", padx=8)
    app._lbl(kpi_frame, fin.fmt_brl(summary["total_brl"]), size=16, weight="bold", mono=True).grid(
        row=1, column=1, sticky="w", padx=8)
    app._lbl(kpi_frame, "PM EFETIVO (BRL/USD)", size=9, weight="bold", color=C["muted"]).grid(
        row=0, column=2, sticky="w", padx=8)
    app._lbl(kpi_frame, f"R$ {summary['avg_effective_rate']:.4f}", size=16, weight="bold", mono=True).grid(
        row=1, column=2, sticky="w", padx=8)
    app._lbl(kpi_frame, "P&L (COM TAXA ATUAL)", size=9, weight="bold", color=C["muted"]).grid(
        row=0, column=3, sticky="w", padx=8)
    pnl_lbl = app._lbl(kpi_frame, "— informe taxa", size=14, color=C["muted"], mono=True)
    pnl_lbl.grid(row=1, column=3, sticky="w", padx=8)

    def _calc_pnl(_e=None) -> None:
        try:
            rate = float(rate_e.get().strip().replace(",", "."))
            s    = fin.dollar_summary(entries, rate)
            sign = "+" if s["pnl"] >= 0 else ""
            clr  = C["green"] if s["pnl"] >= 0 else C["red"]
            pnl_lbl.configure(
                text=f"{sign}{fin.fmt_brl(s['pnl'])} ({fin.fmt_pct(s['pnl_pct'])})",
                text_color=clr)
        except ValueError:
            pass

    rate_e.bind("<Return>",   _calc_pnl)
    rate_e.bind("<FocusOut>", _calc_pnl)

    def _fetch_rate() -> None:
        fetch_btn.configure(text="Buscando…", state="disabled")

        def _task() -> None:
            rate = api_client.fetch_usd_brl()
            if rate is not None:
                rate_e.delete(0, "end")
                rate_e.insert(0, f"{rate:.4f}")
                _calc_pnl()
            else:
                pnl_lbl.configure(text="Falha ao buscar cotação", text_color=C["red"])
            fetch_btn.configure(text="Buscar Cotação", state="normal")

        threading.Thread(target=_task, daemon=True).start()

    fetch_btn.configure(command=_fetch_rate)

    # ── Formulário de compra ───────────────────────────────────────────────────
    form_card = app._card(outer, row=1, column=0, sticky="ew", pady=(0, 16))
    form_card.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
    app._lbl(form_card, "Registrar Compra de Dólar", size=13, weight="bold").grid(
        row=0, column=0, columnspan=6, sticky="w", padx=16, pady=(14, 10))
    app._sep(form_card, 1)

    labels_entries = [
        ("Descrição",                           "Ex: Banco X, Corretora…"),
        ("Quantidade (USD)",                     "100.00"),
        ("Taxa Base (BRL/USD)",                  "5.70"),
        (f"IOF (%, padrão {settings.default_iof_pct})", str(settings.default_iof_pct)),
        ("Spread (%)",                           "0.0"),
        ("Data",                                 date.today().isoformat()),
    ]
    entry_widgets: list[ctk.CTkEntry] = []
    for col, (lbl, ph) in enumerate(labels_entries):
        app._lbl(form_card, lbl, size=11, weight="bold").grid(
            row=2, column=col, sticky="w",
            padx=(16 if col == 0 else 8, 8), pady=(10, 3))
        e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text=ph)
        if col == 3:
            e.insert(0, str(settings.default_iof_pct))
        if col == 5:
            e.insert(0, date.today().isoformat())
        e.grid(row=3, column=col, sticky="ew", padx=(16 if col == 0 else 8, 8))
        entry_widgets.append(e)

    dmsg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
    dmsg.grid(row=4, column=0, columnspan=5, padx=16, pady=(6, 0))

    def _add_dollar() -> None:
        dmsg.configure(text="", text_color=C["red"])
        try:
            desc, usd_s, rate_s, iof_s, spread_s, date_s = [e.get().strip() for e in entry_widgets]
            entry = DollarEntry(
                date=date_s,
                description=desc or "Compra de dólar",
                amount_usd=float(usd_s.replace(",", ".")),
                exchange_rate=float(rate_s.replace(",", ".")),
                iof_pct=float(iof_s.replace(",", ".")),
                spread_pct=float(spread_s.replace(",", ".")),
            )
            entry.validate()
            app._s.add_dollar_entry(entry)
            app._nav_to("dollar")
        except ValueError as exc:
            dmsg.configure(text=str(exc), text_color=C["red"])

    ctk.CTkButton(
        form_card, text="Registrar", height=36, corner_radius=6,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
        command=_add_dollar,
    ).grid(row=3, column=5, padx=(8, 16))

    # ── Lista de compras ───────────────────────────────────────────────────────
    list_card = app._card(outer, row=2, column=0, sticky="ew")
    list_card.grid_columnconfigure(0, weight=1)
    app._lbl(list_card, "Compras Registradas", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 14))
    app._sep(list_card, 1)

    th = ctk.CTkFrame(list_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
    th.grid(row=2, column=0, sticky="ew")
    th.grid_propagate(False)
    th.grid_columnconfigure(1, weight=1)
    for col, lbl in enumerate(
        ["DATA", "DESCRIÇÃO", "USD", "TAXA BASE", "IOF%", "SPREAD%", "CUSTO BRL", "PM EFET.", ""]
    ):
        app._lbl(th, lbl, size=9, weight="bold", color=C["muted"], anchor="center").grid(
            row=0, column=col, padx=6, pady=6)

    entries_loaded = app._s.load_dollar_entries()
    for i, e in enumerate(sorted(entries_loaded, key=lambda x: x.date, reverse=True)):
        rf = ctk.CTkFrame(list_card, fg_color="transparent")
        rf.grid(row=3 + i * 2, column=0, sticky="ew")
        rf.grid_columnconfigure(1, weight=1)
        for col, txt in enumerate([
            e.date, e.description, f"$ {e.amount_usd:,.2f}",
            f"R$ {e.exchange_rate:.4f}", f"{e.iof_pct:.2f}%", f"{e.spread_pct:.2f}%",
            fin.fmt_brl(e.total_cost_brl), f"R$ {e.effective_rate:.4f}",
        ]):
            app._lbl(rf, txt, size=11, mono=(col in (2, 3, 6, 7)),
                      anchor="w" if col == 1 else "center").grid(
                row=0, column=col, padx=6, pady=8, sticky="ew" if col == 1 else "")
        ctk.CTkButton(
            rf, text="✕", width=28, height=24, corner_radius=5,
            fg_color="transparent", border_color=C["border"], border_width=1,
            text_color=C["muted"], hover_color="#fef2f2",
            command=lambda eid=e.id: (app._s.remove_dollar_entry(eid), app._nav_to("dollar")),
        ).grid(row=0, column=8, padx=(4, 14))
        if i < len(entries_loaded) - 1:
            app._sep(list_card, 3 + i * 2 + 1, padx=16)
