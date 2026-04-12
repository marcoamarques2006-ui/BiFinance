"""BiFinance — Interface gráfica completa."""

from __future__ import annotations

import csv
from datetime import date
from tkinter import filedialog

import customtkinter as ctk

from bifinance import charts as ch
from bifinance import finance as fin
from bifinance.models import (
    EXPENSE_CATEGORIES,
    GOAL_COLORS,
    INCOME_CATEGORIES,
    TX_COLORS,
    TX_ICONS,
    TX_LABELS,
    DollarEntry,
    Goal,
    Settings,
    Transaction,
)
from bifinance.storage import Storage

# ── Design system ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

C = {
    "bg":          "#f5f6fa",
    "sidebar":     "#111827",
    "sidebar_tx":  "#9ca3af",
    "sidebar_act": "#1f2937",
    "sidebar_lbl": "#4b5563",
    "header":      "#ffffff",
    "card":        "#ffffff",
    "border":      "#e5e7eb",
    "text":        "#111827",
    "muted":       "#6b7280",
    "blue":        "#3b82f6",
    "green":       "#22c55e",
    "red":         "#ef4444",
    "muted_bg":    "#f3f4f6",
}

NAV = [
    ("GERAL", [
        ("dashboard",    "📊  Dashboard"),
        ("transactions", "💸  Transações"),
    ]),
    ("PATRIMÔNIO", [
        ("investments", "📈  Investimentos"),
        ("dollar",      "💵  Dólar"),
    ]),
    ("PLANEJAMENTO", [
        ("goals",    "🎯  Metas"),
        ("reports",  "📋  Relatórios"),
    ]),
    ("SISTEMA", [
        ("settings", "⚙️  Configurações"),
    ]),
]


def _tint(hex_color: str, f: float = 0.88) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#{:02x}{:02x}{:02x}".format(
        int(r + (255 - r) * f), int(g + (255 - g) * f), int(b + (255 - b) * f)
    )


