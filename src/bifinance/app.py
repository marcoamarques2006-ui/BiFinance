"""BiFinance — shell da aplicação."""

from __future__ import annotations

import csv
import hashlib
from tkinter import filedialog

import customtkinter as ctk

from bifinance import finance as fin
from bifinance.models import TX_COLORS, TX_ICONS, TX_LABELS, Transaction
from bifinance.storage import Storage
from bifinance.theme import NAV, C, _tint
from bifinance.views import (
    budgets,
    dashboard,
    dollar,
    goals,
    investments,
    reports,
    transactions,
)
from bifinance.views import settings as settings_view

# ── Aparência global ───────────────────────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


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
        ctk.CTkLabel(
            topbar, textvariable=self._page_title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=C["text"], anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=16)
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

        bottom = ctk.CTkFrame(sb, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=8, pady=(0, 12))
        ctk.CTkButton(
            bottom, text="🔒  Bloquear", height=36, anchor="w",
            fg_color="transparent", text_color=C["sidebar_tx"],
            hover_color=C["sidebar_act"], font=ctk.CTkFont(size=12), corner_radius=6,
            command=self._lock,
        ).pack(fill="x")

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

    # ══ Navegação ═════════════════════════════════════════════════════════════

    _TITLES = {
        "dashboard":    "Dashboard",
        "transactions": "Transações",
        "investments":  "Investimentos",
        "dollar":       "Dólar",
        "goals":        "Metas",
        "budgets":      "Orçamento",
        "reports":      "Relatórios",
        "settings":     "Configurações",
    }

    _VIEWS = {
        "dashboard":    dashboard,
        "transactions": transactions,
        "investments":  investments,
        "dollar":       dollar,
        "goals":        goals,
        "budgets":      budgets,
        "reports":      reports,
        "settings":     settings_view,
    }

    def _nav_to(self, key: str) -> None:
        self._page_title.set(self._TITLES.get(key, key))
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color=C["sidebar_act"] if k == key else "transparent",
                text_color="#f9fafb" if k == key else C["sidebar_tx"],
            )
        for w in self._content.winfo_children():
            w.destroy()
        self._VIEWS[key].render(self)

    # ══ Helpers compartilhados ════════════════════════════════════════════════

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
        meta = TX_LABELS.get(t.type, t.type)
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
                command=lambda tid=t.id: (
                    self._s.remove_transaction(tid), self._nav_to("transactions")
                ),
            ).grid(row=0, column=4, padx=(8, 16))

    def _lock(self) -> None:
        pin_hash = self._s.load_pin_hash()
        if not pin_hash:
            return
        self.withdraw()
        win = ctk.CTkToplevel(self)
        win.title("BiFinance — Bloqueado")
        win.geometry("340x230")
        win.resizable(False, False)
        win.configure(fg_color=C["bg"])
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), self.destroy()))

        ctk.CTkLabel(win, text="BiFinance",
                      font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                      text_color=C["text"]).pack(pady=(40, 4))
        ctk.CTkLabel(win, text="Digite seu PIN para continuar",
                      font=ctk.CTkFont(size=12), text_color=C["muted"]).pack(pady=(0, 16))
        pin_e = ctk.CTkEntry(win, show="*", width=220, height=42, corner_radius=6,
                              border_color=C["border"], fg_color=C["card"],
                              text_color=C["text"], placeholder_text="PIN")
        pin_e.pack()
        pin_e.focus()
        msg = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
        msg.pack(pady=4)

        def _check() -> None:
            if hashlib.sha256(pin_e.get().encode()).hexdigest() == pin_hash:
                win.destroy()
                self.deiconify()
            else:
                msg.configure(text="PIN incorreto.")
                pin_e.delete(0, "end")

        ctk.CTkButton(win, text="Entrar", width=220, height=42, corner_radius=6,
                       font=ctk.CTkFont(size=13, weight="bold"),
                       fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
                       command=_check).pack()
        pin_e.bind("<Return>", lambda _: _check())

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


def _show_login(pin_hash: str) -> bool:
    win = ctk.CTk()
    win.title("BiFinance")
    win.geometry("340x230")
    win.resizable(False, False)
    win.configure(fg_color=C["bg"])
    authenticated = [False]

    ctk.CTkLabel(win, text="BiFinance",
                  font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                  text_color=C["text"]).pack(pady=(40, 4))
    ctk.CTkLabel(win, text="Digite seu PIN para continuar",
                  font=ctk.CTkFont(size=12), text_color=C["muted"]).pack(pady=(0, 16))
    pin_e = ctk.CTkEntry(win, show="*", width=220, height=42, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text="PIN")
    pin_e.pack()
    msg = ctk.CTkLabel(win, text="", font=ctk.CTkFont(size=11), text_color=C["red"])
    msg.pack(pady=4)

    def _check() -> None:
        if hashlib.sha256(pin_e.get().encode()).hexdigest() == pin_hash:
            authenticated[0] = True
            win.destroy()
        else:
            msg.configure(text="PIN incorreto.")
            pin_e.delete(0, "end")

    ctk.CTkButton(win, text="Entrar", width=220, height=42, corner_radius=6,
                   font=ctk.CTkFont(size=13, weight="bold"),
                   fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
                   command=_check).pack()
    pin_e.bind("<Return>", lambda _: _check())
    win.mainloop()
    return authenticated[0]


def main() -> None:
    storage  = Storage()
    pin_hash = storage.load_pin_hash()
    if pin_hash and not _show_login(pin_hash):
        return
    app = BiFinanceApp(storage)
    app.mainloop()
