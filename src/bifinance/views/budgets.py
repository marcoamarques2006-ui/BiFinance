"""View: Orçamento Mensal por Categoria."""

from __future__ import annotations

from datetime import date

import customtkinter as ctk

from bifinance import finance as fin
from bifinance.models import EXPENSE_CATEGORIES, Budget
from bifinance.theme import C

# Cores por status do orçamento
_STATUS_COLOR = {
    "ok":        C["green"],
    "alerta":    "#f59e0b",
    "estourado": C["red"],
}
_STATUS_LABEL = {
    "ok":        "Dentro do orçamento",
    "alerta":    "Perto do limite",
    "estourado": "Limite estourado",
}


def render(app) -> None:
    outer = ctk.CTkFrame(app._content, fg_color=C["bg"])
    outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(2, weight=1)

    today = date.today()

    # ── Formulário ────────────────────────────────────────────────────────────
    form_card = app._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
    form_card.grid_columnconfigure((0, 1), weight=1)
    app._lbl(form_card, "Novo Orçamento Mensal", size=13, weight="bold").grid(
        row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(14, 10))
    app._sep(form_card, 1)

    app._lbl(form_card, "Categoria", size=11, weight="bold").grid(
        row=2, column=0, sticky="w", padx=(16, 8), pady=(10, 3))
    cat_var = ctk.StringVar(value=EXPENSE_CATEGORIES[0])
    ctk.CTkOptionMenu(
        form_card, values=EXPENSE_CATEGORIES, variable=cat_var,
        height=36, corner_radius=6, fg_color=C["card"],
        button_color=C["border"], text_color=C["text"],
        dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
    ).grid(row=3, column=0, sticky="ew", padx=(16, 8))

    app._lbl(form_card, "Limite Mensal (R$)", size=11, weight="bold").grid(
        row=2, column=1, sticky="w", padx=8, pady=(10, 3))
    limit_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                           border_color=C["border"], fg_color=C["card"],
                           text_color=C["text"], placeholder_text="800")
    limit_e.grid(row=3, column=1, sticky="ew", padx=8)

    bmsg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
    bmsg.grid(row=4, column=0, columnspan=3, padx=16, pady=(6, 10))

    def _add_budget() -> None:
        bmsg.configure(text="")
        try:
            budget = Budget(
                category=cat_var.get(),
                limit=float(limit_e.get().strip().replace(",", ".")),
            )
            budget.validate()
            app._s.add_budget(budget)
            app._nav_to("budgets")
        except ValueError as exc:
            bmsg.configure(text=str(exc), text_color=C["red"])

    form_card.grid_columnconfigure(2, weight=0)
    ctk.CTkButton(
        form_card, text="Definir Orçamento", height=36, corner_radius=6,
        font=ctk.CTkFont(size=12, weight="bold"),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
        command=_add_budget,
    ).grid(row=3, column=2, padx=(8, 16), sticky="e")

    # ── Resumo do mês ───────────────────────────────────────────────────────────
    budgets = app._s.load_budgets()
    txs = app._s.load_transactions()
    status = fin.budget_status(txs, budgets, today.year, today.month)

    total_limit = fin.total_budgeted(budgets)
    total_spent = sum(s["spent"] for s in status)
    sub_color = C["red"] if total_spent > total_limit > 0 else C["muted"]
    app._lbl(
        outer,
        f"{today.month:02d}/{today.year}  ·  Gasto {fin.fmt_brl(total_spent)} "
        f"de {fin.fmt_brl(total_limit)} orçados",
        size=12, color=sub_color,
    ).grid(row=1, column=0, sticky="w", pady=(0, 10))

    # ── Lista de orçamentos ─────────────────────────────────────────────────────
    body = ctk.CTkScrollableFrame(outer, fg_color=C["bg"],
                                  scrollbar_button_color=C["border"])
    body.grid(row=2, column=0, sticky="nsew")
    body.grid_columnconfigure((0, 1), weight=1, uniform="bcol")

    if not status:
        app._lbl(body, "Nenhum orçamento definido. Defina um limite por categoria acima.",
                 color=C["muted"]).grid(row=0, column=0, columnspan=2, pady=40)
        return

    # mapa categoria → id para remoção
    id_by_cat = {b.category: b.id for b in budgets}

    for i, s in enumerate(status):
        col = i % 2
        row = i // 2
        color = _STATUS_COLOR[s["status"]]

        card = ctk.CTkFrame(body, fg_color=C["card"],
                            border_color=C["border"], border_width=1, corner_radius=8)
        card.grid(row=row, column=col, sticky="nsew",
                  padx=(0, 8) if col == 0 else (8, 0), pady=8)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        top.grid_columnconfigure(0, weight=1)
        app._lbl(top, s["category"], size=14, weight="bold").grid(row=0, column=0, sticky="w")
        app._lbl(top, _STATUS_LABEL[s["status"]], size=11, weight="bold",
                 color=color).grid(row=0, column=1, sticky="e")

        app._lbl(card, fin.fmt_brl(s["spent"]), size=22, weight="bold", mono=True).grid(
            row=1, column=0, sticky="w", padx=16, pady=(4, 2))
        remaining_txt = (
            f"de {fin.fmt_brl(s['limit'])} — "
            + (f"restam {fin.fmt_brl(s['remaining'])}" if s["remaining"] >= 0
               else f"excedeu {fin.fmt_brl(-s['remaining'])}")
        )
        app._lbl(card, remaining_txt, size=11, color=C["muted"]).grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 8))

        bar = ctk.CTkProgressBar(card, height=6, corner_radius=3,
                                 progress_color=color, fg_color=C["muted_bg"])
        bar.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 4))
        bar.set(min(1.0, s["pct"] / 100))
        app._lbl(card, f"{s['pct']:.0f}% do limite", size=11, color=color).grid(
            row=4, column=0, sticky="w", padx=16, pady=(0, 12))

        ctk.CTkButton(
            card, text="✕  Remover", height=30, corner_radius=6,
            fg_color="transparent", border_color=C["border"], border_width=1,
            text_color=C["muted"], hover_color="#fef2f2", font=ctk.CTkFont(size=11),
            command=lambda bid=id_by_cat.get(s["category"]): (
                app._s.remove_budget(bid), app._nav_to("budgets")
            ),
        ).grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 16))