class BiFinanceApp(ctk.CTk):
    def __init__(self, storage: Storage | None = None) -> None:
        super().__init__()
        self._s = storage or Storage()
        self.title("BiFinance")
        self.geometry("1160x760")
        self.minsize(900, 600)
        self.configure(fg_color=C["bg"])
        self._nav_btns: dict[str, ctk.CTkButton] = {}
        self._tx_filter: str = "Todos"
        self._page_title = ctk.StringVar(value="Dashboard")
        self._build_layout()
        self._nav_to("dashboard")

    # ══ Layout ════════════════════════════════════════════════════════════════

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sb = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=C["sidebar"])
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        self._build_sidebar(sb)

        right = ctk.CTkFrame(self, corner_radius=0, fg_color=C["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        topbar = ctk.CTkFrame(right, height=56, corner_radius=0, fg_color=C["header"])
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(topbar, textvariable=self._page_title,
                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                      text_color=C["text"], anchor="w").grid(
            row=0, column=0, sticky="w", padx=24, pady=16)
        ctk.CTkFrame(right, height=1, corner_radius=0, fg_color=C["border"]).grid(
            row=0, column=0, sticky="sew")

        self._content = ctk.CTkFrame(right, corner_radius=0, fg_color=C["bg"])
        self._content.grid(row=1, column=0, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self, sb: ctk.CTkFrame) -> None:
        logo = ctk.CTkFrame(sb, fg_color="transparent", height=65)
        logo.pack(fill="x")
        logo.pack_propagate(False)
        badge = ctk.CTkFrame(logo, width=32, height=32, corner_radius=6, fg_color=C["sidebar_act"])
        badge.place(x=16, y=16)
        ctk.CTkLabel(badge, text="💰", font=ctk.CTkFont(size=14)).place(relx=.5, rely=.5, anchor="c")
        ctk.CTkLabel(logo, text="BiFinance",
                      font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                      text_color="#f9fafb").place(x=58, y=16)
        ctk.CTkLabel(logo, text="Gestor Financeiro Pessoal",
                      font=ctk.CTkFont(size=9), text_color=C["sidebar_lbl"]).place(x=58, y=37)
        ctk.CTkFrame(sb, height=1, fg_color=C["sidebar_act"]).pack(fill="x")

        nav = ctk.CTkFrame(sb, fg_color="transparent")
        nav.pack(fill="both", expand=True, padx=8, pady=10)

        for group_label, items in NAV:
            ctk.CTkLabel(nav, text=group_label,
                          font=ctk.CTkFont(size=9, weight="bold"),
                          text_color=C["sidebar_lbl"]).pack(anchor="w", padx=8, pady=(10, 3))
            for key, label in items:
                btn = ctk.CTkButton(
                    nav, text=label, height=36, anchor="w",
                    fg_color="transparent", text_color=C["sidebar_tx"],
                    hover_color=C["sidebar_act"], font=ctk.CTkFont(size=12), corner_radius=6,
                    command=lambda k=key: self._nav_to(k),
                )
                btn.pack(fill="x", pady=1)
                self._nav_btns[key] = btn

    # ══ Navigation ════════════════════════════════════════════════════════════

    _TITLES = {
        "dashboard": "Dashboard", "transactions": "Transações",
        "investments": "Investimentos", "dollar": "Dólar",
        "goals": "Metas", "reports": "Relatórios", "settings": "Configurações",
    }

    def _nav_to(self, key: str) -> None:
        self._page_title.set(self._TITLES.get(key, key))
        for k, btn in self._nav_btns.items():
            btn.configure(fg_color=C["sidebar_act"] if k == key else "transparent",
                           text_color="#f9fafb" if k == key else C["sidebar_tx"])
        for w in self._content.winfo_children():
            w.destroy()
        {
            "dashboard":    self._view_dashboard,
            "transactions": self._view_transactions,
            "investments":  self._view_investments,
            "dollar":       self._view_dollar,
            "goals":        self._view_goals,
            "reports":      self._view_reports,
            "settings":     self._view_settings,
        }[key]()

    # ══ Shared helpers ════════════════════════════════════════════════════════

    def _card(self, parent, **kw) -> ctk.CTkFrame:
        f = ctk.CTkFrame(parent, fg_color=C["card"], border_color=C["border"],
                          border_width=1, corner_radius=8)
        f.grid(**kw)
        return f

    def _lbl(self, parent, text, size=13, weight="normal", color=None,
             mono=False, **kw) -> ctk.CTkLabel:
        return ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family="Consolas" if mono else "Segoe UI", size=size, weight=weight),
            text_color=color or C["text"], **kw)

    def _sep(self, parent, row: int, padx: int = 0) -> None:
        ctk.CTkFrame(parent, height=1, corner_radius=0, fg_color=C["border"]).grid(
            row=row, column=0, columnspan=99, sticky="ew", padx=padx)

    def _scroll(self, parent) -> ctk.CTkScrollableFrame:
        f = ctk.CTkScrollableFrame(parent, fg_color=C["bg"],
                                    scrollbar_button_color=C["border"],
                                    scrollbar_button_hover_color=C["muted"])
        f.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        return f

    def _kpi(self, parent, col: int, title: str, value: str, sub: str,
             sub_color: str, padx=(0, 10)) -> None:
        card = self._card(parent, row=0, column=col, sticky="nsew", padx=padx, pady=(0, 16))
        card.grid_columnconfigure(0, weight=1)
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        top.grid_columnconfigure(0, weight=1)
        self._lbl(top, title, size=10, weight="bold", color=C["muted"]).grid(row=0, column=0, sticky="w")
        ib = ctk.CTkFrame(top, width=26, height=26, corner_radius=5, fg_color=C["muted_bg"])
        ib.grid(row=0, column=1)
        ib.grid_propagate(False)
        self._lbl(card, value, size=20, weight="bold", mono=True).grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 3))
        self._lbl(card, sub, size=11, color=sub_color).grid(
            row=2, column=0, sticky="w", padx=16, pady=(0, 14))

    def _tx_badge(self, parent, tx_type: str) -> None:
        clr = TX_COLORS.get(tx_type, "#94a3b8")
        label = TX_LABELS.get(tx_type, tx_type)
        f = ctk.CTkFrame(parent, fg_color=_tint(clr, 0.85), corner_radius=4, width=110)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=clr, anchor="center").pack(expand=True, fill="both", pady=3)

    # ══ Dashboard ═════════════════════════════════════════════════════════════

    def _view_dashboard(self) -> None:
        scroll = self._scroll(self._content)
        scroll.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        txs      = self._s.load_transactions()
        settings = self._s.load_settings()
        today    = date.today()
        y, m     = today.year, today.month

        cash     = fin.available_cash(txs)
        invested = fin.total_invested_cost(txs)
        income_m = fin.monthly_income(txs, y, m)
        exp_m    = fin.monthly_expenses(txs, y, m)
        divs     = fin.total_dividends(txs)

        # ── KPIs ──────────────────────────────────────────────────────────────
        kpis = [
            ("PATRIMÔNIO TOTAL",   fin.fmt_brl(cash + invested),   f"Caixa {fin.fmt_brl(cash)} + Invest. {fin.fmt_brl(invested)}", C["muted"]),
            ("RECEITA DO MÊS",     fin.fmt_brl(income_m),          fin.fmt_pct((income_m - exp_m) / income_m * 100) + " saldo" if income_m > 0 else "— sem receitas", C["green"] if income_m >= exp_m else C["red"]),
            ("GASTOS DO MÊS",      fin.fmt_brl(exp_m),             "Apenas despesas reais — invest. excluídos", C["red"] if exp_m > 0 else C["muted"]),
            ("PROVENTOS RECEBIDOS", fin.fmt_brl(divs),             f"Investido: {fin.fmt_brl(invested)}", C["blue"]),
        ]
        for col, (title, value, sub, sc) in enumerate(kpis):
            self._kpi(scroll, col, title, value, sub, sc,
                       padx=(0, 10) if col < 3 else 0)

        # ── Gráficos: barras + rosca ───────────────────────────────────────────
        charts_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        charts_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 16))
        charts_frame.grid_columnconfigure(0, weight=2)
        charts_frame.grid_columnconfigure(1, weight=1)

        hist    = fin.monthly_history(txs, 6)
        by_cat  = fin.expenses_by_category(txs, y, m)

        bar_card = self._card(charts_frame, row=0, column=0, sticky="nsew", padx=(0, 8))
        bar_card.grid_columnconfigure(0, weight=1)
        self._lbl(bar_card, "Receitas vs Despesas Reais — Últimos 6 meses",
                   size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
        fig_bar = ch.bar_income_expenses(hist)
        canvas  = ch.embed(fig_bar, bar_card)
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        donut_card = self._card(charts_frame, row=0, column=1, sticky="nsew", padx=(8, 0))
        donut_card.grid_columnconfigure(0, weight=1)
        self._lbl(donut_card, "Gastos por Categoria — Este mês",
                   size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
        fig_donut = ch.donut_categories(by_cat)
        canvas2   = ch.embed(fig_donut, donut_card)
        canvas2.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # ── CDI ───────────────────────────────────────────────────────────────
        cdi_card = self._card(scroll, row=2, column=0, columnspan=4, sticky="ew", pady=(0, 16))
        cdi_card.grid_columnconfigure(0, weight=1)
        self._lbl(cdi_card, f"Portfólio vs CDI ({settings.cdi_rate:.1f}% a.a.) — Últimos 6 meses",
                   size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
        cdi_data = fin.patrimony_vs_cdi(txs, 6, settings.cdi_rate)
        fig_cdi  = ch.area_portfolio_cdi(cdi_data, settings.cdi_rate)
        canvas3  = ch.embed(fig_cdi, cdi_card)
        canvas3.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # ── Transações recentes ────────────────────────────────────────────────
        rec_card = self._card(scroll, row=3, column=0, columnspan=4, sticky="ew")
        rec_card.grid_columnconfigure(0, weight=1)
        recent = sorted(txs, key=lambda t: t.date, reverse=True)[:8]
        hdr = ctk.CTkFrame(rec_card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)
        self._lbl(hdr, "Transações Recentes", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(16, 14))
        self._lbl(hdr, f"Últimas {len(recent)}", size=11, color=C["muted"]).grid(
            row=0, column=1, sticky="e", padx=16)
        self._sep(rec_card, 1)
        if not recent:
            self._lbl(rec_card, "Nenhuma transação registrada.", color=C["muted"]).grid(
                row=2, column=0, pady=24)
        else:
            for i, t in enumerate(recent):
                self._tx_row(rec_card, t, row=2 + i * 2, show_delete=False)
                if i < len(recent) - 1:
                    self._sep(rec_card, 2 + i * 2 + 1, padx=16)

    # ══ Transactions ══════════════════════════════════════════════════════════

    def _tx_row(self, parent, t: Transaction, row: int, show_delete: bool = True) -> None:
        clr  = TX_COLORS.get(t.type, "#94a3b8")
        icon = TX_ICONS.get(t.type, "💳")
        rf   = ctk.CTkFrame(parent, fg_color="transparent")
        rf.grid(row=row, column=0, sticky="ew")
        rf.grid_columnconfigure(2, weight=1)

        av = ctk.CTkFrame(rf, width=36, height=36, corner_radius=18, fg_color=_tint(clr, 0.84))
        av.grid(row=0, column=0, padx=(16, 12), pady=10)
        av.grid_propagate(False)
        ctk.CTkLabel(av, text=icon, font=ctk.CTkFont(size=13)).place(relx=.5, rely=.5, anchor="c")

        info = ctk.CTkFrame(rf, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", padx=(0, 12))
        self._lbl(info, t.description, size=13, weight="bold").grid(row=0, column=0, sticky="w")
        meta = f"{TX_LABELS.get(t.type, t.type)}"
        if t.category:
            meta += f" · {t.category}"
        if t.ticker:
            meta += f" · {t.ticker.upper()}"
        if t.is_recurring:
            meta += " · 🔁 Recorrente"
        self._lbl(info, meta, size=11, color=C["muted"]).grid(row=1, column=0, sticky="w")

        self._lbl(rf, t.date, size=11, color=C["muted"], mono=True).grid(
            row=0, column=2, sticky="e", padx=8)

        sign = "+" if t.type in ("income", "dividend", "investment_sell") else "−"
        self._lbl(rf, f"{sign}{fin.fmt_brl(t.amount)}", size=13, weight="bold",
                   color=clr, mono=True).grid(row=0, column=3, padx=(8, 0))

        if show_delete:
            ctk.CTkButton(
                rf, text="✕", width=30, height=26, corner_radius=5,
                fg_color="transparent", border_color=C["border"], border_width=1,
                text_color=C["muted"], hover_color="#fef2f2",
                command=lambda tid=t.id: (self._s.remove_transaction(tid), self._nav_to("transactions")),
            ).grid(row=0, column=4, padx=(8, 16))

    def _view_transactions(self) -> None:
        outer = ctk.CTkFrame(self._content, fg_color=C["bg"])
        outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # ── Form ──────────────────────────────────────────────────────────────
        form_card = self._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
        form_card.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self._lbl(form_card, "Nova Transação", size=13, weight="bold").grid(
            row=0, column=0, columnspan=6, sticky="w", padx=16, pady=(14, 10))
        self._sep(form_card, 1)

        # Type selector
        self._lbl(form_card, "Tipo", size=11, weight="bold").grid(
            row=2, column=0, sticky="w", padx=12, pady=(10, 3))
        tx_type_var = ctk.StringVar(value="expense")
        type_menu = ctk.CTkOptionMenu(
            form_card, values=list(TX_LABELS.keys()),
            variable=tx_type_var, height=36, corner_radius=6,
            fg_color=C["card"], button_color=C["border"],
            text_color=C["text"], dropdown_fg_color=C["card"],
            dropdown_text_color=C["text"],
        )
        type_menu.grid(row=3, column=0, sticky="ew", padx=12)

        # Description
        self._lbl(form_card, "Descrição", size=11, weight="bold").grid(
            row=2, column=1, sticky="w", padx=8, pady=(10, 3))
        desc_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                               border_color=C["border"], fg_color=C["card"],
                               text_color=C["text"], placeholder_text="Ex: Salário, Mercado, ITUB4…")
        desc_e.grid(row=3, column=1, sticky="ew", padx=8)

        # Amount
        self._lbl(form_card, "Valor (R$)", size=11, weight="bold").grid(
            row=2, column=2, sticky="w", padx=8, pady=(10, 3))
        amount_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                                 border_color=C["border"], fg_color=C["card"],
                                 text_color=C["text"], placeholder_text="0,00")
        amount_e.grid(row=3, column=2, sticky="ew", padx=8)

        # Date
        self._lbl(form_card, "Data", size=11, weight="bold").grid(
            row=2, column=3, sticky="w", padx=8, pady=(10, 3))
        date_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                               border_color=C["border"], fg_color=C["card"],
                               text_color=C["text"])
        date_e.insert(0, date.today().isoformat())
        date_e.grid(row=3, column=3, sticky="ew", padx=8)

        # Context field: category | ticker
        ctx_lbl = ctk.CTkLabel(form_card, text="Categoria",
                                font=ctk.CTkFont(size=11, weight="bold"), text_color=C["text"])
        ctx_lbl.grid(row=2, column=4, sticky="w", padx=8, pady=(10, 3))
        ctx_var = ctk.StringVar(value=EXPENSE_CATEGORIES[0])
        ctx_menu = ctk.CTkOptionMenu(
            form_card, values=EXPENSE_CATEGORIES, variable=ctx_var,
            height=36, corner_radius=6, fg_color=C["card"],
            button_color=C["border"], text_color=C["text"],
            dropdown_fg_color=C["card"], dropdown_text_color=C["text"],
        )
        ctx_menu.grid(row=3, column=4, sticky="ew", padx=8)

        # Qty (investments only)
        qty_lbl = ctk.CTkLabel(form_card, text="Qtd / Cotas",
                                font=ctk.CTkFont(size=11, weight="bold"), text_color=C["text"])
        qty_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"],
                              text_color=C["text"], placeholder_text="100")

        # Recurring checkbox
        recurring_var = ctk.BooleanVar(value=False)
        recurring_cb = ctk.CTkCheckBox(form_card, text="Recorrente", variable=recurring_var,
                                        font=ctk.CTkFont(size=11), text_color=C["text"],
                                        fg_color=C["blue"], border_color=C["border"])

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
                tx_type = tx_type_var.get()
                is_invest = tx_type in ("investment_buy", "investment_sell")
                raw_amt = amount_e.get().strip().replace(",", ".")
                ticker_val = ctx_e.get().strip().upper() if is_invest or tx_type == "dividend" else None
                qty_val = float(qty_e.get().strip()) if is_invest and qty_e.get().strip() else None
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
                self._s.add_transaction(tx)
                desc_e.delete(0, "end")
                amount_e.delete(0, "end")
                msg.configure(text="Transação adicionada.", text_color=C["green"])
            except ValueError as exc:
                msg.configure(text=str(exc), text_color=C["red"])

        # Ticker entry (shown for invest/dividend)
        ctx_e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"],
                              text_color=C["text"], placeholder_text="TICKER")

        submit_btn = ctk.CTkButton(
            form_card, text="Adicionar", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
            command=_submit,
        )
        submit_btn.grid(row=3, column=5, padx=(8, 12), sticky="e")

        msg.grid(row=4, column=0, columnspan=6, padx=12, pady=(6, 10))

        # ── List ──────────────────────────────────────────────────────────────
        txs = self._s.load_transactions()
        list_card = self._card(outer, row=1, column=0, sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(list_card, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)
        self._lbl(hdr, "Histórico de Transações", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 14))
        ctk.CTkOptionMenu(
            hdr, values=["Todos"] + list(TX_LABELS.keys()),
            variable=ctk.StringVar(value=self._tx_filter),
            height=28, width=150, corner_radius=6,
            fg_color=C["muted_bg"], button_color=C["border"],
            text_color=C["text"], dropdown_fg_color=C["card"],
            dropdown_text_color=C["text"],
            command=lambda v: (setattr(self, "_tx_filter", v), self._nav_to("transactions")),
        ).grid(row=0, column=1, padx=8)
        txs_show = [t for t in txs if self._tx_filter == "Todos" or t.type == self._tx_filter]
        self._lbl(hdr, f"{len(txs_show)} registros", size=11, color=C["muted"]).grid(
            row=0, column=2, sticky="e", padx=8)
        ctk.CTkButton(
            hdr, text="Exportar CSV", height=28, corner_radius=6, width=110,
            font=ctk.CTkFont(size=11), fg_color=C["muted_bg"],
            border_color=C["border"], border_width=1,
            text_color=C["text"], hover_color=C["border"],
            command=lambda: self._export_csv(txs),
        ).grid(row=0, column=3, padx=(0, 16))
        self._sep(list_card, 1)

        table = ctk.CTkScrollableFrame(list_card, fg_color=C["card"],
                                        scrollbar_button_color=C["border"])
        table.grid(row=2, column=0, sticky="nsew")
        table.grid_columnconfigure(0, weight=1)

        n = len(txs_show)
        if not txs_show:
            self._lbl(table, "Nenhuma transação ainda.", color=C["muted"]).grid(
                row=0, column=0, pady=40)
            return
        for i, t in enumerate(sorted(txs_show, key=lambda x: x.date, reverse=True)):
            self._tx_row(table, t, row=i * 2)
            if i < n - 1:
                self._sep(table, i * 2 + 1, padx=16)

    # ══ Investments ═══════════════════════════════════════════════════════════

    def _view_investments(self) -> None:
        scroll = self._scroll(self._content)
        scroll.grid_columnconfigure(0, weight=1)

        txs       = self._s.load_transactions()
        prices    = self._s.load_prices()
        positions = fin.portfolio_positions(txs)
        with_pl   = fin.with_pnl(positions, prices)

        total_cost = fin.total_invested_cost(txs)
        total_mkt  = sum(p["market_value"] for p in with_pl.values() if p["current_price"] > 0)
        total_pnl  = total_mkt - total_cost if total_mkt > 0 else 0.0
        divs       = fin.total_dividends(txs)

        # KPIs
        kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        kpi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="ikpi")
        kpi_data = [
            ("CUSTO TOTAL",       fin.fmt_brl(total_cost),  "Valor aportado (PM × Qtd)",  C["muted"]),
            ("VALOR DE MERCADO",  fin.fmt_brl(total_mkt),   "Preços atuais inseridos",     C["blue"]),
            ("P&L NÃO REALIZADO", fin.fmt_brl(total_pnl),   fin.fmt_pct(total_pnl / total_cost * 100) if total_cost > 0 else "—", C["green"] if total_pnl >= 0 else C["red"]),
            ("PROVENTOS",         fin.fmt_brl(divs),        "Dividendos e JCP recebidos",  C["blue"]),
        ]
        for col, (title, val, sub, sc) in enumerate(kpi_data):
            self._kpi(kpi_frame, col, title, val, sub, sc,
                       padx=(0, 10) if col < 3 else 0)

        # Positions table
        table_card = self._card(scroll, row=1, column=0, sticky="ew", pady=(0, 16))
        table_card.grid_columnconfigure(0, weight=1)

        self._lbl(table_card, "Posições em Carteira", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4))
        self._lbl(table_card, "Insira o preço atual para calcular P&L não realizado.",
                   size=11, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        self._sep(table_card, 2)

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
            self._lbl(th, label, size=10, weight="bold", color=C["muted"], **kw).grid(
                row=0, column=col, padx=(16, 4) if col == 0 else 4, pady=8,
                sticky="ew" if col == 1 else "")

        if not with_pl:
            self._lbl(table_card, "Nenhuma posição em carteira.", color=C["muted"]).grid(
                row=4, column=0, pady=24)
        else:
            for i, (ticker, pos) in enumerate(sorted(with_pl.items())):
                rf = ctk.CTkFrame(table_card, fg_color="transparent")
                rf.grid(row=4 + i * 2, column=0, sticky="ew")
                rf.grid_columnconfigure(1, weight=1)

                pnl_clr = C["green"] if pos["pnl"] >= 0 else C["red"]
                pnl_sign = "+" if pos["pnl"] >= 0 else ""

                self._lbl(rf, ticker, size=13, weight="bold", mono=True, width=80, anchor="center").grid(
                    row=0, column=0, padx=(16, 4), pady=10)
                self._lbl(rf, pos["asset_type"], size=11, color=C["muted"], anchor="w").grid(
                    row=0, column=1, sticky="ew", padx=4)
                self._lbl(rf, f"{pos['quantity']:.2f}", size=12, mono=True, width=70, anchor="center").grid(
                    row=0, column=2, padx=4)
                self._lbl(rf, fin.fmt_brl(pos["avg_cost"]), size=12, mono=True, width=90, anchor="center").grid(
                    row=0, column=3, padx=4)

                price_e = ctk.CTkEntry(rf, width=95, height=30, corner_radius=5,
                                        border_color=C["border"], fg_color=C["muted_bg"],
                                        text_color=C["text"])
                if pos["current_price"] > 0:
                    price_e.insert(0, f"{pos['current_price']:.2f}")
                price_e.grid(row=0, column=4, padx=4)

                mkt_lbl = self._lbl(rf, fin.fmt_brl(pos["market_value"]) if pos["current_price"] > 0 else "—",
                                     size=12, mono=True, width=110, anchor="center")
                mkt_lbl.grid(row=0, column=5, padx=4)
                pnl_lbl = self._lbl(rf, f"{pnl_sign}{fin.fmt_brl(pos['pnl'])}" if pos["current_price"] > 0 else "—",
                                     size=12, mono=True, color=pnl_clr if pos["current_price"] > 0 else C["muted"],
                                     width=100, anchor="center")
                pnl_lbl.grid(row=0, column=6, padx=4)
                pnl_pct_lbl = self._lbl(rf, fin.fmt_pct(pos["pnl_pct"]) if pos["current_price"] > 0 else "—",
                                          size=12, mono=True, color=pnl_clr if pos["current_price"] > 0 else C["muted"],
                                          width=80, anchor="center")
                pnl_pct_lbl.grid(row=0, column=7, padx=(4, 16))

                def _save_price(e, t=ticker, ml=mkt_lbl, pl=pnl_lbl, pp=pnl_pct_lbl,
                                 qty=pos["quantity"], cost=pos["total_cost"]) -> None:
                    try:
                        p = float(e.widget.get().replace(",", "."))
                        prices[t] = p
                        self._s.save_prices(prices)
                        mkt = p * qty
                        pnl = mkt - cost
                        pnl_pct = pnl / cost * 100 if cost > 0 else 0.0
                        clr = C["green"] if pnl >= 0 else C["red"]
                        sign = "+" if pnl >= 0 else ""
                        ml.configure(text=fin.fmt_brl(mkt))
                        pl.configure(text=f"{sign}{fin.fmt_brl(pnl)}", text_color=clr)
                        pp.configure(text=fin.fmt_pct(pnl_pct), text_color=clr)
                    except ValueError:
                        pass

                price_e.bind("<FocusOut>", _save_price)
                price_e.bind("<Return>",   _save_price)

                if i < len(with_pl) - 1:
                    self._sep(table_card, 4 + i * 2 + 1, padx=16)

    # ══ Dollar ════════════════════════════════════════════════════════════════

    def _view_dollar(self) -> None:
        outer = ctk.CTkFrame(self._content, fg_color=C["bg"])
        outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        entries  = self._s.load_dollar_entries()
        settings = self._s.load_settings()
        summary  = fin.dollar_summary(entries)

        # Current rate input
        rate_card = self._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
        rate_card.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._lbl(rate_card, "Taxa Atual (BRL/USD) para P&L",
                   size=13, weight="bold").grid(row=0, column=0, columnspan=5,
                                                 sticky="w", padx=16, pady=(14, 10))
        self._sep(rate_card, 1)
        rate_e = ctk.CTkEntry(rate_card, height=38, corner_radius=6,
                               border_color=C["border"], fg_color=C["card"],
                               text_color=C["text"], placeholder_text="Ex: 5,85")
        rate_e.grid(row=2, column=0, sticky="ew", padx=12, pady=10)

        kpi_frame = ctk.CTkFrame(rate_card, fg_color="transparent")
        kpi_frame.grid(row=2, column=1, columnspan=4, sticky="ew", padx=8)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="dkpi")

        total_usd_lbl = self._lbl(kpi_frame, f"USD {summary['total_usd']:,.2f}", size=16, weight="bold", mono=True)
        total_usd_lbl.grid(row=1, column=0, sticky="w", padx=8)
        self._lbl(kpi_frame, "TOTAL EM DÓLAR", size=9, weight="bold", color=C["muted"]).grid(
            row=0, column=0, sticky="w", padx=8)
        self._lbl(kpi_frame, "CUSTO TOTAL (BRL)", size=9, weight="bold", color=C["muted"]).grid(
            row=0, column=1, sticky="w", padx=8)
        self._lbl(kpi_frame, fin.fmt_brl(summary["total_brl"]), size=16, weight="bold", mono=True).grid(
            row=1, column=1, sticky="w", padx=8)
        self._lbl(kpi_frame, "PM EFETIVO (BRL/USD)", size=9, weight="bold", color=C["muted"]).grid(
            row=0, column=2, sticky="w", padx=8)
        avg_lbl = self._lbl(kpi_frame, f"R$ {summary['avg_effective_rate']:.4f}", size=16, weight="bold", mono=True)
        avg_lbl.grid(row=1, column=2, sticky="w", padx=8)
        self._lbl(kpi_frame, "P&L (COM TAXA ATUAL)", size=9, weight="bold", color=C["muted"]).grid(
            row=0, column=3, sticky="w", padx=8)
        pnl_lbl = self._lbl(kpi_frame, "— informe taxa", size=14, color=C["muted"], mono=True)
        pnl_lbl.grid(row=1, column=3, sticky="w", padx=8)

        def _calc_pnl(_e=None) -> None:
            try:
                rate = float(rate_e.get().strip().replace(",", "."))
                s = fin.dollar_summary(entries, rate)
                sign = "+" if s["pnl"] >= 0 else ""
                clr  = C["green"] if s["pnl"] >= 0 else C["red"]
                pnl_lbl.configure(
                    text=f"{sign}{fin.fmt_brl(s['pnl'])} ({fin.fmt_pct(s['pnl_pct'])})",
                    text_color=clr)
            except ValueError:
                pass

        rate_e.bind("<Return>", _calc_pnl)
        rate_e.bind("<FocusOut>", _calc_pnl)

        # Add form
        form_card = self._card(outer, row=1, column=0, sticky="ew", pady=(0, 16))
        form_card.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self._lbl(form_card, "Registrar Compra de Dólar", size=13, weight="bold").grid(
            row=0, column=0, columnspan=6, sticky="w", padx=16, pady=(14, 10))
        self._sep(form_card, 1)

        labels_entries = [
            ("Descrição", "Ex: Banco X, Corretora…"),
            ("Quantidade (USD)", "100.00"),
            ("Taxa Base (BRL/USD)", "5.70"),
            (f"IOF (%, padrão {settings.default_iof_pct})", str(settings.default_iof_pct)),
            ("Spread (%)", "0.0"),
            ("Data", date.today().isoformat()),
        ]
        entries_widgets: list[ctk.CTkEntry] = []
        for col, (lbl, ph) in enumerate(labels_entries):
            self._lbl(form_card, lbl, size=11, weight="bold").grid(
                row=2, column=col, sticky="w", padx=(16 if col == 0 else 8, 8), pady=(10, 3))
            e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"],
                              text_color=C["text"], placeholder_text=ph)
            if col == 3:
                e.insert(0, str(settings.default_iof_pct))
            if col == 5:
                e.insert(0, date.today().isoformat())
            e.grid(row=3, column=col, sticky="ew", padx=(16 if col == 0 else 8, 8))
            entries_widgets.append(e)

        dmsg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
        dmsg.grid(row=4, column=0, columnspan=5, padx=16, pady=(6, 0))

        def _add_dollar() -> None:
            dmsg.configure(text="", text_color=C["red"])
            try:
                desc, usd_s, rate_s, iof_s, spread_s, date_s = [e.get().strip() for e in entries_widgets]
                entry = DollarEntry(
                    date=date_s, description=desc or "Compra de dólar",
                    amount_usd=float(usd_s.replace(",", ".")),
                    exchange_rate=float(rate_s.replace(",", ".")),
                    iof_pct=float(iof_s.replace(",", ".")),
                    spread_pct=float(spread_s.replace(",", ".")),
                )
                entry.validate()
                self._s.add_dollar_entry(entry)
                self._nav_to("dollar")
            except ValueError as exc:
                dmsg.configure(text=str(exc), text_color=C["red"])

        ctk.CTkButton(
            form_card, text="Registrar", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
            command=_add_dollar,
        ).grid(row=3, column=5, padx=(8, 16))

        # Entries list
        list_card = self._card(outer, row=2, column=0, sticky="ew")
        list_card.grid_columnconfigure(0, weight=1)
        self._lbl(list_card, "Compras Registradas", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 14))
        self._sep(list_card, 1)

        th = ctk.CTkFrame(list_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
        th.grid(row=2, column=0, sticky="ew")
        th.grid_propagate(False)
        th.grid_columnconfigure(1, weight=1)
        for col, lbl in enumerate(["DATA", "DESCRIÇÃO", "USD", "TAXA BASE", "IOF%", "SPREAD%", "CUSTO BRL", "PM EFET.", ""]):
            self._lbl(th, lbl, size=9, weight="bold", color=C["muted"], anchor="center").grid(
                row=0, column=col, padx=6, pady=6)

        entries_loaded = self._s.load_dollar_entries()
        for i, e in enumerate(sorted(entries_loaded, key=lambda x: x.date, reverse=True)):
            rf = ctk.CTkFrame(list_card, fg_color="transparent")
            rf.grid(row=3 + i * 2, column=0, sticky="ew")
            rf.grid_columnconfigure(1, weight=1)
            for col, txt in enumerate([
                e.date, e.description, f"$ {e.amount_usd:,.2f}",
                f"R$ {e.exchange_rate:.4f}", f"{e.iof_pct:.2f}%", f"{e.spread_pct:.2f}%",
                fin.fmt_brl(e.total_cost_brl), f"R$ {e.effective_rate:.4f}",
            ]):
                self._lbl(rf, txt, size=11, mono=(col in (2, 3, 6, 7)),
                           anchor="w" if col == 1 else "center").grid(
                    row=0, column=col, padx=6, pady=8, sticky="ew" if col == 1 else "")
            ctk.CTkButton(
                rf, text="✕", width=28, height=24, corner_radius=5,
                fg_color="transparent", border_color=C["border"], border_width=1,
                text_color=C["muted"], hover_color="#fef2f2",
                command=lambda eid=e.id: (self._s.remove_dollar_entry(eid), self._nav_to("dollar")),
            ).grid(row=0, column=8, padx=(4, 14))
            if i < len(entries_loaded) - 1:
                self._sep(list_card, 3 + i * 2 + 1, padx=16)

    # ══ Goals ═════════════════════════════════════════════════════════════════

    def _view_goals(self) -> None:
        outer = ctk.CTkFrame(self._content, fg_color=C["bg"])
        outer.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Add form
        form_card = self._card(outer, row=0, column=0, sticky="ew", pady=(0, 16))
        form_card.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self._lbl(form_card, "Nova Meta", size=13, weight="bold").grid(
            row=0, column=0, columnspan=5, sticky="w", padx=16, pady=(14, 10))
        self._sep(form_card, 1)

        fields = [("Nome da Meta", "Ex: Reserva de emergência…"), ("Valor Alvo (R$)", "10000"),
                  ("Valor Atual (R$)", "0"), ("Prazo (AAAA-MM-DD)", "Opcional")]
        goal_entries: list[ctk.CTkEntry] = []
        for col, (lbl, ph) in enumerate(fields):
            self._lbl(form_card, lbl, size=11, weight="bold").grid(
                row=2, column=col, sticky="w", padx=(16 if col == 0 else 8, 8), pady=(10, 3))
            e = ctk.CTkEntry(form_card, height=36, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"],
                              text_color=C["text"], placeholder_text=ph)
            e.grid(row=3, column=col, sticky="ew", padx=(16 if col == 0 else 8, 8))
            goal_entries.append(e)

        color_var = ctk.StringVar(value=GOAL_COLORS[0])
        ctk.CTkOptionMenu(form_card, values=GOAL_COLORS, variable=color_var,
                           height=36, corner_radius=6, fg_color=C["card"],
                           button_color=C["border"], text_color=C["text"],
                           dropdown_fg_color=C["card"], dropdown_text_color=C["text"]).grid(
            row=3, column=4, padx=8)
        self._lbl(form_card, "Cor", size=11, weight="bold").grid(
            row=2, column=4, sticky="w", padx=8, pady=(10, 3))

        gmsg = ctk.CTkLabel(form_card, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
        gmsg.grid(row=4, column=0, columnspan=5, padx=16, pady=(6, 10))

        def _add_goal() -> None:
            gmsg.configure(text="")
            try:
                name, target_s, current_s, deadline_s = [e.get().strip() for e in goal_entries]
                goal = Goal(
                    name=name, target=float(target_s.replace(",", ".")),
                    current=float(current_s.replace(",", ".")) if current_s else 0.0,
                    deadline=deadline_s or None, color=color_var.get(),
                )
                goal.validate()
                self._s.add_goal(goal)
                self._nav_to("goals")
            except ValueError as exc:
                gmsg.configure(text=str(exc), text_color=C["red"])

        form_card.grid_columnconfigure(5, weight=0)
        ctk.CTkButton(
            form_card, text="Criar Meta", height=36, corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
            command=_add_goal,
        ).grid(row=3, column=5, padx=(8, 16), sticky="e")

        # Goals list
        goals = self._s.load_goals()
        goals_frame = ctk.CTkScrollableFrame(outer, fg_color=C["bg"],
                                              scrollbar_button_color=C["border"])
        goals_frame.grid(row=1, column=0, sticky="nsew")
        goals_frame.grid_columnconfigure((0, 1), weight=1, uniform="gcol")

        if not goals:
            self._lbl(goals_frame, "Nenhuma meta cadastrada ainda.", color=C["muted"]).grid(
                row=0, column=0, columnspan=2, pady=40)
            return

        for i, g in enumerate(goals):
            col = i % 2
            row = i // 2
            card = ctk.CTkFrame(goals_frame, fg_color=C["card"],
                                 border_color=C["border"], border_width=1, corner_radius=8)
            card.grid(row=row, column=col, sticky="nsew",
                       padx=(0, 8) if col == 0 else (8, 0), pady=8)
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
            top.grid_columnconfigure(0, weight=1)
            self._lbl(top, g.name, size=14, weight="bold").grid(row=0, column=0, sticky="w")
            if g.deadline:
                self._lbl(top, f"Prazo: {g.deadline}", size=11, color=C["muted"]).grid(
                    row=0, column=1, sticky="e")

            self._lbl(card, fin.fmt_brl(g.current), size=22, weight="bold", mono=True).grid(
                row=1, column=0, sticky="w", padx=16, pady=(4, 2))
            self._lbl(card, f"de {fin.fmt_brl(g.target)} — faltam {fin.fmt_brl(g.remaining)}",
                       size=11, color=C["muted"]).grid(row=2, column=0, sticky="w", padx=16, pady=(0, 8))

            bar = ctk.CTkProgressBar(card, height=6, corner_radius=3,
                                      progress_color=g.color, fg_color=C["muted_bg"])
            bar.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 4))
            bar.set(g.progress)
            self._lbl(card, f"{g.progress * 100:.0f}% concluído", size=11, color=g.color).grid(
                row=4, column=0, sticky="w", padx=16, pady=(0, 8))

            # Quick update
            upd_frame = ctk.CTkFrame(card, fg_color="transparent")
            upd_frame.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 16))
            upd_frame.grid_columnconfigure(0, weight=1)
            upd_e = ctk.CTkEntry(upd_frame, height=32, corner_radius=6,
                                  border_color=C["border"], fg_color=C["muted_bg"],
                                  text_color=C["text"], placeholder_text="Novo valor atual…")
            upd_e.grid(row=0, column=0, sticky="ew", padx=(0, 8))

            def _upd(goal=g, entry=upd_e) -> None:
                try:
                    v = float(entry.get().strip().replace(",", "."))
                    goal.current = v
                    self._s.update_goal(goal)
                    self._nav_to("goals")
                except ValueError:
                    pass

            ctk.CTkButton(upd_frame, text="Atualizar", height=32, corner_radius=6,
                           fg_color=g.color, hover_color=_tint(g.color, 0.2),
                           text_color="#ffffff", font=ctk.CTkFont(size=11),
                           command=_upd).grid(row=0, column=1)
            ctk.CTkButton(upd_frame, text="✕", width=28, height=32, corner_radius=6,
                           fg_color="transparent", border_color=C["border"], border_width=1,
                           text_color=C["muted"], hover_color="#fef2f2",
                           command=lambda gid=g.id: (self._s.remove_goal(gid), self._nav_to("goals")),
                           ).grid(row=0, column=2, padx=(6, 0))

    # ══ Reports ═══════════════════════════════════════════════════════════════

    def _view_reports(self) -> None:
        scroll = self._scroll(self._content)
        scroll.grid_columnconfigure(0, weight=1)

        txs  = self._s.load_transactions()
        hist = fin.monthly_history(txs, 6)

        # Balance chart
        bal_card = self._card(scroll, row=0, column=0, sticky="ew", pady=(0, 16))
        bal_card.grid_columnconfigure(0, weight=1)
        self._lbl(bal_card, "Saldo Acumulado (Receitas − Despesas Reais) — 6 meses",
                   size=12, weight="bold").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 10))
        fig_bal = ch.line_balance(hist)
        ch.embed(fig_bal, bal_card).get_tk_widget().grid(
            row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Small vices
        vices = fin.small_vices(txs, min_count=2)
        vices_card = self._card(scroll, row=1, column=0, sticky="ew", pady=(0, 16))
        vices_card.grid_columnconfigure(0, weight=1)
        self._lbl(vices_card, "🕵️  Pequenos Vícios", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 4))
        self._lbl(vices_card, "Gastos recorrentes com projeção anual — pequenas despesas, grande impacto.",
                   size=11, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))
        self._sep(vices_card, 2)

        th = ctk.CTkFrame(vices_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
        th.grid(row=3, column=0, sticky="ew")
        th.grid_propagate(False)
        th.grid_columnconfigure(0, weight=1)
        for col, lbl in enumerate(["DESCRIÇÃO", "OCORRÊNCIAS", "VALOR MÉDIO", "EST. MENSAL", "EST. ANUAL"]):
            self._lbl(th, lbl, size=9, weight="bold", color=C["muted"],
                       anchor="w" if col == 0 else "center").grid(
                row=0, column=col, padx=(16 if col == 0 else 8, 8), pady=6,
                sticky="ew" if col == 0 else "")

        if not vices:
            self._lbl(vices_card, "Nenhum padrão recorrente encontrado ainda.", color=C["muted"]).grid(
                row=4, column=0, pady=24)
        else:
            for i, v in enumerate(vices):
                rf = ctk.CTkFrame(vices_card, fg_color="transparent")
                rf.grid(row=4 + i * 2, column=0, sticky="ew")
                rf.grid_columnconfigure(0, weight=1)
                self._lbl(rf, v["description"], size=13, weight="bold", anchor="w").grid(
                    row=0, column=0, sticky="ew", padx=16, pady=10)
                self._lbl(rf, str(v["count"]), size=12, mono=True, anchor="center").grid(
                    row=0, column=1, padx=8)
                self._lbl(rf, fin.fmt_brl(v["avg"]), size=12, mono=True, anchor="center").grid(
                    row=0, column=2, padx=8)
                self._lbl(rf, fin.fmt_brl(v["monthly_est"]), size=12, mono=True, anchor="center").grid(
                    row=0, column=3, padx=8)
                self._lbl(rf, fin.fmt_brl(v["annual_est"]), size=13, weight="bold",
                           color=C["red"], mono=True, anchor="center").grid(
                    row=0, column=4, padx=(8, 16))
                if i < len(vices) - 1:
                    self._sep(vices_card, 4 + i * 2 + 1, padx=16)

        # Monthly breakdown table
        hist_card = self._card(scroll, row=2, column=0, sticky="ew")
        hist_card.grid_columnconfigure(0, weight=1)
        self._lbl(hist_card, "Histórico Mensal Detalhado", size=13, weight="bold").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 14))
        self._sep(hist_card, 1)
        th2 = ctk.CTkFrame(hist_card, fg_color=C["muted_bg"], height=34, corner_radius=0)
        th2.grid(row=2, column=0, sticky="ew")
        th2.grid_propagate(False)
        th2.grid_columnconfigure(0, weight=1)
        for col, lbl in enumerate(["MÊS", "RECEITAS", "DESPESAS REAIS", "SALDO"]):
            self._lbl(th2, lbl, size=9, weight="bold", color=C["muted"],
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
            self._lbl(rf, h["month"], size=12, mono=True, anchor="w").grid(
                row=0, column=0, sticky="ew", padx=16, pady=10)
            self._lbl(rf, fin.fmt_brl(h["income"]), size=12, mono=True, color=C["green"], anchor="center").grid(
                row=0, column=1, padx=8)
            self._lbl(rf, fin.fmt_brl(h["expenses"]), size=12, mono=True, color=C["red"], anchor="center").grid(
                row=0, column=2, padx=8)
            self._lbl(rf, f"{sign}{fin.fmt_brl(saldo)}", size=12, mono=True, color=clr, anchor="center").grid(
                row=0, column=3, padx=(8, 16))
            if i < len(hist) - 1:
                self._sep(hist_card, 3 + i * 2 + 1, padx=16)

    # ══ Settings ══════════════════════════════════════════════════════════════

    def _view_settings(self) -> None:
        outer = ctk.CTkFrame(self._content, fg_color=C["bg"])
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        card = ctk.CTkFrame(outer, width=480, fg_color=C["card"],
                             border_color=C["border"], border_width=1, corner_radius=8)
        card.grid(row=0, column=0, padx=40, pady=32, sticky="n")
        card.grid_columnconfigure(0, weight=1)

        self._lbl(card, "Configurações", size=15, weight="bold").grid(
            row=0, column=0, sticky="w", padx=24, pady=(24, 4))
        self._lbl(card, "Parâmetros usados nos cálculos do dashboard e relatórios.",
                   size=12, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))
        self._sep(card, 2)

        settings = self._s.load_settings()

        def _field(label: str, row: int, placeholder: str, value: str) -> ctk.CTkEntry:
            self._lbl(card, label, size=12, weight="bold").grid(
                row=row, column=0, sticky="w", padx=24, pady=(16, 4))
            e = ctk.CTkEntry(card, height=40, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"], text_color=C["text"],
                              placeholder_text=placeholder)
            e.insert(0, value)
            e.grid(row=row + 1, column=0, sticky="ew", padx=24)
            return e

        cdi_e = _field("Taxa CDI (% a.a.)", 3, "Ex: 10.75", str(settings.cdi_rate))
        iof_e = _field("IOF padrão para compra de dólar (%)", 5, "Ex: 1.1", str(settings.default_iof_pct))

        self._sep(card, 7)
        smsg = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12), text_color=C["red"])
        smsg.grid(row=8, column=0, padx=24, pady=(12, 0))

        def _save() -> None:
            smsg.configure(text="")
            try:
                s = Settings(
                    cdi_rate=float(cdi_e.get().strip().replace(",", ".")),
                    default_iof_pct=float(iof_e.get().strip().replace(",", ".")),
                )
                self._s.save_settings(s)
                smsg.configure(text="Configurações salvas.", text_color=C["green"])
            except ValueError:
                smsg.configure(text="Valores inválidos.", text_color=C["red"])

        ctk.CTkButton(
            card, text="Salvar Configurações", height=42, corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
            command=_save,
        ).grid(row=9, column=0, sticky="ew", padx=24, pady=(12, 24))


    def _export_csv(self, txs: list[Transaction]) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="bifinance_transacoes.csv",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["Data", "Tipo", "Descrição", "Valor (R$)", "Categoria", "Ticker"])
            for t in sorted(txs, key=lambda x: x.date, reverse=True):
                w.writerow([
                    t.date, TX_LABELS.get(t.type, t.type), t.description,
                    f"{t.amount:.2f}", t.category or "", t.ticker or "",
                ])


def main() -> None:
    app = BiFinanceApp()
    app.mainloop()
