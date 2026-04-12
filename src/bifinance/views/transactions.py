"""View: Transações."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from bifinance.models import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    TX_LABELS,
    Transaction,
)
from bifinance.theme import C


def render(app) -> None:
    outer = ctk.CTkFrame(app._content, fg_color=C["bg"])
    outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(1, weight=1)

    # ── Formulário ────────────────────────────────────────────────────────────
    form_card = app._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
    form_card.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

    app._lbl(form_card, "Nova Transação", size=13, weight="bold").grid(
        row=0, column=0, columnspan=6, sticky="w", padx=16, pady=(14, 10))
    app._sep(form_card, 1)

    app._lbl(form_card, "Tipo", size=11, weight="bold").grid(
        row=2, column=0, sticky="w", padx=12, pady=(10, 3))
    tx_type_var = ctk.StringVar(value="expense")
    type_menu = ctk.CTkOptionMenu(
        form_card, values=list(TX_LABELS.keys()), variable=tx_type_var,
        height=36, corner_radius=6, fg_color=C["card"], button_color=C["border"],
        text_color=C["text"], dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
    )
    type_menu.grid(row=3, column=0, sticky="ew", padx=12)

    app._lbl(form_card, "Descrição", size=11, weight="bold").grid(
        row=2, column=1, sticky="w", padx=8, pady=(10, 3))
    desc_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                           border_color=C["border"], fg_color=C["card"],
                           text_color=C["text"], placeholder_text="Ex: Salário, Mercado, ITUB4…")
    desc_e.grid(row=3, column=1, sticky="ew", padx=8)

    app._lbl(form_card, "Valor (R$)", size=11, weight="bold").grid(
        row=2, column=2, sticky="w", padx=8, pady=(10, 3))
    amount_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                             border_color=C["border"], fg_color=C["card"],
                             text_color=C["text"], placeholder_text="0,00")
    amount_e.grid(row=3, column=2, sticky="ew", padx=8)

    app._lbl(form_card, "Data", size=11, weight="bold").grid(
        row=2, column=3, sticky="w", padx=8, pady=(10, 3))
    date_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                           border_color=C["border"], fg_color=C["card"], text_color=C["text"])
    date_e.insert(0, date.today().isoformat())
    date_e.grid(row=3, column=3, sticky="ew", padx=8)

    ctx_lbl = ctk.CTkLabel(form_card, text="Categoria",
                            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["text"])
    ctx_lbl.grid(row=2, column=4, sticky="w", padx=8, pady=(10, 3))
    ctx_var = ctk.StringVar(value=EXPENSE_CATEGORIES[0])
    ctx_menu = ctk.CTkOptionMenu(
        form_card, values=EXPENSE_CATEGORIES, variable=ctx_var,
        height=36, corner_radius=6, fg_color=C["card"], button_color=C["border"],
        text_color=C["text"], dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
    )
    ctx_menu.grid(row=3, column=4, sticky="ew", padx=8)

    qty_lbl = ctk.CTkLabel(form_card, text="Qtd / Cotas",
                            font=ctk.CTkFont(size=11, weight="bold"), text_color=C["text"])
    qty_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text="100")

    recurring_var = ctk.BooleanVar(value=False)
    recurring_cb = ctk.CTkCheckBox(form_card, text="Recorrente", variable=recurring_var,
                                    font=ctk.CTkFont(size=11), text_color=C["text"],
                                    fg_color=C["blue"], border_color=C["border"])

    ctx_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text="TICKER")

    msg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])

    def _on_type_change(val: str) -> None:
        is_invest = val in ("investment_buy", "investment_sell")
        is_income = val == "income"
        if is_invest:
            ctx_lbl.configure(text="Ticker")
            ctx_var.set("")
            ctx_menu.grid_remove()
            qty_lbl.grid(row=2, column=4, sticky="w", padx=8, pady=(10, 3))
            qty_e.grid(row=3, column=4, sticky="ew", padx=8)
            recurring_cb.grid_remove()
        elif val == "dividend":
            ctx_lbl.configure(text="Ticker")
            ctx_var.set("")
            ctx_menu.grid_remove()
            qty_lbl.grid_remove()
            qty_e.grid_remove()
            recurring_cb.grid_remove()
        else:
            ctx_lbl.configure(text="Categoria")
            ctx_menu.configure(values=INCOME_CATEGORIES if is_income else EXPENSE_CATEGORIES)
            ctx_var.set((INCOME_CATEGORIES if is_income else EXPENSE_CATEGORIES)[0])
            ctx_menu.grid(row=3, column=4, sticky="ew", padx=8)
            qty_lbl.grid_remove()
            qty_e.grid_remove()
            recurring_cb.grid(row=3, column=5, padx=8)

    type_menu.configure(command=_on_type_change)
    recurring_cb.grid(row=3, column=5, padx=8)

    def _submit() -> None:
        msg.configure(text="", text_color=C["red"])
        try:
            tx_type   = tx_type_var.get()
            is_invest = tx_type in ("investment_buy", "investment_sell")
            raw_amt   = amount_e.get().strip().replace(",", ".")
            ticker_val = ctx_e.get().strip().upper() if is_invest or tx_type == "dividend" else None
            qty_val    = float(qty_e.get().strip()) if is_invest and qty_e.get().strip() else None
            tx = Transaction(
                type=tx_type,
                description=desc_e.get().strip(),
                amount=float(raw_amt) if raw_amt else 0.0,
                date=date_e.get().strip(),
                category=ctx_var.get() if not is_invest and tx_type != "dividend" else None,
                is_recurring=recurring_var.get(),
                ticker=ticker_val,
                quantity=qty_val,
            )
            tx.validate()
            app._s.add_transaction(tx)
            desc_e.delete(0, "end")
            amount_e.delete(0, "end")
            msg.configure(text="Transação adicionada.", text_color=C["green"])
        except ValueError as exc:
            msg.configure(text=str(exc), text_color=C["red"])

    ctk.CTkButton(
        form_card, text="Adicionar", height=36, corner_radius=6,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
        command=_submit,
    ).grid(row=3, column=5, padx=(8, 12), sticky="e")
    msg.grid(row=4, column=0, columnspan=6, padx=12, pady=(6, 10))

    # ── Lista ─────────────────────────────────────────────────────────────────
    txs = app._s.load_transactions()
    list_card = app._card(outer, row=1, column=0, sticky="nsew")
    list_card.grid_columnconfigure(0, weight=1)
    list_card.grid_rowconfigure(1, weight=1)

    hdr = ctk.CTkFrame(list_card, fg_color="transparent")
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_columnconfigure(0, weight=1)
    app._lbl(hdr, "Histórico de Transações", size=13, weight="bold").grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 14))
    ctk.CTkOptionMenu(
        hdr, values=["Todos"] + list(TX_LABELS.keys()),
        variable=ctk.StringVar(value=app._tx_filter),
        height=28, width=150, corner_radius=6,
        fg_color=C["muted_bg"], button_color=C["border"],
        text_color=C["text"], dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
        command=lambda v: (setattr(app, "_tx_filter", v), app._nav_to("transactions")),
    ).grid(row=0, column=1, padx=8)
    txs_show = [t for t in txs if app._tx_filter == "Todos" or t.type == app._tx_filter]
    app._lbl(hdr, f"{len(txs_show)} registros", size=11, color=C["muted"]).grid(
        row=0, column=2, sticky="e", padx=8)
    ctk.CTkButton(
        hdr, text="Exportar CSV", height=28, corner_radius=6, width=110,
        font=ctk.CTkFont(size=11), fg_color=C["muted_bg"],
        border_color=C["border"], border_width=1,
        text_color=C["text"], hover_color=C["border"],
        command=lambda: app._export_csv(txs),
    ).grid(row=0, column=3, padx=(0, 16))
    app._sep(list_card, 1)

    table = ctk.CTkScrollableFrame(list_card, fg_color=C["card"],
                                    scrollbar_button_color=C["border"])
    table.grid(row=2, column=0, sticky="nsew")
    table.grid_columnconfigure(0, weight=1)

    n = len(txs_show)
    if not txs_show:
        app._lbl(table, "Nenhuma transação ainda.", color=C["muted"]).grid(
            row=0, column=0, pady=40)
        return
    for i, t in enumerate(sorted(txs_show, key=lambda x: x.date, reverse=True)):
        app._tx_row(table, t, row=i * 2)
        if i < n - 1:
            app._sep(table, i * 2 + 1, padx=16)
