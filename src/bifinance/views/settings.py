"""View: Configurações."""

from __future__ import annotations

import hashlib

import customtkinter as ctk

from bifinance.models import Settings
from bifinance.theme import C


def render(app) -> None:
    outer = ctk.CTkFrame(app._content, fg_color=C["bg"])
    outer.grid(row=0, column=0, sticky="nsew")
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    card = ctk.CTkFrame(outer, width=480, fg_color=C["card"],
                         border_color=C["border"], border_width=1, corner_radius=8)
    card.grid(row=0, column=0, padx=40, pady=32, sticky="n")
    card.grid_columnconfigure(0, weight=1)

    app._lbl(card, "Configurações", size=15, weight="bold").grid(
        row=0, column=0, sticky="w", padx=24, pady=(24, 4))
    app._lbl(card, "Parâmetros usados nos cálculos do dashboard e relatórios.",
              size=12, color=C["muted"]).grid(row=1, column=0, sticky="w", padx=24, pady=(0, 18))
    app._sep(card, 2)

    settings = app._s.load_settings()

    def _field(label: str, row: int, placeholder: str, value: str) -> ctk.CTkEntry:
        app._lbl(card, label, size=12, weight="bold").grid(
            row=row, column=0, sticky="w", padx=24, pady=(16, 4))
        e = ctk.CTkEntry(card, height=40, corner_radius=6,
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text=placeholder)
        e.insert(0, value)
        e.grid(row=row + 1, column=0, sticky="ew", padx=24)
        return e

    cdi_e = _field("Taxa CDI (% a.a.)",                    3, "Ex: 10.75", str(settings.cdi_rate))
    iof_e = _field("IOF padrão para compra de dólar (%)",  5, "Ex: 1.1",   str(settings.default_iof_pct))

    app._sep(card, 7)
    smsg = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12), text_color=C["red"])
    smsg.grid(row=8, column=0, padx=24, pady=(12, 0))

    def _save() -> None:
        smsg.configure(text="")
        try:
            s = Settings(
                cdi_rate=float(cdi_e.get().strip().replace(",", ".")),
                default_iof_pct=float(iof_e.get().strip().replace(",", ".")),
            )
            app._s.save_settings(s)
            smsg.configure(text="Configurações salvas.", text_color=C["green"])
        except ValueError:
            smsg.configure(text="Valores inválidos.", text_color=C["red"])

    ctk.CTkButton(
        card, text="Salvar Configurações", height=42, corner_radius=6,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=C["text"], hover_color="#374151", text_color="#ffffff",
        command=_save,
    ).grid(row=9, column=0, sticky="ew", padx=24, pady=(12, 0))

    # ── PIN de acesso ──────────────────────────────────────────────────────────
    current_hash = app._s.load_pin_hash()
    app._sep(card, 10)
    app._lbl(card, "PIN de Acesso", size=12, weight="bold").grid(
        row=11, column=0, sticky="w", padx=24, pady=(16, 4))
    subtitle = "Altere o PIN atual." if current_hash else "Proteja o aplicativo com um PIN de 4 ou mais dígitos."
    app._lbl(card, subtitle, size=11, color=C["muted"]).grid(
        row=12, column=0, sticky="w", padx=24, pady=(0, 6))

    if current_hash:
        old_pin_e = ctk.CTkEntry(card, height=40, corner_radius=6, show="*",
                                  border_color=C["border"], fg_color=C["card"],
                                  text_color=C["text"], placeholder_text="PIN atual")
        old_pin_e.grid(row=13, column=0, sticky="ew", padx=24, pady=(0, 6))

    pin_e = ctk.CTkEntry(card, height=40, corner_radius=6, show="*",
                          border_color=C["border"], fg_color=C["card"],
                          text_color=C["text"], placeholder_text="Novo PIN")
    pin_e.grid(row=14, column=0, sticky="ew", padx=24)
    pmsg = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=12), text_color=C["red"])
    pmsg.grid(row=15, column=0, padx=24, pady=(8, 0))

    def _set_pin() -> None:
        new_raw = pin_e.get().strip()
        if current_hash:
            old_raw = old_pin_e.get().strip()
            if hashlib.sha256(old_raw.encode()).hexdigest() != current_hash:
                pmsg.configure(text="PIN atual incorreto.", text_color=C["red"])
                return
        if len(new_raw) < 4:
            pmsg.configure(text="Novo PIN deve ter ao menos 4 dígitos.", text_color=C["red"])
            return
        app._s.save_pin_hash(hashlib.sha256(new_raw.encode()).hexdigest())
        pmsg.configure(text="PIN definido. Bloqueando…", text_color=C["green"])
        if current_hash:
            old_pin_e.delete(0, "end")
        pin_e.delete(0, "end")
        app.after(800, app._lock)

    ctk.CTkButton(
        card, text="Definir PIN", height=42, corner_radius=6,
        font=ctk.CTkFont(size=13, weight="bold"),
        fg_color=C["blue"], hover_color="#2563eb", text_color="#ffffff",
        command=_set_pin,
    ).grid(row=16, column=0, sticky="ew", padx=24, pady=(8, 24))
